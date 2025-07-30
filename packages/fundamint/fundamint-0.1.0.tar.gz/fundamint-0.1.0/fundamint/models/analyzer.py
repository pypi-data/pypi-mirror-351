"""Stock analysis module using LLMs."""

from typing import List, Dict, Any, Tuple
import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class StockAnalyzer:
    """Class for analyzing stocks based on news summaries using LLMs."""
    
    def __init__(self, model_name: str = "gpt2-large", 
                 device: str = "cpu",
                 custom_model_path: str = None):
        """Initialize the stock analyzer.
        
        Args:
            model_name: Name of the pre-trained model to use
            device: Device to run the model on ('cpu' or 'cuda')
            custom_model_path: Path to a custom fine-tuned model
        """
        print("  • Initializing StockAnalyzer...")
        self.model_name = model_name
        self.device = device
        self.custom_model_path = custom_model_path
        
        # Load model and tokenizer
        print(f"  • Loading tokenizer and model...")
        start_time = time.time()
        if custom_model_path and os.path.exists(custom_model_path):
            print(f"  • Using custom model from {custom_model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(custom_model_path)
            self.model = AutoModelForCausalLM.from_pretrained(custom_model_path)
        else:
            print(f"  • Using pre-trained model {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
        print(f"  • Model loaded in {time.time() - start_time:.2f} seconds")
            
        # Create text generation pipeline
        print(f"  • Creating text generation pipeline on {device}...")
        self.generator = pipeline(
            "text-generation", 
            model=self.model, 
            tokenizer=self.tokenizer,
            device=0 if device == "cuda" else -1
        )
        print("  • StockAnalyzer initialized successfully")
        
    def analyze_stock(self, ticker: str, market_summary: str, 
                     stock_news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a stock based on news and market summary.
        
        Args:
            ticker: Stock ticker symbol
            market_summary: Overall market summary
            stock_news: List of news articles about the stock
            
        Returns:
            Analysis results including recommendation and confidence
        """
        print(f"  • Analyzing {ticker} based on market summary and {len(stock_news)} news articles...")
        start_time = time.time()
        
        # Prepare context for the model
        context = f"Market Summary: {market_summary}\n\n"
        context += f"News about {ticker}:\n"
        
        # Add summaries of stock-specific news
        article_count = min(5, len(stock_news))
        print(f"  • Using top {article_count} articles for analysis")
        
        for i, article in enumerate(stock_news[:article_count]):
            summary = article.get('summary', article.get('content', ''))
            if summary:
                # Limit summary length to avoid tokenizer issues
                if len(summary) > 500:
                    summary = summary[:500] + "..."
                context += f"{i+1}. {summary}\n"
                
        # Create prompt for the model
        prompt = (
            f"{context}\n\n"
            f"Based on the above information, provide a concise analysis of {ticker} stock. "
            f"End with a clear recommendation (BUY, SELL, or HOLD) and confidence level (LOW, MEDIUM, or HIGH)."
        )
        
        # Ensure prompt isn't too long
        if len(prompt.split()) > 800:
            print("  • WARNING: Prompt too long, truncating...")
            prompt_parts = prompt.split('\n\n')
            # Keep the first part (market summary) and the last part (question)
            prompt = prompt_parts[0] + '\n\n' + prompt_parts[-1]
        
        print("  • Generating analysis...")
        # Generate analysis
        try:
            # Calculate appropriate max_new_tokens based on prompt length
            prompt_tokens = len(prompt.split())
            max_new_tokens = 150  # Reasonable default for a concise analysis
            
            response = self.generator(
                prompt, 
                max_new_tokens=max_new_tokens,
                num_return_sequences=1,
                temperature=0.7,
                truncation=True,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )[0]['generated_text']
            
            # Extract the generated part (after the prompt)
            analysis = response[len(prompt):].strip()
            
            # Clean up the analysis to remove any incomplete sentences at the end
            if analysis and len(analysis) > 0:
                # Find the last complete sentence
                sentence_endings = ['. ', '! ', '? ']
                last_end = -1
                for ending in sentence_endings:
                    pos = analysis.rfind(ending)
                    if pos > last_end:
                        last_end = pos
                
                if last_end > 0:
                    analysis = analysis[:last_end+1].strip()
            
            # If analysis is too short or doesn't contain a recommendation, generate a better one
            if len(analysis) < 100 or not any(word in analysis.upper() for word in ["BUY", "SELL", "HOLD"]):
                analysis = self._generate_fallback_analysis(ticker, market_summary, stock_news)
            
            # Parse recommendation and confidence
            recommendation, confidence = self._parse_recommendation(analysis)
            print(f"  • Analysis generated: {recommendation} with {confidence} confidence")
            
            result = {
                'ticker': ticker,
                'recommendation': recommendation,
                'confidence': confidence,
                'analysis': analysis,
                'context': context
            }
            
            print(f"  • Analysis completed in {time.time() - start_time:.2f} seconds")
            return result
        except Exception as e:
            print(f"  • ERROR analyzing stock {ticker}: {e}")
            return {
                'ticker': ticker,
                'recommendation': 'UNKNOWN',
                'confidence': 'LOW',
                'analysis': self._generate_fallback_analysis(ticker, market_summary, stock_news),
                'context': context
            }
    
    def _generate_fallback_analysis(self, ticker: str, market_summary: str, stock_news: List[Dict[str, Any]]) -> str:
        """Generate a fallback analysis when the model fails to produce a good one.
        
        Args:
            ticker: Stock ticker symbol
            market_summary: Overall market summary
            stock_news: List of news articles about the stock
            
        Returns:
            Fallback analysis text
        """
        # Extract some key information from news
        news_titles = [article.get('title', '') for article in stock_news[:3]]
        titles_text = '. '.join(news_titles)
        
        # Generate a simple analysis based on available information
        analysis = f"Based on recent market trends and news about {ticker}, there are several factors to consider. "
        analysis += f"The market summary indicates: {market_summary} "
        
        if titles_text:
            analysis += f"Recent headlines about {ticker} mention: {titles_text} "
        
        # Add a generic recommendation
        if "up" in market_summary.lower() or "rise" in market_summary.lower() or "gain" in market_summary.lower():
            analysis += f"Given the positive market sentiment, {ticker} appears to be positioned for potential growth. "
            analysis += f"Recommendation: BUY with LOW confidence."
        elif "down" in market_summary.lower() or "fall" in market_summary.lower() or "drop" in market_summary.lower():
            analysis += f"Given the negative market sentiment, {ticker} may face challenges in the near term. "
            analysis += f"Recommendation: SELL with LOW confidence."
        else:
            analysis += f"The market shows mixed signals, suggesting a cautious approach to {ticker}. "
            analysis += f"Recommendation: HOLD with LOW confidence."
            
        return analysis
            
    def _parse_recommendation(self, analysis: str) -> Tuple[str, str]:
        """Parse recommendation and confidence from analysis text.
        
        Args:
            analysis: Generated analysis text
            
        Returns:
            Tuple of (recommendation, confidence)
        """
        analysis_upper = analysis.upper()
        
        # Determine recommendation
        if "BUY" in analysis_upper:
            recommendation = "BUY"
        elif "SELL" in analysis_upper:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
            
        # Determine confidence
        if "HIGH CONFIDENCE" in analysis_upper or "CONFIDENCE: HIGH" in analysis_upper:
            confidence = "HIGH"
        elif "MEDIUM CONFIDENCE" in analysis_upper or "CONFIDENCE: MEDIUM" in analysis_upper:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
            
        return recommendation, confidence
        
    def get_top_recommendations(self, tickers: List[str], 
                               market_summary: str,
                               news_by_ticker: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Get top stock recommendations based on news analysis.
        
        Args:
            tickers: List of stock ticker symbols
            market_summary: Overall market summary
            news_by_ticker: Dictionary mapping tickers to their news articles
            
        Returns:
            List of stock recommendations sorted by confidence
        """
        print(f"  • Generating recommendations for {len(tickers)} stocks...")
        start_time = time.time()
        recommendations = []
        
        for i, ticker in enumerate(tickers):
            print(f"  • Analyzing stock {i+1}/{len(tickers)}: {ticker}")
            stock_news = news_by_ticker.get(ticker, [])
            analysis = self.analyze_stock(ticker, market_summary, stock_news)
            recommendations.append(analysis)
            
        # Sort by confidence and recommendation
        confidence_values = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        recommendations.sort(
            key=lambda x: (
                confidence_values.get(x['confidence'], 0),
                1 if x['recommendation'] == "BUY" else 0
            ),
            reverse=True
        )
        
        print(f"  • Completed recommendations in {time.time() - start_time:.2f} seconds")
        return recommendations