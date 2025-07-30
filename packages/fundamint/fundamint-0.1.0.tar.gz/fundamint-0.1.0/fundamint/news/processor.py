"""News processing and filtering module."""

from typing import List, Dict, Any
import re
from datetime import datetime

class NewsProcessor:
    """Class for processing and filtering news articles."""
    
    def __init__(self):
        """Initialize NewsProcessor."""
        print("  • Initializing NewsProcessor...")
        print("  • NewsProcessor initialized successfully")
        
    def filter_relevant_articles(self, articles: List[Dict[str, Any]], 
                                keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Filter articles based on relevance to financial markets and stocks.
        
        Args:
            articles: List of news articles
            keywords: Additional keywords to filter by
            
        Returns:
            Filtered list of news articles
        """
        print(f"  • Filtering {len(articles)} articles for relevance...")
        if not keywords:
            keywords = ["stock", "market", "investor", "trading", "financial", 
                       "economy", "shares", "price", "earnings", "revenue"]
            print(f"  • Using default keywords: {', '.join(keywords)}")
        else:
            print(f"  • Using custom keywords: {', '.join(keywords)}")
                       
        filtered_articles = []
        for i, article in enumerate(articles):
            # Fix: Handle None values by using empty strings as defaults
            title = (article.get('title') or '').lower()
            description = (article.get('description') or '').lower()
            content = (article.get('content') or '').lower()
            
            # Check if any keyword is in the article
            if any(keyword.lower() in title or 
                   keyword.lower() in description or 
                   keyword.lower() in content 
                   for keyword in keywords):
                filtered_articles.append(article)
                
        print(f"  • Filtered down to {len(filtered_articles)} relevant articles")
        return filtered_articles
        
    def extract_key_information(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract key information from articles.
        
        Args:
            articles: List of news articles
            
        Returns:
            List of articles with extracted key information
        """
        print(f"  • Extracting key information from {len(articles)} articles...")
        processed_articles = []
        
        for i, article in enumerate(articles):
            # Extract date
            published_at = article.get('publishedAt')
            if published_at:
                try:
                    date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                    formatted_date = date.strftime("%Y-%m-%d")
                except ValueError:
                    formatted_date = published_at
            else:
                formatted_date = "Unknown"
                
            # Create processed article
            processed_article = {
                'title': article.get('title', 'Untitled'),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'date': formatted_date,
                'url': article.get('url', ''),
                'content': article.get('content') or article.get('description') or '',
            }
            
            processed_articles.append(processed_article)
            
        print(f"  • Successfully processed {len(processed_articles)} articles")
        return processed_articles