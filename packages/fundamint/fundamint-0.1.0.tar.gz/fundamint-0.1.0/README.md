# FundaMint

A Python package for stock recommendations based on news analysis using open-source LLMs.

## Features

- Collects financial news from public APIs
- Summarizes news articles using open-source LLMs
- Analyzes news to provide stock recommendations
- Evaluates buy/sell decisions for specific stocks
- Provides both CLI and API interfaces
- Supports training and fine-tuning custom models
- Generates detailed markdown reports

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fundamint.git
cd fundamint

# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Requirements

- Python 3.8+
- NewsAPI key (get one at https://newsapi.org)

## Quick Start

### Set your NewsAPI key

```bash
# Linux/macOS
export NEWS_API_KEY=your_api_key

# Windows (Command Prompt)
set NEWS_API_KEY=your_api_key

# Windows (PowerShell)
$env:NEWS_API_KEY = "your_api_key"
```

### Run the sample script

```bash
python fundamint/examples/sample1.py
```

This will:
1. Fetch market news and stock-specific news
2. Summarize the news using an LLM
3. Generate stock recommendations
4. Create detailed reports in the `reports` directory

## Usage

### Command Line Interface

Get stock recommendations:

```bash
# Get top stock recommendations
python -m fundamint.cli recommend --limit 5 --report

# Analyze a specific stock
python -m fundamint.cli analyze AAPL --action buy --report
```

### Python API

```python
import os
from fundamint.news.collector import NewsCollector
from fundamint.news.processor import NewsProcessor
from fundamint.models.summarizer import NewsSummarizer
from fundamint.models.analyzer import StockAnalyzer
from fundamint.utils.report_generator import ReportGenerator

# Set API key
os.environ["NEWS_API_KEY"] = "your_api_key"

# Initialize components
news_collector = NewsCollector()
news_processor = NewsProcessor()
summarizer = NewsSummarizer()
analyzer = StockAnalyzer()
report_generator = ReportGenerator()

# Get market news
market_news = news_collector.get_market_news(days=1)
filtered_news = news_processor.filter_relevant_articles(market_news)
processed_news = news_processor.extract_key_information(filtered_news)
summarized_news = summarizer.summarize_articles(processed_news)
market_summary = summarizer.create_market_summary(summarized_news)

# Get stock-specific news
ticker = "AAPL"
stock_news = news_collector.get_stock_news(ticker, days=1)
filtered_stock_news = news_processor.filter_relevant_articles(stock_news)
processed_stock_news = news_processor.extract_key_information(filtered_stock_news)
summarized_stock_news = summarizer.summarize_articles(processed_stock_news)

# Analyze stock
analysis = analyzer.analyze_stock(ticker, market_summary, summarized_stock_news)
print(f"Recommendation: {analysis['recommendation']}")
print(f"Confidence: {analysis['confidence']}")
print(analysis['analysis'])

# Generate report
report_path = report_generator.generate_stock_report(
    ticker=ticker,
    analysis=analysis,
    stock_info=get_stock_info(ticker),
    market_summary=market_summary,
    stock_news=summarized_stock_news
)
print(f"Report saved to: {report_path}")
```

## Example Reports

### Stock Report

The stock reports include:

- Stock information and metrics
- Market summary
- Detailed analysis and recommendation
- News article summaries
- Model performance metrics

Example stock report:

```markdown
# Stock Analysis Report: AAPL
**Generated on:** 2025-05-29 17:31:53

## Recommendation Summary
**Recommendation:** BUY
**Confidence:** LOW

## Stock Information
| Metric | Value |
| ------ | ----- |
| Symbol | AAPL |
| Name | Apple Inc. |
| Current Price | 198.99 |
| Previous Close | 198.11 |
| Market Cap | 3,075,123,200,000.00 |
| Pe Ratio | 30.76 |
| Dividend Yield | 0.0055 |

## Market Summary
Shares of Broadcom Inc. are up 68% in the past year. Tesla billionaire Elon Musk quietly confirmed what could be a bitcoin and crypto game-changer. U.S. stocks drifted lower on Wednesday, cooling down a day after leaping within a few good days worth of gains from their all-time high.

## Detailed Analysis
Based on recent market trends and news about AAPL, there are several factors to consider. The market summary indicates mixed signals with some stocks performing well while the overall market is drifting lower. Apple continues to show resilience in a challenging market environment. The company's strong ecosystem and loyal customer base provide stability even during market fluctuations. Recent product announcements and AI initiatives suggest potential for future growth. Recommendation: BUY with LOW confidence.
```

### Market Report

The market reports include:

- Market indices
- Overall market summary
- Top stock recommendations
- Detailed analyses for each stock
- Recent market news summaries

Example market report:

```markdown
# Market Analysis Report
**Generated on:** 2025-05-29 17:35:17

## Market Indices
| Index | Value |
| ----- | ----- |
| S&P 500 | 5,912.17 |
| Dow Jones | 42,215.73 |
| NASDAQ | 19,175.87 |
| Russell 2000 | 2,074.78 |
| VIX | 19.18 |

## Market Summary
Shares of Broadcom Inc. are up 68% in the past year. Tesla billionaire Elon Musk quietly confirmed what could be a bitcoin and crypto game-changer. U.S. stocks drifted lower on Wednesday, cooling down a day after leaping within a few good days worth of gains from their all-time high.

## Top Stock Recommendations
| Rank | Ticker | Recommendation | Confidence |
| ---- | ------ | -------------- | ---------- |
| 1 | AMZN | BUY | HIGH |
| 2 | AAPL | BUY | LOW |
| 3 | TSLA | BUY | LOW |
| 4 | MSFT | SELL | LOW |
| 5 | GOOGL | HOLD | LOW |
```

## Training Custom Models

You can train custom models for news summarization and stock analysis:

```bash
# Prepare training data in JSON format
# Train summarizer model
python -m fundamint.cli train --model summarizer --data training_data.json --output ./my_summarizer --epochs 3

# Train analyzer model
python -m fundamint.cli train --model analyzer --data training_data.json --output ./my_analyzer --epochs 3
```

## API Server

Start the API server:

```bash
python -m fundamint.cli server --port 8000
```

Then access the API at http://localhost:8000/docs

Available endpoints:
- GET `/recommendations` - Get top stock recommendations
- POST `/analyze` - Analyze a specific stock for buy/sell action

## Project Structure

```
fundamint/
├── fundamint/
│   ├── __init__.py
│   ├── cli.py
│   ├── news/
│   │   ├── __init__.py
│   │   ├── collector.py
│   │   └── processor.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── summarizer.py
│   │   ├── analyzer.py
│   │   └── trainer.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py
│   └── utils/
│       ├── __init__.py
│       ├── stock_data.py
│       └── report_generator.py
├── setup.py
└── README.md
```

## License

MIT

## Disclaimer

This package is for educational and research purposes only. The stock recommendations provided should not be considered financial advice. Always consult with a qualified financial advisor before making investment decisions.