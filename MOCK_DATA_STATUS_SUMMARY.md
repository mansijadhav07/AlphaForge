# Mock Data Status Summary
**Date**: March 26, 2026
**Analysis**: Complete Project Audit

---

## 🎯 Quick Status

### Backend API
- ✅ **Market Routes**: 100% Real Data (4/4 endpoints)
- ⚠️ **PGM Routes**: Real Data with Mock Fallbacks (2/3 endpoints using mock)
- ✅ **Discretization**: 100% Real Data

### Frontend
- ⚠️ **All Endpoints**: Mock fallbacks exist for error handling

---

## 📊 Detailed Breakdown

### ✅ USING REAL DATA (No Mock)

#### 1. Market Overview - `/api/market-overview`
- **Status**: ✅ Real Data
- **Source**: yfinance + PGM predictions
- **Test Result**: Returns empty arrays (data fetch issues, but no mock)

#### 2. Stock Features - `/api/features/{symbol}`
- **Status**: ✅ Real Data  
- **Source**: OfflineFeatureStore parquet files
- **Test Result**: Returns dict (needs investigation)

#### 3. Backtesting - `/api/backtest/{strategy}`
- **Status**: ✅ Real Data
- **Source**: `data/backtesting/*.parquet`
- **Test Result**: ✅ Working - 808 data points, 0.93% return

#### 4. Insights - `/api/insights`
- **Status**: ✅ Real Data
- **Source**: Dynamic PGM explanations
- **Test Result**: ✅ Returns 1 insight

#### 5. PGM Predictions (All)
- **Endpoints**: probabilities, explanation, signal, regime, feature-impact, graph
- **Status**: ✅ 100% Real
- **Source**: Trained PGM model

#### 6. Baseline Comparison
- **Status**: ✅ Real Data
- **Source**: Precomputed JSON files

#### 7. Calibration
- **Status**: ✅ Real Data
- **Source**: Precomputed JSON files

#### 8. Discretization
- **Status**: ✅ Real Data
- **Source**: Encoder config JSON

---

### ⚠️ USING MOCK DATA (Fallback Mode)

#### 1. Model Evaluation - `/api/pgm/evaluation/{symbol}`
- **Status**: ⚠️ **MOCK DATA ACTIVE**
- **Reason**: No cached evaluation files exist
- **Mock Location**: `api/pgm_routes.py::_get_mock_evaluation()` (lines 835-920)
- **Test Result**: Returns mock data (accuracy: 65%, n_samples: 100)
- **Fix**: Run evaluation script to generate real data
  ```bash
  python3 scripts/generate_evaluation_data.py
  ```

#### 2. Failure Analysis - `/api/pgm/failures/{symbol}`
- **Status**: ⚠️ **MOCK DATA ACTIVE**
- **Reason**: Historical data analysis failing
- **Mock Location**: `api/pgm_routes.py::_get_mock_failure_analysis()` (lines 750-833)
- **Test Result**: Returns mock data (3 hardcoded failures, 35 total)
- **Fix**: Ensure historical feature data exists for all symbols

#### 3. Structure Analysis - `/api/pgm/structure-analysis`
- **Status**: ⚠️ **MOCK FALLBACK EXISTS**
- **Reason**: Feature store might be empty
- **Mock Location**: `api/pgm_routes.py::_get_mock_features_df()` (lines 990-1020)
- **Fix**: Populate feature store with real data

---

### ⚠️ FRONTEND MOCK FALLBACKS

**Location**: `frontend/lib/api.ts`

All API methods have try-catch blocks that fall back to mock data on error:

| Method | Mock Function | Lines |
|--------|---------------|-------|
| `getFeatures()` | `getMockFeatures()` | 165-205 |
| `getMarketOverview()` | `getMockMarketOverview()` | 206-224 |
| `getBacktestResults()` | `getMockBacktestResults()` | 225-264 |
| `getInsights()` | `getMockInsights()` | 265-290 |
| `getPGMGraph()` | `getMockPGMGraph()` | 470-505 |
| `getPGMProbabilities()` | `getMockPGMProbabilities()` | 506-518 |
| `getPGMExplanation()` | `getMockPGMExplanation()` | 519-535 |
| `getPGMFeatureImpact()` | `getMockFeatureImpact()` | 536-552 |
| `getPGMEvaluation()` | `getMockEvaluation()` | 553-615 |
| `getPGMFailures()` | `getMockFailures()` | 616-680 |

**Purpose**: Development resilience - prevents UI crashes when backend has issues

**Behavior**: 
- Catches API errors silently
- Returns mock data
- Logs error to console
- User sees data (but it's mock)

---

## 🔧 Action Items to Eliminate Mock Data

### High Priority

1. **Generate Evaluation Data**
   ```bash
   cd /path/to/AlphaForge
   source venv/bin/activate
   python3 scripts/generate_evaluation_data.py --symbols AAPL TSLA GOOGL MSFT
   ```
   - Creates: `data/evaluation/{symbol}_evaluation.json`
   - Eliminates: Mock evaluation data

2. **Fix Feature Store Access**
   - Investigate why `/api/features/AAPL` returns dict instead of list
   - Verify parquet files exist in `data/features/`
   - Check OfflineFeatureStore implementation

3. **Fix Market Overview**
   - Currently returns empty arrays for stocks/signals
   - Check DataService implementation
   - Verify yfinance data fetching

### Medium Priority

4. **Generate Failure Analysis Data**
   - Ensure historical feature data exists
   - Run failure analysis for all symbols
   - Cache results to avoid mock fallback

5. **Add Mock Indicator to Frontend**
   ```typescript
   // Show badge when mock data is displayed
   {isMockData && (
     <Badge variant="warning">Demo Data</Badge>
   )}
   ```

### Low Priority

6. **Remove Frontend Fallbacks** (Production)
   - Replace mock fallbacks with proper error UI
   - Show retry buttons
   - Display meaningful error messages

---

## 📈 Progress Tracking

### Completed ✅
- [x] Market Overview endpoint (real data integration)
- [x] Stock Features endpoint (real data integration)
- [x] Backtesting endpoint (real data integration)
- [x] Insights endpoint (real data integration)
- [x] All PGM prediction endpoints (already real)
- [x] Baseline comparison (precomputed data)
- [x] Calibration (precomputed data)
- [x] Discretization (real config)

### In Progress ⚠️
- [ ] Model Evaluation (mock fallback active)
- [ ] Failure Analysis (mock fallback active)
- [ ] Structure Analysis (mock fallback exists)

### Pending 📋
- [ ] Frontend mock indicators
- [ ] Generate evaluation data for all symbols
- [ ] Fix feature store access issues
- [ ] Fix market overview empty data

---

## 🧪 Testing Commands

### Test Real Data Endpoints
```bash
# Market Overview
curl http://localhost:8000/api/market-overview | jq

# Features
curl http://localhost:8000/api/features/AAPL | jq

# Backtesting
curl 'http://localhost:8000/api/backtest/rsi?ticker=AAPL' | jq

# Insights
curl http://localhost:8000/api/insights | jq

# PGM Predictions
curl http://localhost:8000/api/pgm/probabilities/AAPL | jq
```

### Test Mock Fallback Endpoints
```bash
# Evaluation (currently returns mock)
curl http://localhost:8000/api/pgm/evaluation/AAPL | jq '.n_samples'
# Should return: 100 (mock data)

# Failure Analysis (currently returns mock)
curl http://localhost:8000/api/pgm/failures/AAPL | jq '.summary.total_failures'
# Should return: 35 (mock data)
```

---

## 📝 Conclusion

**Overall Status**: 🟡 Mostly Real Data

- **8/11 backend endpoints** use 100% real data
- **3/11 backend endpoints** have mock fallbacks (2 active, 1 dormant)
- **Frontend** has mock fallbacks for all endpoints (development safety)

**Primary Issues**:
1. Evaluation data not generated → Mock data returned
2. Failure analysis not working → Mock data returned
3. Some data fetch issues (empty arrays) → Need investigation

**Next Step**: Run evaluation script to eliminate the main mock data source.
