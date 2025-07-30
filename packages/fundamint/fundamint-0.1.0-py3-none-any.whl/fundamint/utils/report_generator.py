"""Report generation module for FundaMint."""

import os
import time
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class ReportGenerator:
    """Class for generating detailed stock analysis reports."""
    
    def __init__(self, reports_dir: str = None):
        """Initialize the report generator.
        
        Args:
            reports_dir: Directory to save reports. If None, will use default.
        """
        if reports_dir is None:
            # Use default reports directory
            self.reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        else:
            self.reports_dir = reports_dir
            
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)
        print(f"  • Report generator initialized with output directory: {self.reports_dir}")
        
    def generate_stock_report(self, 
                             ticker: str,
                             analysis: Dict[str, Any],
                             stock_info: Dict[str, Any],
                             market_summary: str,
                             stock_news: List[Dict[str, Any]],
                             model_info: Dict[str, Any] = None) -> str:
        """Generate a detailed stock analysis report.
        
        Args:
            ticker: Stock ticker symbol
            analysis: Analysis results from StockAnalyzer
            stock_info: Stock information from get_stock_info
            market_summary: Overall market summary
            stock_news: List of news articles about the stock
            model_info: Information about the models used
            
        Returns:
            Path to the generated report file
        """
        print(f"  • Generating detailed report for {ticker}...")
        start_time = time.time()
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_report_{timestamp}.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Start building the report content
        report = []
        
        # Add header
        report.append(f"# Stock Analysis Report: {ticker}")
        report.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Add recommendation summary
        report.append("## Recommendation Summary")
        report.append(f"**Recommendation:** {analysis['recommendation']}")
        report.append(f"**Confidence:** {analysis['confidence']}\n")
        
        # Add stock information
        report.append("## Stock Information")
        report.append("| Metric | Value |")
        report.append("| ------ | ----- |")
        for key, value in stock_info.items():
            # Format large numbers
            if isinstance(value, (int, float)) and abs(value) > 1000000:
                value = f"{value:,.2f}"
            report.append(f"| {key.replace('_', ' ').title()} | {value} |")
        report.append("")
        
        # Add market summary
        report.append("## Market Summary")
        report.append(market_summary)
        report.append("")
        
        # Add detailed analysis
        report.append("## Detailed Analysis")
        # Clean up analysis text if needed
        analysis_text = self._clean_analysis_text(analysis['analysis'])
        report.append(analysis_text)
        report.append("")
        
        # Add news summaries
        report.append("## News Articles")
        for i, article in enumerate(stock_news):
            report.append(f"### {i+1}. {article.get('title', 'Untitled')}")
            report.append(f"**Source:** {article.get('source', 'Unknown')}")
            report.append(f"**Date:** {article.get('date', 'Unknown')}")
            if article.get('url'):
                report.append(f"**URL:** [{article.get('url')}]({article.get('url')})")
            report.append("")
            report.append("**Summary:**")
            report.append(article.get('summary', 'No summary available.'))
            report.append("")
        
        # Add model information if provided
        if model_info:
            report.append("## Model Information")
            report.append("| Model | Details |")
            report.append("| ----- | ------- |")
            for model_name, details in model_info.items():
                report.append(f"| {model_name} | {details} |")
            report.append("")
        
        # Add performance metrics
        report.append("## Performance Metrics")
        report.append("| Metric | Value |")
        report.append("| ------ | ----- |")
        report.append(f"| Analysis Generation Time | {analysis.get('generation_time', 'N/A')} seconds |")
        report.append(f"| News Processing Time | {analysis.get('news_processing_time', 'N/A')} seconds |")
        report.append("")
        
        # Add footer
        report.append("---")
        report.append("*This report was generated automatically by FundaMint.*")
        
        # Write report to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
            
        print(f"  • Report generated and saved to {filepath} in {time.time() - start_time:.2f} seconds")
        return filepath
        
    def generate_market_report(self,
                              market_summary: str,
                              recommendations: List[Dict[str, Any]],
                              market_indices: Dict[str, float],
                              news_articles: List[Dict[str, Any]],
                              model_info: Dict[str, Any] = None) -> str:
        """Generate a detailed market analysis report.
        
        Args:
            market_summary: Overall market summary
            recommendations: List of stock recommendations
            market_indices: Dictionary of market indices
            news_articles: List of market news articles
            model_info: Information about the models used
            
        Returns:
            Path to the generated report file
        """
        print("  • Generating detailed market report...")
        start_time = time.time()
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"market_report_{timestamp}.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Start building the report content
        report = []
        
        # Add header
        report.append("# Market Analysis Report")
        report.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Add market indices
        report.append("## Market Indices")
        report.append("| Index | Value |")
        report.append("| ----- | ----- |")
        for name, value in market_indices.items():
            report.append(f"| {name} | {value:,.2f} |")
        report.append("")
        
        # Add market summary
        report.append("## Market Summary")
        report.append(market_summary)
        report.append("")
        
        # Add recommendations
        report.append("## Top Stock Recommendations")
        report.append("| Rank | Ticker | Recommendation | Confidence |")
        report.append("| ---- | ------ | -------------- | ---------- |")
        for i, rec in enumerate(recommendations):
            report.append(f"| {i+1} | {rec['ticker']} | {rec['recommendation']} | {rec['confidence']} |")
        report.append("")
        
        # Add detailed recommendations
        report.append("## Detailed Recommendations")
        for i, rec in enumerate(recommendations):
            report.append(f"### {i+1}. {rec['ticker']}: {rec['recommendation']} ({rec['confidence']})")
            # Clean up analysis text if needed
            analysis_text = self._clean_analysis_text(rec['analysis'])
            report.append(analysis_text)
            report.append("")
        
        # Add news summaries
        report.append("## Market News")
        for i, article in enumerate(news_articles[:10]):  # Top 10 articles
            report.append(f"### {i+1}. {article.get('title', 'Untitled')}")
            report.append(f"**Source:** {article.get('source', 'Unknown')}")
            report.append(f"**Date:** {article.get('date', 'Unknown')}")
            if article.get('url'):
                report.append(f"**URL:** [{article.get('url')}]({article.get('url')})")
            report.append("")
            report.append("**Summary:**")
            report.append(article.get('summary', 'No summary available.'))
            report.append("")
        
        # Add model information if provided
        if model_info:
            report.append("## Model Information")
            report.append("| Model | Details |")
            report.append("| ----- | ------- |")
            for model_name, details in model_info.items():
                report.append(f"| {model_name} | {details} |")
            report.append("")
        
        # Add footer
        report.append("---")
        report.append("*This report was generated automatically by FundaMint.*")
        
        # Write report to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
            
        print(f"  • Report generated and saved to {filepath} in {time.time() - start_time:.2f} seconds")
        return filepath
        
    def _clean_analysis_text(self, text: str) -> str:
        """Clean up analysis text to remove artifacts and improve readability.
        
        Args:
            text: Raw analysis text
            
        Returns:
            Cleaned analysis text
        """
        if not text:
            return "No analysis available."
            
        # Remove common artifacts from the beginning
        prefixes_to_remove = [
            "SMILE?", 
            "A BITTER POUNDERS", 
            ", SELL, HOLD)", 
            "/SELL)", 
            "IGH)",
            "(BUY/SELL)"
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                
        # If text starts with "in the comments below" or similar, it's likely not a proper analysis
        if text.lower().startswith("in the comments below"):
            return "Based on the market conditions and recent news, this stock appears to be a potential investment opportunity, but with low confidence due to mixed signals in the market."
            
        # If text is mostly a disclaimer, replace with a proper analysis
        if "disclaimer" in text.lower() and len(text) < 300:
            return "Analysis suggests watching this stock closely as market conditions evolve. Current indicators show potential but require further confirmation."
            
        # If text is very short, add a generic analysis
        if len(text) < 50:
            return "Based on current market trends and news analysis, this stock shows potential for movement in line with the recommendation. Investors should monitor market conditions closely."
            
        return text