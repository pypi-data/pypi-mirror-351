"""Module for training and fine-tuning LLMs for stock analysis."""

import os
import json
from typing import List, Dict, Any, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    Trainer, 
    TrainingArguments,
    DataCollatorForSeq2Seq,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

class ModelTrainer:
    """Class for training and fine-tuning LLMs."""
    
    def __init__(self, model_type: str = "summarizer", 
                 base_model: str = None,
                 output_dir: str = "./trained_model"):
        """Initialize the model trainer.
        
        Args:
            model_type: Type of model to train ('summarizer' or 'analyzer')
            base_model: Base model to fine-tune
            output_dir: Directory to save the trained model
        """
        self.model_type = model_type
        self.output_dir = output_dir
        
        # Set default base model based on model type
        if base_model is None:
            if model_type == "summarizer":
                self.base_model = "facebook/bart-large-cnn"
            else:  # analyzer
                self.base_model = "gpt2-large"
        else:
            self.base_model = base_model
            
        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        
        if model_type == "summarizer":
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.base_model)
        else:  # analyzer
            self.model = AutoModelForCausalLM.from_pretrained(self.base_model)
            
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
    def prepare_summarizer_dataset(self, 
                                  articles: List[Dict[str, Any]], 
                                  summaries: List[str]) -> Dataset:
        """Prepare dataset for training a summarizer model.
        
        Args:
            articles: List of news articles
            summaries: List of corresponding summaries
            
        Returns:
            HuggingFace Dataset
        """
        if len(articles) != len(summaries):
            raise ValueError("Number of articles must match number of summaries")
            
        # Extract article content
        contents = []
        for article in articles:
            content = article.get('content', article.get('description', ''))
            contents.append(content)
            
        # Create dataset
        dataset_dict = {
            "text": contents,
            "summary": summaries
        }
        
        return Dataset.from_dict(dataset_dict)
        
    def prepare_analyzer_dataset(self, 
                               market_summaries: List[str],
                               stock_news: List[List[Dict[str, Any]]],
                               tickers: List[str],
                               recommendations: List[str]) -> Dataset:
        """Prepare dataset for training a stock analyzer model.
        
        Args:
            market_summaries: List of market summaries
            stock_news: List of lists of news articles for each stock
            tickers: List of stock tickers
            recommendations: List of corresponding recommendations
            
        Returns:
            HuggingFace Dataset
        """
        if len(market_summaries) != len(stock_news) or len(stock_news) != len(recommendations):
            raise ValueError("Number of market summaries, stock news lists, and recommendations must match")
            
        # Create prompts and completions
        prompts = []
        completions = []
        
        for i in range(len(market_summaries)):
            # Create context
            context = f"Market Summary: {market_summaries[i]}\n\n"
            context += f"News about {tickers[i]}:\n"
            
            # Add summaries of stock-specific news
            for j, article in enumerate(stock_news[i][:5]):  # Use top 5 articles
                summary = article.get('summary', article.get('content', ''))
                if summary:
                    context += f"{j+1}. {summary}\n"
                    
            # Create prompt
            prompt = (
                f"{context}\n\n"
                f"Based on the above information, should investors BUY or SELL {tickers[i]} stock? "
                f"Provide a recommendation (BUY/SELL) and confidence level (LOW/MEDIUM/HIGH)."
            )
            
            prompts.append(prompt)
            completions.append(recommendations[i])
            
        # Create dataset
        dataset_dict = {
            "prompt": prompts,
            "completion": completions
        }
        
        return Dataset.from_dict(dataset_dict)
        
    def train_summarizer(self, 
                        dataset: Dataset,
                        epochs: int = 3,
                        batch_size: int = 4,
                        learning_rate: float = 5e-5) -> None:
        """Train a summarizer model.
        
        Args:
            dataset: Training dataset
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for training
        """
        # Tokenize dataset
        def preprocess_function(examples):
            inputs = self.tokenizer(examples["text"], truncation=True, padding="max_length", max_length=1024)
            labels = self.tokenizer(examples["summary"], truncation=True, padding="max_length", max_length=128)
            
            batch = {
                "input_ids": inputs.input_ids,
                "attention_mask": inputs.attention_mask,
                "labels": labels.input_ids,
            }
            
            # Replace padding token id with -100 so it's ignored in loss
            batch["labels"] = [
                [-100 if token == self.tokenizer.pad_token_id else token for token in labels]
                for labels in batch["labels"]
            ]
            
            return batch
            
        tokenized_dataset = dataset.map(preprocess_function, batched=True)
        
        # Set up training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=os.path.join(self.output_dir, "logs"),
            logging_steps=100,
            save_strategy="epoch",
        )
        
        # Create data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model,
            padding=True
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Train model
        trainer.train()
        
        # Save model and tokenizer
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        
    def train_analyzer(self, 
                      dataset: Dataset,
                      epochs: int = 3,
                      batch_size: int = 4,
                      learning_rate: float = 5e-5) -> None:
        """Train a stock analyzer model.
        
        Args:
            dataset: Training dataset
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for training
        """
        # Tokenize dataset
        def preprocess_function(examples):
            # Combine prompt and completion for causal language modeling
            texts = [prompt + completion for prompt, completion in zip(examples["prompt"], examples["completion"])]
            encodings = self.tokenizer(texts, truncation=True, padding="max_length", max_length=1024)
            
            return encodings
            
        tokenized_dataset = dataset.map(preprocess_function, batched=True)
        
        # Set up training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=os.path.join(self.output_dir, "logs"),
            logging_steps=100,
            save_strategy="epoch",
        )
        
        # Create data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Train model
        trainer.train()
        
        # Save model and tokenizer
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)