"""News summarization module using open-source LLMs."""

from typing import List, Dict, Any, Optional
import os
import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

class NewsSummarizer:
    """Class for summarizing news articles using LLMs."""
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn", 
                 device: str = "cpu",
                 custom_model_path: Optional[str] = None):
        """Initialize the news summarizer.
        
        Args:
            model_name: Name of the pre-trained model to use
            device: Device to run the model on ('cpu' or 'cuda')
            custom_model_path: Path to a custom fine-tuned model
        """
        print("  • Initializing NewsSummarizer...")
        self.model_name = model_name
        self.device = device
        self.custom_model_path = custom_model_path
        
        # Load model and tokenizer
        print(f"  • Loading tokenizer and model...")
        start_time = time.time()
        if custom_model_path and os.path.exists(custom_model_path):
            print(f"  • Using custom model from {custom_model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(custom_model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(custom_model_path)
        else:
            print(f"  • Using pre-trained model {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
        print(f"  • Model loaded in {time.time() - start_time:.2f} seconds")
            
        # Create summarization pipeline
        print(f"  • Creating summarization pipeline on {device}...")
        self.summarizer = pipeline(
            "summarization", 
            model=self.model, 
            tokenizer=self.tokenizer,
            device=0 if device == "cuda" else -1
        )
        print("  • NewsSummarizer initialized successfully")
        
    def summarize_article(self, article: Dict[str, Any], 
                         max_length: int = None, 
                         min_length: int = None) -> str:
        """Summarize a single news article.
        
        Args:
            article: News article dictionary
            max_length: Maximum length of the summary
            min_length: Minimum length of the summary
            
        Returns:
            Summarized text
        """
        title = article.get('title', 'Untitled')
        content = article.get('content', article.get('description', ''))
        if not content:
            print(f"  • WARNING: No content to summarize for article: {title[:30]}...")
            return ""
            
        # Truncate content if it's too long for the model
        # Fix: Use a safe max_tokens value (1024 is typically safe for most models)
        max_tokens = min(1024, self.tokenizer.model_max_length - 100)
        
        try:
            # Safely truncate the content to avoid overflow
            if len(content) > 5000:
                print(f"  • WARNING: Content too long ({len(content)} chars), truncating to 5000 chars")
                content = content[:5000]
                
            tokens = self.tokenizer(content, return_tensors="pt", truncation=True, max_length=max_tokens)
            truncated_content = self.tokenizer.decode(tokens["input_ids"][0], skip_special_tokens=True)
            
            # Dynamically set max_length and min_length based on input length
            input_length = len(truncated_content.split())
            if max_length is None:
                # Set max_length to half the input length, with a minimum of 30
                max_length = max(30, min(input_length // 2, 150))
            if min_length is None:
                # Set min_length to 1/4 the input length, with a minimum of 10
                min_length = max(10, min(input_length // 4, 50))
            
            # Generate summary
            summary = self.summarizer(
                truncated_content, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )[0]['summary_text']
            
            return summary
        except Exception as e:
            print(f"  • ERROR summarizing article '{title[:30]}...': {e}")
            print(f"  • Falling back to first 200 characters as summary")
            # Fallback to first 200 chars if summarization fails
            return content[:200] + "..."
            
    def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize a list of news articles.
        
        Args:
            articles: List of news article dictionaries
            
        Returns:
            List of articles with added summaries
        """
        print(f"  • Summarizing {len(articles)} articles...")
        start_time = time.time()
        summarized_articles = []
        
        for i, article in enumerate(articles):
            if i % 5 == 0 and i > 0:
                print(f"  • Summarized {i}/{len(articles)} articles...")
                
            summary = self.summarize_article(article)
            article_with_summary = article.copy()
            article_with_summary['summary'] = summary
            summarized_articles.append(article_with_summary)
            
        print(f"  • Completed summarizing {len(articles)} articles in {time.time() - start_time:.2f} seconds")
        return summarized_articles
        
    def create_market_summary(self, articles: List[Dict[str, Any]]) -> str:
        """Create an overall market summary from multiple articles.
        
        Args:
            articles: List of news article dictionaries
            
        Returns:
            Overall market summary
        """
        print("  • Creating overall market summary...")
        start_time = time.time()
        
        # Combine summaries from individual articles
        combined_text = ""
        article_count = min(10, len(articles))
        print(f"  • Using top {article_count} articles for market summary")
        
        for article in articles[:article_count]:
            summary = article.get('summary', '')
            if not summary:
                summary = self.summarize_article(article, max_length=100, min_length=20)
            if summary:
                combined_text += summary + " "
                
        # Limit combined text length to avoid tokenizer issues
        if len(combined_text) > 4000:
            print(f"  • Combined text too long ({len(combined_text)} chars), truncating to 4000 chars")
            combined_text = combined_text[:4000]
                
        # Summarize the combined text
        if combined_text:
            try:
                # Dynamically set max_length based on input length
                input_length = len(combined_text.split())
                max_length = min(200, max(50, input_length // 3))
                min_length = min(50, max(20, input_length // 10))
                
                market_summary = self.summarizer(
                    combined_text, 
                    max_length=max_length, 
                    min_length=min_length, 
                    do_sample=False
                )[0]['summary_text']
                print(f"  • Market summary created in {time.time() - start_time:.2f} seconds")
                return market_summary
            except Exception as e:
                print(f"  • ERROR creating market summary: {e}")
                print(f"  • Falling back to first 200 characters as summary")
                return combined_text[:200] + "..."
                
        print("  • WARNING: Unable to generate market summary")
        return "Unable to generate market summary."