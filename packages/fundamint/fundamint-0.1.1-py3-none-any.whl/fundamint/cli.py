"""Command-line interface for FundaMint."""

import os
import argparse
import json
import time
from datetime import datetime
from typing import List, Dict, Any

from fundamint.news.collector import NewsCollector
from fundamint.news.processor import NewsProcessor
from fundamint.models.summarizer import NewsSummarizer
from fundamint.models.analyzer import StockAnalyzer
from fundamint.utils.stock_data import get_stock_info, get_market_indices
from fundamint.utils.report_generator import ReportGenerator

def main():
    """Main entry point for the CLI."""
    print("="*80)
    print("FUNDAMINT - Stock recommendations based on news analysis")
    print("="*80)
    
    parser = argparse.ArgumentParser(description="FundaMint - Stock recommendations based on news analysis")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Recommendations command
    recommend_parser = subparsers.add_parser("recommend", help="Get stock recommendations")
    recommend_parser.add_argument("--limit", type=int, default=5, help="Number of recommendations to show")
    recommend_parser.add_argument("--days", type=int, default=1, help="Number of days to look back for news")
    recommend_parser.add_argument("--report", action="store_true", help="Generate a detailed report")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a specific stock")
    analyze_parser.add_argument("ticker", help="Stock ticker symbol")
    analyze_parser.add_argument("--action", choices=["buy", "sell"], help="Intended action (buy or sell)")
    analyze_parser.add_argument("--report", action="store_true", help="Generate a detailed report")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the API server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    server_parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    
    # Training command
    train_parser = subparsers.add_parser("train", help="Train models")
    train_parser.add_argument("--model", choices=["summarizer", "analyzer"], required=True, help="Model to train")
    train_parser.add_argument("--data", required=True, help="Path to training data")
    train_parser.add_argument("--output", default="./trained_model", help="Output directory for trained model")
    train_parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get API key from environment
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        print("\n⚠️  WARNING: NEWS_API_KEY environment variable not set")
        print("Please set your NewsAPI key using: export NEWS_API_KEY=your_api_key")
        return
    
    # Handle commands
    if args.command == "recommend":
        get_recommendations(news_api_key, args.limit, args.days, args.report)
    elif args.command == "analyze":
        analyze_stock(news_api_key, args.ticker, args.action, args.report)
    elif args.command == "server":
        from fundamint.api.server import start_server
        print("\n[1/1] Starting API server...")
        print(f"  • Host: {args.host}")
        print(f"  • Port: {args.port}")
        start_server(host=args.host, port=args.port, news_api_key=news_api_key)
    elif args.command == "train":
        train_model(args.model, args.data, args.output, args.epochs)
    else:
        parser.print_help()

def get_recommendations(api_key: str, limit: int = 5, days: int = 1, generate_report: bool = False):
    """Get and display stock recommendations.
    
    Args:
        api_key: NewsAPI key
        limit: Number of recommendations to show
        days: Number of days to look back for news
        generate_report: Whether to generate a detailed report
    """
    print("\n[1/5] Initializing components...")
    start_time = time.time()
    
    # Initialize components
    news_collector = NewsCollector(api_key=api_key)
    news_processor = NewsProcessor()
    summarizer = NewsSummarizer()
    analyzer = StockAnalyzer()
    
    if generate_report:
        report_generator = ReportGenerator()
    
    summarizer_time = time.time() - start_time
    print(f"✓ Components initialized in {summarizer_time:.2f} seconds")
    
    # Get market news
    print("\n[2/5] Getting market news...")
    start_time = time.time()
    market_news = news_collector.get_market_news(days=days)
    filtered_market_news = news_processor.filter_relevant_articles(market_news)
    processed_market_news = news_processor.extract_key_information(filtered_market_news)
    market_news_time = time.time() - start_time
    print(f"✓ Market news collected in {market_news_time:.2f} seconds")
    
    # Summarize market news
    print("\n[3/5] Summarizing market news...")
    start_time = time.time()
    summarized_market_news = summarizer.summarize_articles(processed_market_news)
    market_summary = summarizer.create_market_summary(summarized_market_news)
    summarization_time = time.time() - start_time
    print(f"✓ Market news summarized in {summarization_time:.2f} seconds")
    
    print("\nMARKET SUMMARY:")
    print("-"*80)
    print(market_summary)
    print("-"*80)
    
    # Get market indices
    print("\nGetting market indices...")
    indices_start_time = time.time()
    market_indices = get_market_indices()
    indices_time = time.time() - indices_start_time
    print("MARKET INDICES:")
    print("-"*80)
    for name, value in market_indices.items():
        print(f"{name}: {value}")
    print("-"*80)
    
    # Get news for popular stocks
    popular_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"]
    news_by_ticker = {}
    stock_info_by_ticker = {}
    
    print(f"\n[4/5] Collecting and processing news for {len(popular_tickers)} stocks...")
    stocks_start_time = time.time()
    for i, ticker in enumerate(popular_tickers):
        print(f"  • Processing stock {i+1}/{len(popular_tickers)}: {ticker}")
        
        # Get stock info
        stock_info_by_ticker[ticker] = get_stock_info(ticker)
        
        # Get and process news
        stock_news = news_collector.get_stock_news(ticker, days=days)
        filtered_stock_news = news_processor.filter_relevant_articles(stock_news)
        processed_stock_news = news_processor.extract_key_information(filtered_stock_news)
        summarized_stock_news = summarizer.summarize_articles(processed_stock_news)
        news_by_ticker[ticker] = summarized_stock_news
    
    stocks_time = time.time() - stocks_start_time
    print(f"✓ Stock news processed in {stocks_time:.2f} seconds")
    
    # Get recommendations
    print("\n[5/5] Generating stock recommendations...")
    recommendations_start_time = time.time()
    recommendations = analyzer.get_top_recommendations(
        popular_tickers, market_summary, news_by_ticker
    )
    recommendations_time = time.time() - recommendations_start_time
    print(f"✓ Recommendations generated in {recommendations_time:.2f} seconds")
    
    # Display recommendations
    print("\nTOP RECOMMENDATIONS:")
    print("="*80)
    for i, rec in enumerate(recommendations[:limit]):
        print(f"{i+1}. {rec['ticker']}: {rec['recommendation']} (Confidence: {rec['confidence']})")
        print(f"   {rec['analysis'][:200]}...")
        print("-"*80)
    
    # Generate report if requested
    if generate_report:
        print("\n[+] Generating detailed market report...")
        
        # Add timing information to recommendations
        for rec in recommendations:
            rec['generation_time'] = recommendations_time / len(popular_tickers)
            rec['news_processing_time'] = stocks_time / len(popular_tickers)
        
        # Model information for reports
        model_info = {
            "Summarizer": f"{summarizer.model_name}",
            "Analyzer": f"{analyzer.model_name}"
        }
        
        # Generate market report
        market_report_path = report_generator.generate_market_report(
            market_summary=market_summary,
            recommendations=recommendations,
            market_indices=market_indices,
            news_articles=summarized_market_news,
            model_info=model_info
        )
        
        print(f"\n✅ Market report saved to: {market_report_path}")

def analyze_stock(api_key: str, ticker: str, action: str = None, generate_report: bool = False):
    """Analyze a specific stock.
    
    Args:
        api_key: NewsAPI key
        ticker: Stock ticker symbol
        action: Intended action (buy or sell)
        generate_report: Whether to generate a detailed report
    """
    ticker = ticker.upper()
    print(f"\n[1/5] Analyzing {ticker}...")
    
    # Initialize components
    print("\n[2/5] Initializing components...")
    start_time = time.time()
    news_collector = NewsCollector(api_key=api_key)
    news_processor = NewsProcessor()
    summarizer = NewsSummarizer()
    analyzer = StockAnalyzer()
    
    if generate_report:
        report_generator = ReportGenerator()
        
    init_time = time.time() - start_time
    print(f"✓ Components initialized in {init_time:.2f} seconds")
    
    # Get stock info
    print(f"\n[3/5] Getting information for {ticker}...")
    stock_info_start = time.time()
    stock_info = get_stock_info(ticker)
    stock_info_time = time.time() - stock_info_start
    print(f"✓ Stock information retrieved in {stock_info_time:.2f} seconds")
    
    print("\nSTOCK INFORMATION:")
    print("-"*80)
    for key, value in stock_info.items():
        print(f"{key}: {value}")
    print("-"*80)
    
    # Get market news
    print("\n[4/5] Getting and processing market news...")
    market_start_time = time.time()
    market_news = news_collector.get_market_news(days=1)
    filtered_market_news = news_processor.filter_relevant_articles(market_news)
    processed_market_news = news_processor.extract_key_information(filtered_market_news)
    summarized_market_news = summarizer.summarize_articles(processed_market_news)
    market_summary = summarizer.create_market_summary(summarized_market_news)
    
    # Get market indices
    market_indices = get_market_indices()
    
    # Get stock-specific news
    print(f"\nGetting and processing news for {ticker}...")
    stock_news = news_collector.get_stock_news(ticker, days=1)
    filtered_stock_news = news_processor.filter_relevant_articles(stock_news)
    processed_stock_news = news_processor.extract_key_information(filtered_stock_news)
    summarized_stock_news = summarizer.summarize_articles(processed_stock_news)
    news_time = time.time() - market_start_time
    print(f"✓ News processing completed in {news_time:.2f} seconds")
    
    # Print news summaries
    print("\nRECENT NEWS:")
    print("-"*80)
    for i, article in enumerate(summarized_stock_news[:3]):
        print(f"{i+1}. {article['title']} ({article['source']})")
        print(f"   {article['summary'][:200]}...")
        print()
    
    # Analyze stock
    print(f"\n[5/5] Generating analysis for {ticker}...")
    analysis_start_time = time.time()
    analysis_result = analyzer.analyze_stock(ticker, market_summary, summarized_stock_news)
    analysis_time = time.time() - analysis_start_time
    print(f"✓ Analysis completed in {analysis_time:.2f} seconds")
    
    # Add timing information to analysis
    analysis_result['generation_time'] = analysis_time
    analysis_result['news_processing_time'] = news_time
    
    print("\nANALYSIS:")
    print("="*80)
    print(f"Recommendation: {analysis_result['recommendation']}")
    print(f"Confidence: {analysis_result['confidence']}")
    print(f"\n{analysis_result['analysis']}")
    
    # If action is provided, calculate win probability
    if action:
        action = action.upper()
        confidence_values = {"HIGH": 0.8, "MEDIUM": 0.6, "LOW": 0.4}
        confidence = confidence_values.get(analysis_result['confidence'], 0.5)
        
        # If recommendation matches requested action, higher probability
        if analysis_result['recommendation'] == action:
            win_probability = confidence
        else:
            win_probability = 1.0 - confidence
            
        print(f"\nWin probability for {action}: {win_probability:.2f} ({win_probability*100:.1f}%)")
    
    print("="*80)
    
    # Generate report if requested
    if generate_report:
        print("\n[+] Generating detailed stock report...")
        
        # Model information for reports
        model_info = {
            "Summarizer": f"{summarizer.model_name}",
            "Analyzer": f"{analyzer.model_name}"
        }
        
        # Generate stock report
        stock_report_path = report_generator.generate_stock_report(
            ticker=ticker,
            analysis=analysis_result,
            stock_info=stock_info,
            market_summary=market_summary,
            stock_news=summarized_stock_news,
            model_info=model_info
        )
        
        print(f"\n✅ Stock report saved to: {stock_report_path}")

def train_model(model_type: str, data_path: str, output_dir: str, epochs: int):
    """Train a model.
    
    Args:
        model_type: Type of model to train ('summarizer' or 'analyzer')
        data_path: Path to training data
        output_dir: Output directory for trained model
        epochs: Number of training epochs
    """
    from fundamint.models.trainer import ModelTrainer
    
    print(f"\n[1/4] Training {model_type} model...")
    print(f"  • Model type: {model_type}")
    print(f"  • Training data: {data_path}")
    print(f"  • Output directory: {output_dir}")
    print(f"  • Epochs: {epochs}")
    
    # Load training data
    print("\n[2/4] Loading training data...")
    start_time = time.time()
    try:
        with open(data_path, 'r') as f:
            training_data = json.load(f)
        print(f"✓ Training data loaded in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Error loading training data: {e}")
        return
    
    # Initialize trainer
    print("\n[3/4] Initializing model trainer...")
    start_time = time.time()
    trainer = ModelTrainer(model_type=model_type, output_dir=output_dir)
    print(f"✓ Trainer initialized in {time.time() - start_time:.2f} seconds")
    
    # Prepare dataset and train model
    print("\n[4/4] Training model...")
    start_time = time.time()
    
    if model_type == "summarizer":
        if "articles" not in training_data or "summaries" not in training_data:
            print("❌ Training data must contain 'articles' and 'summaries' keys")
            return
            
        print(f"  • Preparing dataset with {len(training_data['articles'])} examples...")
        dataset = trainer.prepare_summarizer_dataset(
            training_data["articles"], 
            training_data["summaries"]
        )
        print("  • Starting training...")
        trainer.train_summarizer(dataset, epochs=epochs)
    else:  # analyzer
        if ("market_summaries" not in training_data or 
            "stock_news" not in training_data or
            "tickers" not in training_data or
            "recommendations" not in training_data):
            print("❌ Training data must contain 'market_summaries', 'stock_news', 'tickers', and 'recommendations' keys")
            return
            
        print(f"  • Preparing dataset with {len(training_data['tickers'])} examples...")
        dataset = trainer.prepare_analyzer_dataset(
            training_data["market_summaries"],
            training_data["stock_news"],
            training_data["tickers"],
            training_data["recommendations"]
        )
        print("  • Starting training...")
        trainer.train_analyzer(dataset, epochs=epochs)
    
    print(f"✓ Model trained in {time.time() - start_time:.2f} seconds")
    print(f"\n✅ Model trained and saved to {output_dir}")
    print("="*80)

if __name__ == "__main__":
    main()