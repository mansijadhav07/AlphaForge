# AlphaForge - Clean Project Structure 📁

## Overview

This document shows the organized folder structure of AlphaForge after reorganization.

## Root Directory

```
AlphaForge/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 .gitignore                   # Git ignore rules
├── 📄 requirements.txt             # Python dependencies
├── 📄 Makefile                     # Build automation
├── 📄 api_server.py                # FastAPI server entry point
├── 📄 main.py                      # Alternative entry point
│
├── 📁 docs/                        # 📚 Documentation (organized)
├── 📁 scripts/                     # 🔧 Example scripts
├── 📁 tests/                       # 🧪 Unit tests
│
├── 📁 pgm_model/                   # 🧠 PGM Core AI
├── 📁 api/                         # 🔌 FastAPI Backend
├── 📁 frontend/                    # ⚛️ Next.js Frontend
│
├── 📁 feature_engineering/         # ⚙️ Feature computation
├── 📁 feature_store/               # 💾 Storage management
├── 📁 data_ingestion/              # 📥 Data fetching
├── 📁 data_validation/             # 🔍 Data quality
├── 📁 backtesting/                 # 🧪 Strategy testing
├── 📁 analytics/                   # 📊 Analysis tools
├── 📁 pipelines/                   # 🔄 Data pipelines
├── 📁 dashboard/                   # 📊 Streamlit (legacy)
├── 📁 utils/                       # 🛠️ Utilities
├── 📁 config/                      # ⚙️ Configuration
│
├── 📁 data/                        # 💾 Data storage (gitignored)
└── 📁 logs/                        # 📝 Log files (gitignored)
```

## Detailed Structure

### 📚 Documentation (`docs/`)

```
docs/
├── README.md                       # Documentation index
│
├── setup/                          # Installation & setup
│   ├── INSTALLATION.md            # Complete setup guide
│   └── QUICKSTART.md              # Quick start guide
│
├── overview/                       # Project overview
│   ├── PROJECT_ANALYSIS.md        # Complete analysis
│   ├── PROJECT_SUMMARY.md         # High-level summary
│   └── FEATURES.md                # Feature list
│
├── architecture/                   # System design
│   └── ARCHITECTURE.md            # Architecture overview
│
├── pgm/                           # PGM documentation
│   ├── WHAT_IS_PGM.md            # Introduction
│   ├── PGM_DOCUMENTATION.md      # Complete guide
│   ├── PGM_INTEGRATION_GUIDE.md  # Integration steps
│   ├── PGM_MODULE_SUMMARY.md     # Module overview
│   └── PGM_COMPLETION_REPORT.md  # Implementation report
│
├── features/                      # Feature documentation
│   ├── PGM_GRAPH_SUMMARY.md      # Graph visualization
│   ├── FEATURE_CONTRIBUTION_COMPLETE.md  # Feature impact
│   ├── MODEL_EVALUATION_COMPLETE.md      # Model evaluation
│   └── FAILURE_ANALYSIS_COMPLETE.md      # Failure analysis
│
└── performance/                   # Performance docs
    └── PERFORMANCE_FIXES.md       # Optimizations
```

### 🔧 Scripts (`scripts/`)

```
scripts/
├── example_workflow.py            # General workflow example
├── example_pgm_workflow.py        # PGM workflow example
└── demo_pgm.py                    # PGM demo script
```

### 🧪 Tests (`tests/`)

```
tests/
├── __init__.py
├── test_pgm_module.py             # PGM module tests
├── test_ingestion.py              # Data ingestion tests
└── ...                            # More test files
```

### 🧠 PGM Model (`pgm_model/`)

```
pgm_model/
├── __init__.py
├── state_encoding.py              # Continuous → Discrete
├── graph_structure.py             # Bayesian Network DAG
├── probability_learning.py        # CPT learning
├── inference_engine.py            # Probabilistic inference
├── explanation_engine.py          # Human explanations
├── scenario_simulator.py          # What-if analysis
├── evaluation.py                  # Model evaluation
├── failure_analysis.py            # Failure analysis
└── utils.py                       # Utilities
```

### 🔌 API (`api/`)

```
api/
├── __init__.py
├── pgm_routes.py                  # PGM endpoints (10)
├── market_routes.py               # Market endpoints (4)
├── schemas.py                     # Pydantic models
└── dependencies.py                # Shared dependencies
```

### ⚛️ Frontend (`frontend/`)

```
frontend/
├── app/                           # Next.js pages (9)
│   ├── page.tsx                   # Home (splash)
│   ├── layout.tsx                 # Root layout
│   ├── globals.css                # Global styles
│   ├── dashboard/                 # Market dashboard
│   ├── stock/[symbol]/            # Stock detail
│   ├── backtesting/               # Backtesting
│   ├── insights/                  # Insights
│   ├── pgm-graph/                 # PGM graph
│   ├── feature-impact/            # Feature impact
│   ├── model-evaluation/          # Model evaluation
│   └── model-failures/            # Failure analysis
│
├── components/                    # React components (30+)
│   ├── ui/                        # Base UI (8)
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── animated-card.tsx
│   │   ├── stat-card.tsx
│   │   ├── skeleton-loader.tsx
│   │   ├── insight-card.tsx
│   │   ├── regime-indicator.tsx
│   │   └── feature-badge.tsx
│   ├── charts/                    # Charts (6)
│   │   ├── price-chart.tsx
│   │   ├── indicator-chart.tsx
│   │   ├── equity-curve-chart.tsx
│   │   ├── feature-impact-chart.tsx
│   │   ├── confusion-matrix.tsx
│   │   └── calibration-curve.tsx
│   ├── pgm/                       # PGM components
│   │   └── network-graph.tsx
│   └── layout/                    # Layout
│       └── navbar.tsx
│
├── lib/                           # Utilities
│   ├── api.ts                     # API service
│   ├── utils.ts                   # Helper functions
│   └── config.ts                  # Configuration
│
├── public/                        # Static assets
├── README.md                      # Frontend docs
├── SETUP_GUIDE.md                 # Setup guide
├── PREMIUM_UI_COMPLETE.md         # UI guide
├── PERFORMANCE_GUIDE.md           # Performance guide
├── package.json                   # Dependencies
├── tsconfig.json                  # TypeScript config
├── tailwind.config.ts             # Tailwind config
└── next.config.js                 # Next.js config
```

### ⚙️ Feature Engineering (`feature_engineering/`)

```
feature_engineering/
├── __init__.py
└── features.py                    # 50+ technical indicators
```

### 💾 Feature Store (`feature_store/`)

```
feature_store/
├── __init__.py
├── offline_store.py               # Parquet storage
└── online_store.py                # Redis storage
```

### 📥 Data Ingestion (`data_ingestion/`)

```
data_ingestion/
├── __init__.py
└── ingestion.py                   # yfinance integration
```

### 🔍 Data Validation (`data_validation/`)

```
data_validation/
├── __init__.py
└── validator.py                   # Data quality checks
```

### 🧪 Backtesting (`backtesting/`)

```
backtesting/
├── __init__.py
├── backtest_engine.py             # Backtesting engine
└── strategies.py                  # Trading strategies
```

### 📊 Analytics (`analytics/`)

```
analytics/
├── __init__.py
└── analyzer.py                    # Analysis tools
```

### 🔄 Pipelines (`pipelines/`)

```
pipelines/
├── __init__.py
├── batch_pipeline.py              # Batch processing
└── streaming_pipeline.py          # Streaming simulation
```

### 🛠️ Utilities (`utils/`)

```
utils/
├── __init__.py
├── logger.py                      # Logging setup
└── helpers.py                     # Helper functions
```

### ⚙️ Configuration (`config/`)

```
config/
├── __init__.py
└── config.yaml                    # Configuration file
```

### 💾 Data Storage (`data/`) - Gitignored

```
data/
├── raw/                           # Raw market data
│   ├── AAPL_*.parquet
│   └── TSLA_*.parquet
├── features/                      # Computed features
│   └── offline/
│       ├── example_features/
│       └── market_features/
├── validated/                     # Validated data
├── analytics/                     # Analysis outputs
│   ├── correlation_heatmap.png
│   ├── feature_importance.png
│   └── pgm_graph_structure.png
└── backtesting/                   # Backtest results
    ├── *_Strategy_history.parquet
    ├── *_Strategy_metrics.txt
    └── *_Strategy_trades.csv
```

## File Count Summary

```
📁 Total Folders:     25+
📄 Python Files:      40+
📄 TypeScript Files:  60+
📄 Documentation:     20+
📄 Config Files:      10+
───────────────────────────
📊 Total Files:       130+
```

## Key Benefits of This Structure

✅ **Organized Documentation** - All docs in `docs/` folder  
✅ **Clear Separation** - Code, docs, tests, scripts separated  
✅ **Easy Navigation** - Logical folder hierarchy  
✅ **Scalable** - Easy to add new modules  
✅ **Professional** - Industry-standard structure  
✅ **IDE Friendly** - Better autocomplete and search  
✅ **Git Friendly** - Cleaner diffs and history  

## Quick Access

### Want to...

**Read documentation?**
→ Go to `docs/` folder

**Run examples?**
→ Go to `scripts/` folder

**Run tests?**
→ Go to `tests/` folder

**Work on backend?**
→ Go to `api/` or `pgm_model/`

**Work on frontend?**
→ Go to `frontend/`

**Check data?**
→ Go to `data/` folder

## Navigation Tips

### VS Code
- Use `Cmd+P` (Mac) or `Ctrl+P` (Windows) to quickly find files
- Use folder icons to identify module types
- Collapse folders you're not working on

### Terminal
```bash
# List documentation
ls docs/

# List scripts
ls scripts/

# List tests
ls tests/

# Find a file
find . -name "*.py" | grep pgm
```

### Git
```bash
# See what changed in docs
git diff docs/

# See what changed in frontend
git diff frontend/
```

---

**This structure makes AlphaForge professional, maintainable, and easy to navigate! 🎉**
