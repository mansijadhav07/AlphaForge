# Complete Feature List

## 📊 Computed Features (50+)

### Basic Features (5)

| Feature | Description | Formula |
|---------|-------------|---------|
| `return` | Daily simple return | `(close_t - close_t-1) / close_t-1` |
| `log_return` | Daily log return | `log(close_t / close_t-1)` |
| `high_low_range` | Intraday range | `(high - low) / close` |
| `open_close_range` | Open-close range | `(close - open) / open` |
| `volume_change` | Volume change | `(volume_t - volume_t-1) / volume_t-1` |

### Trend Features (11)

| Feature | Description | Window |
|---------|-------------|--------|
| `sma_10` | Simple Moving Average | 10 days |
| `sma_30` | Simple Moving Average | 30 days |
| `sma_50` | Simple Moving Average | 50 days |
| `ema_10` | Exponential Moving Average | 10 days |
| `ema_30` | Exponential Moving Average | 30 days |
| `price_to_sma_10` | Price relative to SMA | - |
| `price_to_sma_30` | Price relative to SMA | - |
| `price_to_sma_50` | Price relative to SMA | - |
| `trend_slope_10` | Linear regression slope | 10 days |
| `trend_slope_30` | Linear regression slope | 30 days |

### Volatility Features (9)

| Feature | Description | Window |
|---------|-------------|--------|
| `volatility_10` | Rolling standard deviation | 10 days |
| `volatility_30` | Rolling standard deviation | 30 days |
| `atr` | Average True Range | 14 days |
| `atr_pct` | ATR as % of price | - |
| `bb_upper` | Bollinger Band Upper | 20 days |
| `bb_middle` | Bollinger Band Middle | 20 days |
| `bb_lower` | Bollinger Band Lower | 20 days |
| `bb_width` | Bollinger Band Width | - |
| `bb_position` | Price position in bands | - |

### Momentum Features (10)

| Feature | Description | Period |
|---------|-------------|--------|
| `rsi` | Relative Strength Index | 14 |
| `macd` | MACD Line | 12/26 |
| `macd_signal` | MACD Signal Line | 9 |
| `macd_diff` | MACD Histogram | - |
| `stoch_k` | Stochastic %K | 14 |
| `stoch_d` | Stochastic %D | 3 |
| `roc_10` | Rate of Change | 10 days |
| `roc_30` | Rate of Change | 30 days |
| `mfi` | Money Flow Index | 14 |

### Lag Features (5)

| Feature | Description | Lag |
|---------|-------------|-----|
| `close_lag_1` | Previous close price | 1 day |
| `close_lag_5` | Close price 5 days ago | 5 days |
| `close_lag_10` | Close price 10 days ago | 10 days |
| `return_lag_1` | Previous return | 1 day |
| `return_lag_5` | Return 5 days ago | 5 days |
| `volume_lag_1` | Previous volume | 1 day |
| `volume_lag_5` | Volume 5 days ago | 5 days |

### Advanced Features (10+)

| Feature | Description | Type |
|---------|-------------|------|
| `regime` | Market regime | Classification (1=Bull, 0=Sideways, -1=Bear) |
| `momentum_score` | Composite momentum | Normalized score (-1 to 1) |
| `volatility_return_interaction` | Volatility × Return | Interaction |
| `volume_price_interaction` | Volume change × Return | Interaction |
| `price_momentum_5` | 5-day price momentum | Momentum |
| `price_momentum_20` | 20-day price momentum | Momentum |
| `volume_sma_20` | Volume moving average | 20 days |
| `volume_to_sma` | Volume relative to average | Ratio |

## 🎯 Feature Categories

### 1. Price-Based Features
- Raw prices (OHLC)
- Returns (simple, log)
- Price changes
- Price ratios

### 2. Volume-Based Features
- Raw volume
- Volume changes
- Volume ratios
- Volume momentum

### 3. Time-Series Features
- Moving averages
- Exponential smoothing
- Trend analysis
- Seasonality (future)

### 4. Technical Indicators
- Momentum oscillators
- Trend indicators
- Volatility measures
- Volume indicators

### 5. Statistical Features
- Rolling statistics
- Percentiles
- Z-scores
- Correlations

### 6. Derived Features
- Feature interactions
- Composite scores
- Regime classifications
- Custom indicators

## 📈 Feature Properties

### Stationarity
- **Stationary**: Returns, changes, ratios
- **Non-stationary**: Prices, cumulative values

### Frequency
- **Daily**: All current features
- **Intraday**: Future enhancement
- **Weekly/Monthly**: Aggregations

### Lookback Windows
- **Short-term**: 10 days
- **Medium-term**: 30 days
- **Long-term**: 50 days
- **Custom**: Configurable

## 🔧 Feature Engineering Techniques

### 1. Rolling Window Operations
```python
df['sma_10'] = df['close'].rolling(window=10).mean()
df['volatility_10'] = df['return'].rolling(window=10).std()
```

### 2. Exponential Smoothing
```python
df['ema_10'] = df['close'].ewm(span=10, adjust=False).mean()
```

### 3. Technical Indicators (TA-Lib)
```python
df['rsi'] = ta.momentum.rsi(df['close'], window=14)
df['macd'] = ta.trend.MACD(df['close']).macd()
```

### 4. Custom Calculations
```python
df['regime'] = detect_regime(df['trend_slope_30'])
df['momentum_score'] = composite_momentum(df)
```

### 5. Feature Interactions
```python
df['vol_ret_interaction'] = df['volatility_10'] * df['return']
```

## 📊 Feature Statistics

### Distribution Types
- **Normal**: Returns, changes
- **Skewed**: Volume, momentum indicators
- **Bounded**: RSI (0-100), Stochastic (0-100)
- **Unbounded**: Prices, MACD

### Missing Value Handling
- **Forward fill**: Price-based features
- **Backward fill**: Volume-based features
- **Drop**: Critical features
- **Interpolate**: Time-series features

### Outlier Treatment
- **Winsorization**: Extreme returns
- **Clipping**: Bounded indicators
- **Removal**: Data quality issues
- **Flagging**: Anomaly detection

## 🎨 Feature Visualization

### Time Series Plots
- Price trends
- Indicator overlays
- Volume bars
- Regime highlighting

### Distribution Plots
- Histograms
- Box plots
- Violin plots
- Q-Q plots

### Correlation Analysis
- Heatmaps
- Scatter plots
- Pair plots
- Network graphs

### Feature Importance
- Bar charts
- Ranking tables
- SHAP values (future)
- Permutation importance (future)

## 🔍 Feature Selection

### Correlation-Based
- Remove highly correlated features (>0.9)
- Select features correlated with target
- Hierarchical clustering

### Statistical Tests
- Chi-square test
- ANOVA F-test
- Mutual information

### Model-Based
- Feature importance from trees
- L1 regularization
- Recursive feature elimination

### Domain Knowledge
- Technical analysis principles
- Market microstructure
- Trading experience

## 📝 Feature Metadata

Each feature includes:
- **Name**: Unique identifier
- **Description**: What it measures
- **Formula**: Calculation method
- **Parameters**: Window sizes, periods
- **Type**: Continuous, categorical, binary
- **Range**: Min/max values
- **Unit**: Price, percentage, index
- **Frequency**: Daily, intraday
- **Lag**: Historical dependency
- **Version**: Feature version

## 🚀 Future Features

### Planned Additions
1. **Market Microstructure**
   - Bid-ask spread
   - Order flow imbalance
   - Trade intensity

2. **Alternative Data**
   - Sentiment scores
   - News analytics
   - Social media metrics

3. **Cross-Asset Features**
   - Correlation with indices
   - Sector relative strength
   - Market breadth

4. **Machine Learning Features**
   - Autoencoder embeddings
   - Clustering labels
   - Anomaly scores

5. **Time-Based Features**
   - Day of week
   - Month of year
   - Holiday effects
   - Earnings calendar

## 📚 References

### Technical Analysis
- Murphy, J. J. (1999). Technical Analysis of the Financial Markets
- Pring, M. J. (2002). Technical Analysis Explained

### Feature Engineering
- Kuhn, M., & Johnson, K. (2019). Feature Engineering and Selection
- Zheng, A., & Casari, A. (2018). Feature Engineering for Machine Learning

### Quantitative Finance
- Chan, E. (2013). Algorithmic Trading
- Jansen, S. (2020). Machine Learning for Algorithmic Trading

## 🎯 Best Practices

1. **Avoid Look-Ahead Bias**: Use only historical data
2. **Handle Missing Values**: Consistent strategy
3. **Normalize Features**: Scale appropriately
4. **Version Features**: Track changes
5. **Document Thoroughly**: Clear descriptions
6. **Test Robustness**: Multiple time periods
7. **Monitor Drift**: Feature stability
8. **Validate Logic**: Sanity checks
