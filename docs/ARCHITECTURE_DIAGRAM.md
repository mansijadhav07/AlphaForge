# AlphaForge – Layered System Architecture
## Explainable AI Trading Platform

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ALPHAFORGE - LAYERED SYSTEM ARCHITECTURE                    ║
║                   Explainable AI Financial Intelligence Platform               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 1: CLIENT / PRESENTATION LAYER                       │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  👤 User Interface (Browser)                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Next.js 14 Frontend (React + TypeScript)                               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │ │
│  │  │  Dashboard   │  │  Stock Page  │  │   Insights   │  │ Backtesting│ │ │
│  │  │  • Charts    │  │  • Prices    │  │  • AI Tips   │  │ • Results  │ │ │
│  │  │  • Stats     │  │  • Signals   │  │  • Warnings  │  │ • Metrics  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │ │
│  │                                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │ │
│  │  │  PGM Graph   │  │ Calibration  │  │  Evaluation  │  │  Baseline  │ │ │
│  │  │  • Network   │  │  • Curves    │  │  • Metrics   │  │ • Compare  │ │ │
│  │  │  • Nodes     │  │  • Bins      │  │  • Confusion │  │ • Models   │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │ │
│  │                                                                          │ │
│  │  Rendering: SSR (Server-Side) + CSR (Client-Side)                       │ │
│  │  Animations: Framer Motion | Charts: Recharts | Icons: Lucide React    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  📡 API Client Layer                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • fetch() / axios for HTTP requests                                    │ │
│  │  • Auto-refresh (30s-60s intervals)                                     │ │
│  │  • Error handling & retry logic                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │ HTTPS / REST API
                                    │ JSON Request/Response
┌───────────────────────────────────▼───────────────────────────────────────────┐
│                      LAYER 2: API GATEWAY LAYER                                │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  🌐 FastAPI Backend (Python 3.10+)                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  REST API Endpoints                                                      │ │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐ │ │
│  │  │  /api/pgm/*        │  │  /api/market/*     │  │ /api/discretize  │ │ │
│  │  │  • probabilities   │  │  • historical      │  │  • demo          │ │ │
│  │  │  • explanation     │  │  • live            │  │  • compare       │ │ │
│  │  │  • signal          │  │  • overview        │  └──────────────────┘ │ │
│  │  │  • evaluation      │  │  • insights        │                        │ │
│  │  │  • calibration     │  └────────────────────┘                        │ │
│  │  │  • baseline        │                                                 │ │
│  │  │  • failures        │                                                 │ │
│  │  └────────────────────┘                                                 │ │
│  │                                                                          │ │
│  │  Middleware Stack:                                                       │ │
│  │  • CORS (Cross-Origin Resource Sharing)                                 │ │
│  │  • Request Validation (Pydantic schemas)                                │ │
│  │  • Authentication & Authorization (JWT - Future)                        │ │
│  │  • Rate Limiting (Token bucket - Future)                                │ │
│  │  • Error Handling (structured responses)                                │ │
│  │  • API Documentation (OpenAPI/Swagger)                                  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼───────────────────────────────────────────┐
│                 LAYER 3: SERVICE / BUSINESS LOGIC LAYER                        │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ⚙️  Core Services                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  ┌──────────────────────┐         ┌──────────────────────┐             │ │
│  │  │   Data Service       │         │   Cache Service      │             │ │
│  │  │  • Fetch market data │         │  • Redis cache       │             │ │
│  │  │  • Manage features   │         │  • In-memory cache   │             │ │
│  │  │  • CRUD operations   │         │  • TTL management    │             │ │
│  │  │  • Data validation   │         │  • Cache warming     │             │ │
│  │  └──────────────────────┘         └──────────────────────┘             │ │
│  │                                                                          │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │   Pipeline Manager                                                │  │ │
│  │  │  ┌─────────────────────┐      ┌─────────────────────┐           │  │ │
│  │  │  │  Batch Pipeline     │      │ Streaming Pipeline  │           │  │ │
│  │  │  │  • Historical data  │      │  • Real-time data   │           │  │
│  │  │  │  • Feature compute  │      │  • Live updates     │           │  │
│  │  │  │  • Model training   │      │  • Incremental      │           │  │
│  │  │  └─────────────────────┘      └─────────────────────┘           │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                          │ │
│  │  Orchestration: Coordinate between data, cache, and model layers        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼───────────────────────────────────────────┐
│              ⭐ LAYER 4: MODEL / AI LAYER (CORE INTELLIGENCE) ⭐               │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  🤖 Feature Engineering Module                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Technical Indicators (50+ features)                                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │ │
│  │  │  Momentum    │  │    Trend     │  │  Volatility  │  │   Volume   │ │ │
│  │  │  • RSI       │  │  • SMA/EMA   │  │  • Bollinger │  │  • OBV     │ │ │
│  │  │  • MACD      │  │  • ADX       │  │  • ATR       │  │  • Vol SMA │ │ │
│  │  │  • Stochastic│  │  • Trend     │  │  • Std Dev   │  │  • Ratio   │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │ │
│  │                                                                          │ │
│  │  Custom Features: Momentum Score, Regime Detection, Trend Slope         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  🧠 PGM Core (Probabilistic Graphical Model) - Bayesian Network              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐│ │
│  │  │  1. State Encoding Module                                          ││ │
│  │  │     • Convert continuous features → discrete states                ││ │
│  │  │     • Learn optimal thresholds (quantile-based)                    ││ │
│  │  │     • Example: RSI → {oversold, neutral, overbought}               ││ │
│  │  └────────────────────────────────────────────────────────────────────┘│ │
│  │                              ↓                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐│ │
│  │  │  2. Graph Structure (Bayesian Network DAG)                         ││ │
│  │  │     • 11 nodes (features + target)                                 ││ │
│  │  │     • 13 edges (dependencies)                                      ││ │
│  │  │     • Causal relationships: RSI → Momentum → Regime → Return      ││ │
│  │  └────────────────────────────────────────────────────────────────────┘│ │
│  │                              ↓                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐│ │
│  │  │  3. Probability Learning                                           ││ │
│  │  │     • Learn Conditional Probability Tables (CPTs)                  ││ │
│  │  │     • P(Node | Parents) for each node                              ││ │
│  │  │     • Laplace smoothing (alpha=1.0)                                ││ │
│  │  └────────────────────────────────────────────────────────────────────┘│ │
│  │                              ↓                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐│ │
│  │  │  4. Inference Engine                                               ││ │
│  │  │     • Variable Elimination algorithm                               ││ │
│  │  │     • Query: P(Future_Return | Current_Features)                   ││ │
│  │  │     • Output: {positive: 0.45, neutral: 0.35, negative: 0.20}     ││ │
│  │  └────────────────────────────────────────────────────────────────────┘│ │
│  │                              ↓                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐│ │
│  │  │  5. Explanation Engine (Explainable AI)                            ││ │
│  │  │     • Feature impact analysis                                      ││ │
│  │  │     • Human-readable explanations                                  ││ │
│  │  │     • Key factors: "Strong bullish momentum (RSI=65, +15%)"        ││ │
│  │  └────────────────────────────────────────────────────────────────────┘│ │
│  │                              ↓                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐│ │
│  │  │  6. Scenario Simulator                                             ││ │
│  │  │     • What-if analysis                                             ││ │
│  │  │     • Sensitivity testing                                          ││ │
│  │  │     • "What if RSI drops to 30?"                                   ││ │
│  │  └────────────────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  📊 Evaluation & Analysis Modules                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐ │ │
│  │  │  Model Eval      │  │  Calibration     │  │  Baseline Compare    │ │ │
│  │  │  • Accuracy      │  │  • Reliability   │  │  • PGM vs LR         │ │ │
│  │  │  • Precision     │  │  • ECE score     │  │  • PGM vs Random     │ │ │
│  │  │  • Recall        │  │  • Brier score   │  │  • PGM vs Majority   │ │ │
│  │  │  • F1 Score      │  │  • Calibration   │  │  • Winner selection  │ │ │
│  │  │  • Confusion     │  │    curves        │  │                      │ │ │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────────┘ │ │
│  │                                                                          │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐ │ │
│  │  │ Failure Analysis │  │  Discretization  │  │  Structure Analysis  │ │ │
│  │  │  • Error cases   │  │  • Binning       │  │  • Dependencies      │ │ │
│  │  │  • Patterns      │  │  • Methods       │  │  • Markov blanket    │ │ │
│  │  │  • Improvements  │  │  • Comparison    │  │  • D-separation      │ │ │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  📈 Backtesting Engine                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Strategy execution on historical data                                │ │
│  │  • Performance metrics: Sharpe Ratio, Max Drawdown, Win Rate            │ │
│  │  • Equity curve generation                                              │ │
│  │  • Trade-by-trade analysis                                              │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼───────────────────────────────────────────┐
│                     LAYER 5: DATA ACCESS LAYER                                 │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  📥 Data Ingestion                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  yfinance API Integration                                                │ │
│  │  • Fetch OHLCV data (Open, High, Low, Close, Volume)                    │ │
│  │  • Historical data (configurable date range)                             │ │
│  │  • Real-time/latest prices                                               │ │
│  │  • Multiple symbols (AAPL, TSLA, GOOGL, MSFT, etc.)                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ✅ Data Validation                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Completeness checks (no missing dates)                                │ │
│  │  • Range validation (prices > 0, volume >= 0)                            │ │
│  │  • Anomaly detection (outliers, spikes)                                  │ │
│  │  • Data quality scoring                                                  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  💾 Feature Store                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  ┌──────────────────────────┐         ┌──────────────────────────┐     │ │
│  │  │  Offline Store           │         │  Online Store            │     │ │
│  │  │  • Parquet files         │         │  • Redis cache           │     │ │
│  │  │  • Columnar format       │         │  • Low latency           │     │ │
│  │  │  • Historical features   │         │  • Real-time features    │     │ │
│  │  │  • Batch access          │         │  • Key-value store       │     │ │
│  │  └──────────────────────────┘         └──────────────────────────┘     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  📂 File I/O System                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Read/Write Parquet files (pandas)                                     │ │
│  │  • JSON serialization (configs, results)                                 │ │
│  │  • Pickle serialization (model artifacts)                                │ │
│  │  • Logging (structured JSON logs)                                        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼───────────────────────────────────────────┐
│                        LAYER 6: STORAGE LAYER                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  💿 File Storage                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  data/                                                                   │ │
│  │  ├── raw/                    # Raw OHLCV data                            │ │
│  │  │   └── {symbol}_raw.parquet                                           │ │
│  │  │                                                                       │ │
│  │  ├── processed/              # Processed data & results                 │ │
│  │  │   ├── {symbol}_validated.parquet                                     │ │
│  │  │   ├── features/           # Feature store (offline)                  │ │
│  │  │   ├── pgm_model/          # Trained models (CPTs, configs)           │ │
│  │  │   ├── evaluation/         # Model metrics                            │ │
│  │  │   ├── calibration/        # Calibration data                         │ │
│  │  │   ├── baseline_comparison/ # Model comparison results                │ │
│  │  │   └── failures/           # Failure analysis                         │ │
│  │  │                                                                       │ │
│  │  └── logs/                   # Application logs                         │ │
│  │      ├── app_YYYY-MM-DD.log                                             │ │
│  │      └── error_YYYY-MM-DD.log                                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  🔴 Redis Cache (In-Memory)                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Multi-Layer Caching Strategy:                                           │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  Key Pattern: {namespace}:{symbol}:{data_type}                   │  │ │
│  │  │                                                                   │  │ │
│  │  │  • market:AAPL:live           → Latest price (TTL: 30s)          │  │ │
│  │  │  • market:AAPL:historical     → Full dataset (TTL: 1h)           │  │ │
│  │  │  • pgm:AAPL:probabilities     → Predictions (TTL: 30s)           │  │ │
│  │  │  • market:overview             → Market summary (TTL: 60s)       │  │ │
│  │  │  • cache:stats                 → Cache statistics                │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                          │ │
│  │  Fallback: In-memory Python dict (if Redis unavailable)                 │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  📦 Model Artifacts                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • encoder_config.json    → State encoding thresholds                   │ │
│  │  • graph_structure.json   → Bayesian Network DAG                        │ │
│  │  • cpts.pkl               → Conditional Probability Tables              │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼───────────────────────────────────────────┐
│              LAYER 7: INFRASTRUCTURE LAYER (Production)                        │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  🌐 Load Balancer                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  NGINX / AWS Application Load Balancer (ALB)                            │ │
│  │  • SSL/TLS termination                                                   │ │
│  │  • Request routing                                                       │ │
│  │  • Health checks                                                         │ │
│  │  • Rate limiting                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  🖥️  Backend Cluster                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Multiple FastAPI Instances (Horizontal Scaling)                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │ │
│  │  │  Instance 1  │  │  Instance 2  │  │  Instance N  │                 │ │
│  │  │  Port 8000   │  │  Port 8001   │  │  Port 800N   │                 │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                 │ │
│  │  • Auto-scaling based on load                                           │ │
│  │  • Health monitoring                                                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  🔴 Redis Cluster                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Master-Replica setup                                                  │ │
│  │  • High availability                                                     │ │
│  │  • Automatic failover                                                    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ☁️  Cloud Storage                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  AWS S3 / Google Cloud Storage / Azure Blob                             │ │
│  │  • Parquet files backup                                                  │ │
│  │  • Model artifacts versioning                                            │ │
│  │  • Log archival                                                          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════════════════╗
║                            DATA FLOW SUMMARY                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

User Request → Frontend (Next.js) → API Gateway (FastAPI) → Cache Check (Redis)
                                                                    │
                                                    ┌───────────────┴───────────┐
                                                    │                           │
                                                Cache Hit                   Cache Miss
                                                    │                           │
                                            Return Cached                       │
                                                    │                           ▼
                                                    │              Data Service → Feature Store
                                                    │                           │
                                                    │                           ▼
                                                    │              PGM Pipeline (6 steps)
                                                    │              1. State Encoding
                                                    │              2. Graph Structure
                                                    │              3. Probability Learning
                                                    │              4. Inference
                                                    │              5. Explanation
                                                    │              6. Signal Generation
                                                    │                           │
                                                    │                           ▼
                                                    │              Cache Result (30s TTL)
                                                    │                           │
                                                    └───────────────┬───────────┘
                                                                    │
                                                            Return JSON Response
                                                                    │
                                                                    ▼
                                                            Frontend Display
                                                            • Prediction
                                                            • Explanation
                                                            • Charts

╔═══════════════════════════════════════════════════════════════════════════════╗
║                          KEY DESIGN PRINCIPLES                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

1. EXPLAINABILITY FIRST
   Every prediction includes human-readable explanations
   Feature impact analysis shows "why" behind predictions

2. LAYERED ARCHITECTURE
   Clear separation of concerns across 7 layers
   Each layer has well-defined responsibilities

3. CACHING STRATEGY
   Multi-layer cache (Browser → Redis → Memory → Disk)
   Smart TTL based on data volatility (30s-1h)

4. SCALABILITY
   Horizontal scaling at API and cache layers
   Stateless backend instances
   Load balancer for traffic distribution

5. PERFORMANCE
   Target: <100ms API response (cached), <500ms (uncached)
   Parquet for fast columnar data access
   Redis for sub-millisecond cache lookups

6. MODULARITY
   19 PGM modules with single responsibility
   Pluggable components (easy to swap/upgrade)
   Clean interfaces between layers

7. OBSERVABILITY
   Structured logging (JSON format)
   Performance metrics tracking
   Error monitoring and alerting

╔═══════════════════════════════════════════════════════════════════════════════╗
║                          TECHNOLOGY STACK SUMMARY                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Frontend:    Next.js 14, React 18, TypeScript, Tailwind CSS, Framer Motion
Backend:     Python 3.10+, FastAPI, Uvicorn, Pydantic
AI/ML:       pgmpy, scikit-learn, pandas, numpy, ta (technical analysis)
Data:        yfinance (market data), Parquet (storage), Redis (cache)
Deployment:  Docker, NGINX, AWS/GCP/Azure (cloud infrastructure)

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              PERFORMANCE METRICS                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

API Response Time:
• Cached:           < 100ms  ✓
• Uncached:         < 500ms  ✓
• Model Inference:  < 50ms   ✓

Frontend Performance:
• First Load:       < 2s (FCP)  ✓
• Page Transition:  < 500ms     ✓
• Animation FPS:    60fps       ✓

Cache Performance:
• Hit Rate:         > 80%       ✓
• Redis Latency:    < 1ms       ✓
• TTL Strategy:     30s-1h      ✓

Model Performance:
• Accuracy:         65-70%      ✓
• Brier Score:      0.15-0.20   ✓
• Inference Speed:  < 10ms      ✓

═══════════════════════════════════════════════════════════════════════════════

                        AlphaForge - Explainable AI Trading
                     Built with ❤️ for Quantitative Traders

═══════════════════════════════════════════════════════════════════════════════
```
