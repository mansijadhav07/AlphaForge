# Dummy Data Analysis - AlphaForge Project

## Summary
Analysis of where dummy/mock data is currently used and what needs real data integration.

---

## ✅ ALREADY USING REAL DATA

### 1. Baseline Comparison (`/api/pgm/baseline-comparison/{symbol}`)
- **Status**: ✅ Real data implemented
- **Location**: `api/pgm_routes.py` (lines 1195-1230)
- **Data Source**: Pre-computed results in `data/baseline_comparison/{symbol}_comparison.json`
- **Script**: `scripts/train_baseline_comparison.py`
- **Symbols**: AAPL, TSLA, GOOGL, MSFT
- **Fallback**: Mock data if file not found

### 2. Calibration Analysis (`/api/pgm/calibration/{symbol}`)
- **Status**: ✅ Real data implemented
- **Location**: `api/pgm_routes.py` (lines 1355-1395)
- **Data Source**: Pre-computed results in `data/calibration/{symbol}_calibration.json`
- **Script**: `scripts/generate_calibration_data.py`
- **Symbols**: AAPL, TSLA, GOOGL, MSFT
- **Fallback**: Mock data if file not found

### 3. PGM Core Predictions
- **Status**: ✅ Real data (uses trained model)
- **Endpoints**: 
  - `/api/pgm/probabilities/{symbol}`
  - `/api/pgm/explanation/{symbol}`
  - `/api/pgm/signal/{symbol}`
  - `/api/pgm/feature-impact/{symbol}`
  - `/api/pgm/regime/{symbol}`
- **Data Source**: Trained PGM model + OfflineFeatureStore

---

## ⚠️ USING MOCK DATA (NEEDS REAL DATA)

### 1. Market Overview (`/api/market-overview`)
- **Status**: ⚠️ 100% Mock Data
- **Location**: `api/market_routes.py` (lines 23-86)
- **Mock Data**:
  - Random market regime (Bull/Bear/Sideways)
  - Random volatility index (10-30)
  - Random stock prices for AAPL, TSLA, GOOGL, MSFT
  - Random price changes and percentages
  - Random trading signals (BUY/SELL/HOLD)
- **What's Needed**:
  - Real-time or latest market data API integration
  - Actual regime detection from PGM
  - Real volatility calculations
  - Real price data from data ingestion
  - Real signal generation from PGM

### 2. Stock Features (`/api/features/{symbol}`)
- **Status**: ⚠️ 100% Mock Data
- **Location**: `api/market_routes.py` (lines 89-138)
- **Mock Data**:
  - 30 days of random OHLCV data
  - Random technical indicators (RSI, MACD, SMA, BB, ATR)
  - Random momentum scores
  - Random regime classifications
- **What's Needed**:
  - Read from OfflineFeatureStore
  - Use real computed features from feature engineering
  - Return actual historical data

### 3. Backtesting Results (`/api/backtest/{strategy}`)
- **Status**: ⚠️ 100% Mock Data
- **Location**: `api/market_routes.py` (lines 141-180)
- **Mock Data**:
  - Random equity curve
  - Random performance metrics (Sharpe, drawdown, win rate)
  - Random number of trades
- **What's Needed**:
  - Integration with `backtesting/backtest_engine.py`
  - Run actual backtests on historical data
  - Store and retrieve backtest results

### 4. Market Insights (`/api/insights`)
- **Status**: ⚠️ 100% Mock Data
- **Location**: `api/market_routes.py` (lines 183-230)
- **Mock Data**:
  - Static hardcoded insights
  - Generic warnings and opportunities
- **What's Needed**:
  - Generate insights from PGM predictions
  - Analyze recent prediction changes
  - Detect anomalies and regime changes
  - Create dynamic insights based on real data

### 5. Model Evaluation (`/api/pgm/evaluation/{symbol}`)
- **Status**: ⚠️ Partial Mock (fallback only)
- **Location**: `api/pgm_routes.py` (lines 575-620, 835-920)
- **Current Behavior**:
  - Tries to load cached results
  - Tries to evaluate on historical data
  - Falls back to mock if both fail
- **Mock Data** (`_get_mock_evaluation`):
  - Fixed confusion matrix
  - Static accuracy (65%)
  - Hardcoded calibration curves
  - Fixed probability distributions
- **What's Needed**:
  - Pre-compute evaluation for all symbols
  - Create script similar to `train_baseline_comparison.py`
  - Store results in `data/evaluation/{symbol}_evaluation.json`

### 6. Failure Analysis (`/api/pgm/failures/{symbol}`)
- **Status**: ⚠️ Partial Mock (fallback only)
- **Location**: `api/pgm_routes.py` (lines 650-750, 750-830)
- **Current Behavior**:
  - Tries to analyze failures on historical data
  - Falls back to mock if fails
- **Mock Data** (`_get_mock_failure_analysis`):
  - 3 hardcoded failure cases
  - Static failure summary
  - Generic insights
- **What's Needed**:
  - Pre-compute failure analysis for all symbols
  - Create script to generate failure data
  - Store results in `data/failures/{symbol}_failures.json`

### 7. Structure Analysis (`/api/pgm/structure-analysis`)
- **Status**: ⚠️ Partial Mock (fallback only)
- **Location**: `api/pgm_routes.py` (lines 950-1020)
- **Current Behavior**:
  - Tries to fetch real features from OfflineFeatureStore
  - Falls back to mock features if not found
- **Mock Data** (`_get_mock_features_df`):
  - 100 samples of random correlated features
  - Synthetic RSI, MACD, BB, volume, ATR
  - Artificial regime classifications
- **What's Needed**:
  - Ensure OfflineFeatureStore has data for all symbols
  - Fix `get_latest_features()` method call
  - Verify feature data availability

---

## 📋 PRIORITY ACTION ITEMS

### HIGH PRIORITY (User-Facing Features)

1. **Market Overview Endpoint**
   - Create `scripts/generate_market_overview.py`
   - Integrate with real price data
   - Use PGM for regime detection
   - Generate real signals
   - Update every 5-15 minutes

2. **Stock Features Endpoint**
   - Modify to read from OfflineFeatureStore
   - Return last 30-90 days of real features
   - Add caching for performance

3. **Insights Generation**
   - Create `analytics/insight_generator.py`
   - Analyze PGM predictions for anomalies
   - Detect regime changes
   - Generate dynamic insights
   - Store in database or JSON files

### MEDIUM PRIORITY (Analysis Features)

4. **Model Evaluation Pre-computation**
   - Create `scripts/generate_evaluation_data.py`
   - Similar to baseline comparison script
   - Evaluate PGM on test set for all symbols
   - Store in `data/evaluation/`

5. **Failure Analysis Pre-computation**
   - Create `scripts/generate_failure_analysis.py`
   - Analyze prediction failures
   - Store in `data/failures/`

6. **Backtesting Integration**
   - Create `scripts/run_backtests.py`
   - Use existing `backtesting/backtest_engine.py`
   - Store results in `data/backtests/`
   - Create API endpoint to retrieve results

### LOW PRIORITY (Already Has Fallback)

7. **Structure Analysis**
   - Verify OfflineFeatureStore data availability
   - Ensure all symbols have feature data
   - Test correlation analysis with real data

---

## 🔧 IMPLEMENTATION RECOMMENDATIONS

### For Market Data Endpoints

```python
# Option 1: Real-time API integration
# - Use yfinance, Alpha Vantage, or similar
# - Cache results for 5-15 minutes
# - Update on schedule

# Option 2: Use existing data pipeline
# - Read from OfflineFeatureStore
# - Use latest ingested data
# - Compute indicators on-the-fly
```

### For Pre-computed Results

```python
# Follow pattern from baseline_comparison and calibration:
# 1. Create script in scripts/
# 2. Generate results for all symbols
# 3. Save to data/{feature}/
# 4. API loads from JSON files
# 5. Fallback to mock if file missing
```

### For Dynamic Insights

```python
# Create insight generator:
# 1. Monitor PGM predictions over time
# 2. Detect significant changes
# 3. Identify high-confidence predictions
# 4. Flag regime transitions
# 5. Generate natural language insights
```

---

## 📊 CURRENT DATA COVERAGE

| Feature | AAPL | TSLA | GOOGL | MSFT | Status |
|---------|------|------|-------|------|--------|
| Baseline Comparison | ✅ | ✅ | ✅ | ✅ | Real |
| Calibration | ✅ | ✅ | ✅ | ✅ | Real |
| PGM Predictions | ✅ | ✅ | ✅ | ✅ | Real |
| Market Overview | ❌ | ❌ | ❌ | ❌ | Mock |
| Stock Features | ❌ | ❌ | ❌ | ❌ | Mock |
| Backtesting | ❌ | ❌ | ❌ | ❌ | Mock |
| Insights | ❌ | ❌ | ❌ | ❌ | Mock |
| Evaluation | ❌ | ❌ | ❌ | ❌ | Mock |
| Failure Analysis | ❌ | ❌ | ❌ | ❌ | Mock |

---

## 🎯 NEXT STEPS

1. **Immediate**: Fix Market Overview and Stock Features (most visible to users)
2. **Short-term**: Generate Evaluation and Failure Analysis data
3. **Medium-term**: Implement dynamic Insights generation
4. **Long-term**: Integrate full backtesting pipeline

---

Generated: 2026-03-26
