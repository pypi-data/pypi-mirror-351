"""News collection and processing module."""

from typing import List, Dict, Any
import os
from datetime import datetime, timedelta
from newsapi import NewsApiClient

class NewsCollector:
    """Class for collecting news from various sources."""
    
    def __init__(self, api_key: str = None):
        """Initialize NewsCollector with NewsAPI key.
        
        Args:
            api_key: API key for NewsAPI. If None, will try to get from environment.
        """
        print("  • Initializing NewsCollector...")
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError("NewsAPI key is required. Set it as an argument or as NEWS_API_KEY environment variable.")
        self.client = NewsApiClient(api_key=self.api_key)
        print("  • NewsAPI client initialized successfully")

    def get_stock_news(self, query: str, days: int = 1) -> List[Dict[str, Any]]:
        """Fetch stock-related news articles.
        
        Args:
            query: Search query for news articles (e.g., "AAPL" or "Tesla stock")
            days: Number of days to look back
            
        Returns:
            List of news articles
        """
        print(f"  • Fetching news for '{query}' from the past {days} day(s)...")
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        try:
            response = self.client.get_everything(
                q=f"{query} stock",
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=100
            )
            articles = response['articles']
            
            # Clean up articles to ensure no None values
            cleaned_articles = []
            for article in articles:
                # Ensure all key fields have at least empty string values
                article['title'] = article.get('title') or ''
                article['description'] = article.get('description') or ''
                article['content'] = article.get('content') or ''
                cleaned_articles.append(article)
                
            print(f"  • Successfully retrieved {len(cleaned_articles)} articles for '{query}'")
            return cleaned_articles
        except Exception as e:
            print(f"  • ERROR fetching news for '{query}': {e}")
            return []
            
    def get_market_news(self, days: int = 1) -> List[Dict[str, Any]]:
        """Fetch general market news.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of news articles
        """
        print(f"  • Fetching general market news from the past {days} day(s)...")
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        try:
            response = self.client.get_everything(
                q="stock market OR financial markets OR wall street",
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=100
            )
            articles = response['articles']
            
            # Clean up articles to ensure no None values
            cleaned_articles = []
            for article in articles:
                # Ensure all key fields have at least empty string values
                article['title'] = article.get('title') or ''
                article['description'] = article.get('description') or ''
                article['content'] = article.get('content') or ''
                cleaned_articles.append(article)
                
            print(f"  • Successfully retrieved {len(cleaned_articles)} market news articles")
            return cleaned_articles
        except Exception as e:
            print(f"  • ERROR fetching market news: {e}")
            return []