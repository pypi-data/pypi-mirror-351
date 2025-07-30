"""FastAPI server for FundaMint."""

from typing import List, Dict, Any, Optional
import time
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn
import yfinance as yf

from fundamint.news.collector import NewsCollector
from fundamint.news.processor import NewsProcessor
from fundamint.models.summarizer import NewsSummarizer
from fundamint.models.analyzer import StockAnalyzer

app = FastAPI(
    title="FundaMint API",
    description="API for stock recommendations based on news analysis",
    version="0.1.0",
)

# Models for request/response
class StockRecommendation(BaseModel):
    ticker: str
    recommendation: str
    confidence: str
    analysis: str

class StockAnalysisRequest(BaseModel):
    ticker: str
    action: str  # "BUY" or "SELL"

class StockAnalysisResponse(BaseModel):
    ticker: str
    action: str
    win_probability: float
    analysis: str

# Global instances
news_collector = None
news_processor = None
summarizer = None
analyzer = None

def initialize_components(news_api_key: str, 
                         summarizer_model: str = "facebook/bart-large-cnn",
                         analyzer_model: str = "gpt2-large",
                         device: str = "cpu"):
    """Initialize all components.
    
    Args:
        news_api_key: API key for NewsAPI
        summarizer_model: Model to use for summarization
        analyzer_model: Model to use for stock analysis
        device: Device to run models on ('cpu' or 'cuda')
    """
    global news_collector, news_processor, summarizer, analyzer
    
    print("Initializing API components...")
    start_time = time.time()
    
    print("  • Creating NewsCollector...")
    news_collector = NewsCollector(api_key=news_api_key)
    
    print("  • Creating NewsProcessor...")
    news_processor = NewsProcessor()
    
    print("  • Creating NewsSummarizer...")
    print("    (This may take a moment as models are downloaded if not cached)")
    summarizer_start = time.time()
    summarizer = NewsSummarizer(model_name=summarizer_model, device=device)
    print(f"    Summarizer initialized in {time.time() - summarizer_start:.2f} seconds")
    
    print("  • Creating StockAnalyzer...")
    print("    (This may take a moment as models are downloaded if not cached)")
    analyzer_start = time.time()
    analyzer = StockAnalyzer(model_name=analyzer_model, device=device)
    print(f"    Analyzer initialized in {time.time() - analyzer_start:.2f} seconds")
    
    print(f"✓ All components initialized in {time.time() - start_time:.2f} seconds")

@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to FundaMint API"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    components_initialized = all([
        news_collector is not None,
        news_processor is not None,
        summarizer is not None,
        analyzer is not None
    ])
    
    return {
        "status": "healthy" if components_initialized else "not_ready",
        "components_initialized": components_initialized
    }

@app.get("/recommendations", response_model=List[StockRecommendation])
def get_recommendations(limit: int = Query(5, ge=1, le=20)):
    """Get top stock recommendations.
    
    Args:
        limit: Maximum number of recommendations to return
        
    Returns:
        List of stock recommendations
    """
    print(f"GET /recommendations (limit={limit})")
    start_time = time.time()
    
    if not all([news_collector, news_processor, summarizer, analyzer]):
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    # Get market news
    print("  • Getting market news...")
    market_news = news_collector.get_market_news(days=1)
    filtered_market_news = news_processor.filter_relevant_articles(market_news)
    processed_market_news = news_processor.extract_key_information(filtered_market_news)
    
    # Summarize market news
    print("  • Summarizing market news...")
    summarized_market_news = summarizer.summarize_articles(processed_market_news)
    market_summary = summarizer.create_market_summary(summarized_market_news)
    
    # Get news for popular stocks
    popular_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"]
    news_by_ticker = {}
    
    print(f"  • Getting news for {len(popular_tickers)} stocks...")
    for ticker in popular_tickers:
        stock_news = news_collector.get_stock_news(ticker, days=1)
        filtered_stock_news = news_processor.filter_relevant_articles(stock_news)
        processed_stock_news = news_processor.extract_key_information(filtered_stock_news)
        summarized_stock_news = summarizer.summarize_articles(processed_stock_news)
        news_by_ticker[ticker] = summarized_stock_news
    
    # Get recommendations
    print("  • Generating recommendations...")
    recommendations = analyzer.get_top_recommendations(
        popular_tickers, market_summary, news_by_ticker
    )
    
    # Return limited number of recommendations
    result = recommendations[:limit]
    print(f"✓ Recommendations generated in {time.time() - start_time:.2f} seconds")
    return result

@app.post("/analyze", response_model=StockAnalysisResponse)
def analyze_stock(request: StockAnalysisRequest):
    """Analyze a specific stock for buy/sell action.
    
    Args:
        request: Stock analysis request
        
    Returns:
        Analysis response with win probability
    """
    print(f"POST /analyze (ticker={request.ticker}, action={request.action})")
    start_time = time.time()
    
    if not all([news_collector, news_processor, summarizer, analyzer]):
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    ticker = request.ticker.upper()
    action = request.action.upper()
    
    if action not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Action must be BUY or SELL")
    
    try:
        # Validate ticker
        print(f"  • Validating ticker {ticker}...")
        stock = yf.Ticker(ticker)
        info = stock.info
        if 'regularMarketPrice' not in info:
            raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching stock info: {str(e)}")
    
    # Get market news
    print("  • Getting market news...")
    market_news = news_collector.get_market_news(days=1)
    filtered_market_news = news_processor.filter_relevant_articles(market_news)
    processed_market_news = news_processor.extract_key_information(filtered_market_news)
    summarized_market_news = summarizer.summarize_articles(processed_market_news)
    market_summary = summarizer.create_market_summary(summarized_market_news)
    
    # Get stock-specific news
    print(f"  • Getting news for {ticker}...")
    stock_news = news_collector.get_stock_news(ticker, days=1)
    filtered_stock_news = news_processor.filter_relevant_articles(stock_news)
    processed_stock_news = news_processor.extract_key_information(filtered_stock_news)
    summarized_stock_news = summarizer.summarize_articles(processed_stock_news)
    
    # Analyze stock
    print(f"  • Analyzing {ticker}...")
    analysis_result = analyzer.analyze_stock(ticker, market_summary, summarized_stock_news)
    
    # Calculate win probability
    confidence_values = {"HIGH": 0.8, "MEDIUM": 0.6, "LOW": 0.4}
    confidence = confidence_values.get(analysis_result['confidence'], 0.5)
    
    # If recommendation matches requested action, higher probability
    if analysis_result['recommendation'] == action:
        win_probability = confidence
    else:
        win_probability = 1.0 - confidence
    
    result = {
        "ticker": ticker,
        "action": action,
        "win_probability": win_probability,
        "analysis": analysis_result['analysis']
    }
    
    print(f"✓ Analysis completed in {time.time() - start_time:.2f} seconds")
    return result

def start_server(host: str = "0.0.0.0", 
                port: int = 8000, 
                news_api_key: str = None,
                summarizer_model: str = "facebook/bart-large-cnn",
                analyzer_model: str = "gpt2-large",
                device: str = "cpu"):
    """Start the FastAPI server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        news_api_key: API key for NewsAPI
        summarizer_model: Model to use for summarization
        analyzer_model: Model to use for stock analysis
        device: Device to run models on ('cpu' or 'cuda')
    """
    print(f"Initializing FundaMint API server on {host}:{port}")
    initialize_components(
        news_api_key=news_api_key,
        summarizer_model=summarizer_model,
        analyzer_model=analyzer_model,
        device=device
    )
    
    print(f"Starting server...")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    import os
    
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        print("WARNING: NEWS_API_KEY environment variable not set")
        
    start_server(news_api_key=news_api_key)