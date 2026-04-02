# AlphaForge - Project Structure

## Overview

AlphaForge follows a clean, minimal, production-ready architecture with clear separation of concerns:

```
AlphaForge/
├── backend/              # All backend logic
│   ├── api/             # FastAPI routes and endpoints
│   ├── services/        # Business logic and services
│   ├── models/          # ML models (PGM, analytics, backtesting)
│   └── pipelines/       # Data processing pipelines
│
├── frontend/            # Next.js 14 application
│   ├── app/            # Pages (App Router)
│   ├── components/     # React components
│   └── lib/            # Frontend utilities
│
├── data/                # Data layer
│   ├── ingestion/       # Data fetching from external sources
│   ├── validation/      # Data quality checks
│   ├── features/        # Feature store (offline/online)
│   ├── raw/            # Raw market data (gitignored)
│   └── processed/      # Processed features (gitignored)
│
├── tests/              # Unit and integration tests
├── utils/              # Shared utilities (logger, helpers)
├── config/             # Configuration files
└── docs/               # Documentation
    └── examples/       # Example usage scripts
```

## Folder Details

### backend/

All backend application logic organized by function:

- **api/** - FastAPI routes, schemas, and dependencies
  - `pgm_routes.py` - PGM prediction endpoints
  - `market_routes.py` - Market data endpoints
  - `discretization_routes.py` - Discretization endpoints
  - `dependencies.py` - Shared dependencies and service initialization
  - `schemas.py` - Pydantic models for request/response

- **services/** - Business logic layer
  - `data_service.py` - Data fetching and caching
  - `cache_service.py` - Redis and in-memory caching

- **pipelines/** - Data processing orchestration
  - `batch_pipeline.py` - Historical data processing
  - `streaming_pipeline.py` - Real-time data processing

- **models/** - All ML and analytics models (19 modules)
  - PGM modules: state_encoding, graph_structure, inference_engine, etc.
  - `analyzer.py` - Analytics engine
  - `features.py` - Feature engineering
  - `backtest_engine.py` - Backtesting engine
  - `strategies.py` - Trading strategies
  - `baseline_models.py` - Baseline model comparisons

### frontend/

Next.js 14 application with modern React patterns:

- **app/** - Pages using App Router
  - `dashboard/` - Main dashboard
  - `stock/[symbol]/` - Individual stock analysis
  - `pgm-graph/` - Bayesian network visualization
  - `feature-impact/` - Feature importance
  - `model-evaluation/` - Model metrics
  - `calibration/` - Probability calibration
  - `baseline-comparison/` - Model comparison
  - `discretization/` - Feature discretization
  - `structure-analysis/` - Dependency analysis
  - `insights/` - AI insights
  - `backtesting/` - Strategy backtesting

- **components/** - Reusable React components
  - `ui/` - Base UI components
  - `charts/` - Chart components (Recharts)
  - `layout/` - Layout components (navbar, etc.)
  - `pgm/` - PGM-specific components

- **lib/** - Frontend utilities
  - `api.ts` - API client
  - `utils.ts` - Helper functions

### data/

Data layer with clear separation:

- **ingestion/** - Fetch data from yfinance and other sources
- **validation/** - Data quality checks and validation rules
- **features/** - Feature store implementation
  - `offline_store.py` - Parquet-based offline storage
  - `online_store.py` - Redis-based online storage
- **raw/** - Raw market data (OHLCV) - gitignored
- **processed/** - Computed features ready for ML - gitignored
  - `analytics/` - Analytics results
  - `backtesting/` - Backtest results
  - `calibration/` - Calibration data
  - `evaluation/` - Model evaluation results
  - `failures/` - Failure analysis data
  - `pgm_model/` - Trained PGM models

### Other Directories

- **tests/** - All unit and integration tests
- **utils/** - Shared utilities (logger, helpers)
- **config/** - Configuration files (config.yaml)
- **docs/** - Comprehensive documentation
  - `examples/` - Example usage scripts (moved from root)
  - `features/` - Feature documentation
  - `architecture/` - Architecture docs
  - `pgm/` - PGM documentation
  - `setup/` - Setup guides

## Root Files

Only essential files in root:
- `api_server.py` - FastAPI server entry point
- `main.py` - CLI entry point
- `README.md` - Main documentation
- `INSTALLATION.md` - Installation guide
- `PROJECT_STRUCTURE.md` - This file
- `requirements.txt` - Python dependencies
- `setup.py` - Package setup
- `Makefile` - Build automation
- `.gitignore` - Git ignore rules

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    External Data Sources                     │
│                      (yfinance API)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  data/ingestion/                             │
│              Fetch OHLCV market data                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  data/validation/                            │
│         Validate data quality and completeness               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              backend/models/features.py                      │
│        Compute 50+ technical indicators                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  data/features/                              │
│         Store features (Parquet + Redis)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  backend/models/                             │
│         PGM Training and Inference                           │
│  • State Encoding  • Graph Structure                         │
│  • Probability Learning  • Inference                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  backend/api/                                │
│              REST API Endpoints                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    frontend/                                 │
│         Next.js UI with visualizations                       │
└─────────────────────────────────────────────────────────────┘
```

## Import Patterns

### Backend Modules
```python
# PGM models
from backend.models.state_encoding import StateEncoder
from backend.models.inference_engine import InferenceEngine

# Services
from backend.services.cache_service import get_cache_service
from backend.services.data_service import DataService

# API
from backend.api.dependencies import get_pgm_service
from backend.api.schemas import PredictionRequest
```

### Data Modules
```python
# Data ingestion
from data.ingestion.ingestion import DataIngestion

# Data validation
from data.validation.validator import DataValidator

# Feature store
from data.features.offline_store import OfflineFeatureStore
from data.features.online_store import OnlineFeatureStore
```

### Pipelines
```python
# Pipelines
from backend.pipelines.batch_pipeline import BatchPipeline
from backend.pipelines.streaming_pipeline import StreamingPipeline
```

## Benefits of This Structure

1. **Minimal Root**: Only 8 files in root directory
2. **Clear Hierarchy**: 7 main folders with logical grouping
3. **Separation of Concerns**: Backend, data, and frontend are distinct
4. **Easy Navigation**: Less folder jumping, clearer hierarchy
5. **Production-Ready**: Follows industry best practices
6. **Scalable**: Easy to add new features within existing structure
7. **Clean**: No clutter, no unnecessary folders

## Comparison

### Before Refactoring
- 15+ top-level folders
- Fragmented structure
- Unclear organization
- Hard to navigate

### After Refactoring
- 7 main folders (backend, frontend, data, tests, utils, config, docs)
- Clear separation of concerns
- Logical grouping
- Easy to navigate
- Production-ready

## Migration Notes

All imports have been automatically updated. The application functionality remains identical - only the folder structure has changed.

Key changes:
- `examples/` → `docs/examples/`
- `data/validated/` → `data/processed/`
- `data/pgm_model/` → `data/processed/pgm_model/`
- All other data subdirectories → `data/processed/`

## Verification

Run the verification script to ensure everything is working:

```bash
python3 scripts/verify_structure.py
```

Expected output:
- ✅ All imports working (9/9 passed)
- ✅ Directory structure correct (15/15 passed)
- ✅ Old directories removed (11/11 removed)
