# Mock Data Audit - AlphaForge Project
**Date**: March 26, 2026
**Status**: Comprehensive Analysis

---

## Executive Summary

This document identifies all remaining mock/dummy data usage across the AlphaForge project after the real data integration refactor.

### Overall Status
- ✅ **Backend Core**: Real data integrated for market routes
- ⚠️ **Backend PGM**: Mock fallbacks exist for error cases
- ⚠️ **Frontend API**: Mock fallbacks exist for all endpoints
- ✅ **Data Pipeline**: All real data sources working

---

## 🟢 FULLY REAL DATA (No Mock)

### 1. PGM Core Predictions
- **Endpoints**: 
  - `/api/pgm/probabilities/{symbol}`
  - `/api/pgm/explanation/{symbol}`
  - `/api/pgm/signal/{symbol}`
  - `/api/pgm/regime/{symbol}`
  - `/api/pgm/feature-impact/{symbol}`
  - `/api/pgm/graph`
- **Status**: ✅ 100% Real
- **Source**: Trained PGM model with real CPTs
- **Location**: `api/pgm_routes.py`

### 2. Baseline Comparison
- **Endpoint**: `/api/pgm/baseline-comparison/{symbol}`
- **Status**: ✅ Real data from precomputed JSON
- **Source**: `data/baseline_comparison/{symbol}_comparison.json`
- **Fallback**: Returns 404 if file missing (no mock)

### 3. Calibration Analysis
- **Endpoint**: `/api/pgm/calibration/{symbol}`
- **Status**: ✅ Real data from precomputed JSON
- **Source**: `data/calibration/{symbol}_calibration.json`
- **Fallback**: Returns 404 if file missing (no mock)

### 4. Discretization
- **Endpoint**: `/api/discretization/bins`
- **Status**: ✅ Real data from encoder config
- **Source**: `data/pgm_model/encoder_config.json`

### 5. Market Overview (FIXED)
- **Endpoint**: `/api/market-overview`
- **Status**: ✅ Real data from DataService
- **Source**: yfinance + PGM predictions
- **Location**: `api/market_routes.py` (lines 33-156)

### 6. Stock Features (FIXED)
- **Endpoint**: `/api/features/{symbol}`
- **Status**: ✅ Real data from OfflineFeatureStore
- **Source**: `data/features/` parquet files
- **Location**: `api/market_routes.py` (lines 158-230)

### 7. Backtesting (FIXED)
- **Endpoint**: `/api/backtest/{strategy}`
- **Status**: ✅ Real data from parquet files
- **Source**: `data/backtesting/{strategy}_history.parquet`
- **Location**: `api/market_routes.py` (lines 232-320)

### 8. Insights (FIXED)
- **Endpoint**: `/api/insights`
- **Status**: ✅ Real data from PGM explanations
- **Source**: Dynamic generation from PGM service
- **Location**: `api/market_routes.py` (lines 275-330)

---

## ⚠️ MOCK FALLBACKS (Development Safety)

### Backend - PGM Routes (`api/pgm_routes.py`)

#### 1. Model Evaluation
- **Endpoint**: `/api/pgm/evaluation/{symbol}`
- **Primary**: Tries to load cached evaluation from `data/evaluation/`
- **Secondary**: Tries to evaluate on historical data
- **Fallback**: `_get_mock_evaluation()` (lines 835-920)
- **Mock Trigger**: When both real data sources fail
- **Mock Data**:
  - Fixed confusion matrix
  - Static accuracy (65%)
  - Hardcoded calibration curves
  - Generic probability distributions

**Recommendation**: Generate real evaluation data for all symbols using evaluation script.

#### 2. Failure Analysis
- **Endpoint**: `/api/pgm/failures/{symbol}`
- **Primary**: Analyzes failures on historical data
- **Fallback**: `_get_mock_failure_analysis()` (lines 750-833)
- **Mock Trigger**: When historical data analysis fails
- **Mock Data**:
  - 3 hardcoded failure cases
  - Static failure summary (35 total failures)
  - Generic insights

**Recommendation**: Ensure historical data exists for all symbols.

#### 3. Structure Analysis
- **Endpoint**: `/api/pgm/structure-analysis`
- **Primary**: Fetches real features from OfflineFeatureStore
- **Fallback**: `_get_mock_features_df()` (lines 990-1020)
- **Mock Trigger**: When feature store is empty
- **Mock Data**:
  - 100 samples of synthetic features
  - Random correlated RSI, MACD, BB, volume, ATR

**Recommendation**: Ensure feature store is populated.

---

## ⚠️ FRONTEND MOCK FALLBACKS (`frontend/lib/api.ts`)

All frontend API methods have mock fallbacks for development resilience:

### 1. Market Data Methods
- `getFeatures()` → `getMockFeatures()` (lines 165-205)
- `getMarketOverview()` → `getMockMarketOverview()` (lines 206-224)
- `getBacktestResults()` → `getMockBacktestResults()` (lines 225-264)
- `getInsights()` → `getMockInsights()` (lines 265-290)

### 2. PGM Methods
- `getPGMGraph()` → `getMockPGMGraph()` (lines 470-505)
- `getPGMProbabilities()` → `getMockPGMProbabilities()` (lines 506-518)
- `getPGMExplanation()` → `getMockPGMExplanation()` (lines 519-535)
- `getPGMFeatureImpact()` → `getMockFeatureImpact()` (lines 536-552)
- `getPGMEvaluation()` → `getMockEvaluation()` (lines 553-615)
- `getPGMFailures()` → `getMockFailures()` (lines 616-680)

**Behavior**: 
- Frontend catches API errors
- Falls back to mock data silently
- Logs error to console
- User sees data (mock) instead of error

**Recommendation**: Keep these fallbacks for development, but add visual indicator when mock data is shown.

---

## 📊 Mock Data Usage Summary

| Component | Endpoint | Status | Mock Location | Trigger |
|-----------|----------|--------|---------------|---------|
| Market Overview | `/api/market-overview` | ✅ Real | None | N/A |
| Stock Features | `/api/features/{symbol}` | ✅ Real | None | N/A |
| Backtesting | `/api/backtest/{strategy}` | ✅ Real | None | N/A |
| Insights | `/api/insights` | ✅ Real | None | N/A |
| PGM Predictions | `/api/pgm/*` | ✅ Real | None | N/A |
| Baseline Comparison | `/api/pgm/baseline-comparison` | ✅ Real | None | N/A |
| Calibration | `/api/pgm/calibration` | ✅ Real | None | N/A |
| Discretization | `/api/discretization/bins` | ✅ Real | None | N/A |
| **Evaluation** | `/api/pgm/evaluation` | ⚠️ Fallback | `_get_mock_evaluation()` | No cached data |
| **Failure Analysis** | `/api/pgm/failures` | ⚠️ Fallback | `_get_mock_failure_analysis()` | Analysis fails |
| **Structure Analysis** | `/api/pgm/structure-analysis` | ⚠️ Fallback | `_get_mock_features_df()` | No features |
| **Frontend (All)** | All endpoints | ⚠️ Fallback | `getMock*()` methods | API error |

---

## 🎯 Recommendations

### High Priority
1. **Generate Evaluation Data**: Run evaluation script for all symbols
   ```bash
   python3 scripts/generate_evaluation_data.py
   ```

2. **Ensure Feature Store**: Verify feature store has data for all symbols
   ```bash
   python3 scripts/populate_feature_store.py
   ```

### Medium Priority
3. **Add Mock Indicator**: Show visual indicator in frontend when mock data is displayed
   ```typescript
   // Add to API responses
   interface ApiResponse<T> {
     data: T
     isMock: boolean
     source: 'real' | 'mock' | 'cached'
   }
   ```

4. **Remove Frontend Fallbacks**: Once backend is stable, remove frontend mock fallbacks
   - Replace with proper error handling
   - Show user-friendly error messages
   - Add retry mechanisms

### Low Priority
5. **Monitoring**: Add metrics to track mock data usage
   - Log when mock fallbacks are triggered
   - Alert if mock usage exceeds threshold
   - Dashboard showing real vs mock data ratio

---

## ✅ Completed Refactoring

### Backend (`api/market_routes.py`)
- ✅ Eliminated all mock data from market routes
- ✅ Integrated DataService for centralized data access
- ✅ Real market data from yfinance
- ✅ Real features from OfflineFeatureStore
- ✅ Real backtest data from parquet files
- ✅ Dynamic insights from PGM predictions
- ✅ Proper error handling (404/503 instead of mock)

### Data Service (`services/data_service.py`)
- ✅ Centralized data access layer
- ✅ 5-minute caching for performance
- ✅ Real data from all sources
- ✅ No mock data fallbacks

---

## 🔍 Testing Mock Fallbacks

To test if mock fallbacks are triggered:

### Backend
```bash
# Test evaluation without cached data
curl http://localhost:8000/api/pgm/evaluation/INVALID_SYMBOL

# Test failure analysis without data
curl http://localhost:8000/api/pgm/failures/INVALID_SYMBOL

# Test structure analysis without features
# (Requires empty feature store)
```

### Frontend
```bash
# Stop backend server
# Frontend will fall back to mock data for all endpoints
# Check browser console for "Error fetching..." messages
```

---

## 📝 Notes

1. **Mock fallbacks are intentional** for development resilience
2. **Production deployment** should have all real data sources populated
3. **Frontend fallbacks** prevent UI crashes during development
4. **Backend fallbacks** are last resort after trying real data sources
5. **All core functionality** (PGM predictions, market data) uses real data

---

## Next Steps

1. Run evaluation script for all symbols
2. Verify feature store population
3. Add mock data indicator to frontend
4. Monitor mock fallback usage in production
5. Consider removing frontend fallbacks once backend is stable
