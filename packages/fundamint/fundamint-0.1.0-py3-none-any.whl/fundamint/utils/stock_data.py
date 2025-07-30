"""Utility functions for fetching and processing stock data."""

from typing import Dict, Any, List, Optional
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(ticker: str, period: str = "1mo") -> Optional[pd.DataFrame]:
    """Get historical stock data.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period to fetch data for (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        DataFrame with stock data or None if error
    """
    print(f"  • Fetching historical data for {ticker} over {period} period...")
    start_time = time.time()
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        print(f"  • Retrieved {len(hist)} data points in {time.time() - start_time:.2f} seconds")
        return hist
    except Exception as e:
        print(f"  • ERROR fetching stock data for {ticker}: {e}")
        return None

def get_stock_info(ticker: str) -> Dict[str, Any]:
    """Get stock information.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with stock information
    """
    print(f"  • Fetching information for {ticker}...")
    start_time = time.time()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract key information
        key_info = {
            'symbol': ticker,
            'name': info.get('shortName', 'Unknown'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'current_price': info.get('regularMarketPrice', 0),
            'previous_close': info.get('previousClose', 0),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
        }
        
        print(f"  • Stock information retrieved in {time.time() - start_time:.2f} seconds")
        return key_info
    except Exception as e:
        print(f"  • ERROR fetching stock info for {ticker}: {e}")
        return {'symbol': ticker, 'error': str(e)}

def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for stock data.
    
    Args:
        data: DataFrame with stock data
        
    Returns:
        DataFrame with added technical indicators
    """
    if data is None or len(data) == 0:
        print("  • WARNING: No data provided for technical indicator calculation")
        return pd.DataFrame()
        
    print(f"  • Calculating technical indicators for {len(data)} data points...")
    start_time = time.time()
    
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Simple Moving Averages
    print("  • Calculating Simple Moving Averages (SMA)...")
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Exponential Moving Averages
    print("  • Calculating Exponential Moving Averages (EMA)...")
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    # MACD
    print("  • Calculating MACD...")
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Relative Strength Index (RSI)
    print("  • Calculating RSI...")
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    print("  • Calculating Bollinger Bands...")
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + 2 * df['BB_Std']
    df['BB_Lower'] = df['BB_Middle'] - 2 * df['BB_Std']
    
    print(f"  • Technical indicators calculated in {time.time() - start_time:.2f} seconds")
    return df

def get_market_indices() -> Dict[str, float]:
    """Get current values of major market indices.
    
    Returns:
        Dictionary with index values
    """
    print("  • Fetching major market indices...")
    start_time = time.time()
    
    indices = {
        'S&P 500': '^GSPC',
        'Dow Jones': '^DJI',
        'NASDAQ': '^IXIC',
        'Russell 2000': '^RUT',
        'VIX': '^VIX'
    }
    
    result = {}
    
    for name, ticker in indices.items():
        try:
            index = yf.Ticker(ticker)
            info = index.info
            result[name] = info.get('regularMarketPrice', 0)
        except Exception as e:
            print(f"  • ERROR fetching {name} index: {e}")
            result[name] = 0
    
    print(f"  • Market indices retrieved in {time.time() - start_time:.2f} seconds")        
    return result