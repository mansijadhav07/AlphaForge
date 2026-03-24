# Real-Time Financial Feature Store & Analytics Platform

## 🎯 Project Overview

A production-grade system for ingesting, processing, and analyzing financial market data with real-time feature engineering capabilities. This platform combines offline batch processing with online streaming simulation to provide a comprehensive feature store for quantitative analysis and backtesting.

## 🏗️ Architecture

```
┌─────────────────┐
│  Data Sources   │ (yfinance API)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Ingestion  │ (Historical + Real-time simulation)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Validation │ (Quality checks, cleaning)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Feature Engineer │ (Technical indicators, time-series features)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│      Feature Store              │
│  ┌──────────┐   ┌──────────┐  │
│  │ Offline  │   │  Online  │  │
│  │ (Parquet)│   │ (Redis)  │  │
│  └──────────┘   └──────────┘  │
└────────┬────────────────────────┘
         │
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
    Analytics  Backtesting Dashboard  Monitoring
```

## 📁 Project Structure

```
project/
├── data_ingestion/       # Data fetching and storage
├── data_validation/      # Data quality and cleaning
├── feature_engineering/  # Feature computation logic
├── feature_store/        # Offline/Online storage management
├── pipelines/           # Orchestration and workflows
├── analytics/           # Analysis and insights
├── backtesting/         # Strategy evaluation
├── dashboard/           # Streamlit UI
├── config/              # Configuration files
├── utils/               # Shared utilities
├── data/                # Data storage (gitignored)
├── logs/                # Application logs
└── tests/               # Unit tests
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Redis (for online feature store)
- 8GB+ RAM recommended

### Installation

1. Clone the repository
```bash
git clone <repo-url>
cd project
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Start Redis (if using online store)
```bash
redis-server
```

5. Configure settings
```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings
```

## 🎮 Usage

### 1. Ingest Historical Data
```bash
python -m pipelines.batch_pipeline --mode historical --tickers AAPL,TSLA,GOOGL
```

### 2. Run Feature Engineering
```bash
python -m pipelines.batch_pipeline --mode features
```

### 3. Start Streaming Simulation
```bash
python -m pipelines.streaming_pipeline
```

### 4. Launch Dashboard
```bash
streamlit run dashboard/app.py
```

### 5. Run Backtesting
```bash
python -m backtesting.backtest_engine --strategy rsi_strategy
```

## 📊 Features Implemented

### Basic Features
- **Returns**: Daily returns, log returns
- **Price Levels**: Open, High, Low, Close, Volume

### Trend Features
- **Moving Averages**: SMA_10, SMA_30, SMA_50
- **Trend Slope**: Linear regression slope over window

### Volatility Features
- **Rolling Std**: 10-day, 30-day volatility
- **ATR**: Average True Range
- **Bollinger Bands**: Upper, Middle, Lower bands

### Momentum Features
- **RSI**: Relative Strength Index (14-period)
- **MACD**: MACD line, Signal line, Histogram
- **Stochastic**: %K, %D oscillators

### Lag Features
- **Price Lags**: 1-day, 5-day, 10-day lags
- **Volume Lags**: Previous volume levels

### Advanced Features
- **Regime Detection**: Bull/Bear/Sideways classification
- **Momentum Score**: Composite indicator
- **Feature Interactions**: volatility×return, volume×price_change

## 🧪 Backtesting Strategies

### RSI Mean Reversion
- Buy: RSI < 30
- Sell: RSI > 70

### MACD Crossover
- Buy: MACD crosses above signal
- Sell: MACD crosses below signal

### Trend Following
- Buy: Price > SMA_50 and momentum positive
- Sell: Price < SMA_50

## 📈 Performance Metrics

- Total Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor

## 🔧 Configuration

Edit `config/config.yaml`:

```yaml
data:
  tickers: [AAPL, TSLA, GOOGL, MSFT]
  start_date: "2020-01-01"
  end_date: "2024-12-31"

features:
  windows:
    short: 10
    medium: 30
    long: 50
  rsi_period: 14
  macd_params: [12, 26, 9]

storage:
  data_dir: "./data"
  offline_store: "./data/features"
  redis_host: "localhost"
  redis_port: 6379
```

## 📊 Dashboard Features

- Real-time feature values
- Feature correlation heatmaps
- Backtesting results visualization
- Data quality monitoring
- Feature importance analysis

## 🔍 Monitoring & Observability

- Pipeline execution logs
- Data freshness tracking
- Feature update timestamps
- Error alerting
- Performance metrics

## 🧪 Testing

```bash
pytest tests/
```

## 📝 Feature Versioning

Features support versioning for A/B testing:
- `RSI_v1`: Standard 14-period RSI
- `RSI_v2`: Modified with different smoothing

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add docstrings to all functions
3. Write unit tests for new features
4. Update documentation

## 📄 License

MIT License

## 👥 Authors

Senior Software Engineering Team

## 🔗 References

- Technical Analysis Library: https://technical-analysis-library-in-python.readthedocs.io/
- Feature Store Concepts: https://www.featurestore.org/
- Quantitative Finance: https://quantlib.org/
