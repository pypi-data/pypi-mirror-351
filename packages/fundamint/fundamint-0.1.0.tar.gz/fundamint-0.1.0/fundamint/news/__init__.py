"""News collection and processing module."""

from typing import List, Dict
import os
from newsapi import NewsApiClient

class NewsCollector:
    def __init__(self, api_key: str = None):
        """Initialize NewsCollector with NewsAPI key."""
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.client = NewsApiClient(api_key=self.api_key)

    def get_stock_news(self, query: str, days: int = 1) -> List[Dict]:
        """Fetch stock-related news articles.
        
        Args:
            query: Search query for news articles
            days: Number of days to look back
            
        Returns:
            List of news articles
        """
        try:
            response = self.client.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=100
            )
            return response['articles']
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []