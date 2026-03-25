# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Redis (for online feature store)

```bash
# macOS
brew install redis
redis-server

# Ubuntu/Debian
sudo apt-get install redis-server
sudo service redis-server start

# Docker
docker run -d -p 6379:6379 redis:latest
```

### 3. Run Your First Pipeline

```bash
# Ingest historical data and compute features
python main.py batch --mode full --tickers AAPL,TSLA

# This will:
# - Fetch historical data from yfinance
# - Validate and clean the data
# - Compute 50+ technical features
# - Store in offline feature store (Parquet)
# - Update online feature store (Redis)
```

### 4. Launch Dashboard

```bash
python main.py dashboard

# Or directly:
streamlit run dashboard/app.py
```

Visit http://localhost:8501 to see your dashboard!

### 5. Check System Status

```bash
python main.py status
```

## 📊 Common Use Cases

### Run Incremental Update

```bash
# Update features with latest data (last 5 days)
python main.py batch --mode incremental --lookback-days 5
```

### Start Streaming Simulation

```bash
# Simulate real-time updates every 60 seconds
python main.py stream --interval 60 --max-iterations 10
```

### Generate Analytics

```bash
# Analyze features for a specific ticker
python main.py analytics --ticker AAPL --plots
```

### Run Backtesting

```bash
# Test RSI strategy
python -m backtesting.backtest_engine --strategy rsi --ticker AAPL

# Test all strategies
python -m backtesting.backtest_engine --strategy all --ticker AAPL
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:

- Tickers to track
- Date ranges
- Feature parameters (RSI period, MA windows, etc.)
- Storage locations
- Redis connection settings

## 📁 Project Structure

```
project/
├── data_ingestion/       # Fetch stock data
├── data_validation/      # Clean and validate
├── feature_engineering/  # Compute features
├── feature_store/        # Store features (offline + online)
├── pipelines/           # Orchestration
├── analytics/           # Analysis and insights
├── backtesting/         # Strategy evaluation
├── dashboard/           # Streamlit UI
├── config/              # Configuration
└── utils/               # Utilities
```

## 🎯 Next Steps

1. **Customize Features**: Edit `feature_engineering/features.py` to add your own features
2. **Create Strategies**: Add new strategies in `backtesting/strategies.py`
3. **Schedule Pipelines**: Use cron or Airflow to automate updates
4. **Scale Up**: Add more tickers, reduce intervals, add more features

## 🐛 Troubleshooting

### Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### No Data Found
```bash
# Run batch pipeline first
python main.py batch --mode full
```

### Import Errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

## 📚 Learn More

- Check `README.md` for detailed documentation
- Explore example notebooks (coming soon)
- Read inline code documentation

## 💡 Tips

- Start with 2-3 tickers for testing
- Use shorter date ranges initially
- Monitor logs in `./logs/` directory
- Check data quality reports after validation
- Compare strategy performance before live trading

Happy feature engineering! 🚀
