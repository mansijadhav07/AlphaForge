# AlphaForge - System Design Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [API Design](#api-design)
7. [Database Schema](#database-schema)
8. [Security & Performance](#security--performance)
9. [Deployment Architecture](#deployment-architecture)
10. [Future Enhancements](#future-enhancements)

---

## Executive Summary

**AlphaForge** is an AI-powered financial intelligence platform that uses Probabilistic Graphical Models (PGM) to provide explainable stock market predictions and trading signals.

### Key Features
- Real-time market data ingestion and processing
- Bayesian Network-based prediction engine
- Explainable AI with feature impact analysis
- Model evaluation and comparison framework
- Interactive web dashboard with premium UI
- Comprehensive backtesting capabilities

### Design Principles
1. **Explainability First**: All predictions include human-readable explanations
2. **Modular Architecture**: Clear separation of concerns
3. **Scalability**: Designed for horizontal scaling
4. **Performance**: Caching at multiple layers
5. **Maintainability**: Clean code with comprehensive testing

---

## System Architecture

> 📊 **See detailed layered architecture diagram:** [ARCHITECTURE_DIAGRAM.md](./docs/ARCHITECTURE_DIAGRAM.md)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Next.js 14 Frontend (React)                     │  │
│  │  • Server-Side Rendering (SSR)                           │  │
│  │  • Client-Side Rendering (CSR)                           │  │
│  │  • Framer Motion Animations                              │  │
│  │  • Recharts Visualizations                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS/REST API
┌────────────────────────▼────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Server (Python)                      │  │
│  │  • CORS Middleware                                       │  │
│  │  • Request Validation (Pydantic)                         │  │
│  │  • Error Handling                                        │  │
│  │  • API Documentation (OpenAPI)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Services   │  │  Pipelines   │  │    Models    │         │
│  │              │  │              │  │              │         │
│  │ • Data Svc   │  │ • Batch      │  │ • PGM Core   │         │
│  │ • Cache Svc  │  │ • Streaming  │  │ • Analytics  │         │
│  └──────────────┘  └──────────────┘  │ • Backtesting│         │
│                                       └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ yfinance │  │  Redis   │  │ Parquet  │  │  Logs    │       │
│  │   API    │  │  Cache   │  │  Files   │  │  (JSON)  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```


### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER (Frontend)                                │
│ • Next.js App Router                                         │
│ • React Components (UI, Charts, Layout)                      │
│ • Client-side State Management                               │
│ • API Client (fetch/axios)                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ API LAYER (Backend/API)                                      │
│ • REST Endpoints (FastAPI)                                   │
│ • Request/Response Schemas (Pydantic)                        │
│ • Authentication & Authorization                             │
│ • Rate Limiting & Throttling                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ SERVICE LAYER (Backend/Services)                             │
│ • Business Logic                                             │
│ • Data Service (CRUD operations)                             │
│ • Cache Service (Redis + In-Memory)                          │
│ • Orchestration & Coordination                               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ MODEL LAYER (Backend/Models)                                 │
│ • PGM Core (19 modules)                                      │
│ • Feature Engineering                                        │
│ • Analytics Engine                                           │
│ • Backtesting Engine                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ DATA ACCESS LAYER (Data/)                                    │
│ • Data Ingestion (yfinance)                                  │
│ • Data Validation                                            │
│ • Feature Store (Offline/Online)                             │
│ • File I/O (Parquet, JSON)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Frontend Components

#### Component Hierarchy
```
App (Root)
├── Layout
│   ├── Navbar
│   │   └── ModelDropdown
│   └── Footer
├── Pages
│   ├── Dashboard
│   ├── Stock/[symbol]
│   ├── Insights
│   ├── Backtesting
│   ├── PGM Graph
│   ├── Feature Impact
│   ├── Model Evaluation
│   ├── Calibration
│   ├── Baseline Comparison
│   ├── Discretization
│   └── Structure Analysis
└── Shared Components
    ├── UI Components
    │   ├── Card
    │   ├── Badge
    │   ├── StatCard
    │   ├── SkeletonLoader
    │   ├── FullScreenLoader
    │   └── LiveIndicator
    └── Charts
        ├── PriceChart
        ├── IndicatorChart
        ├── EquityCurveChart
        ├── FeatureImpactChart
        ├── CalibrationCurve
        ├── ConfusionMatrix
        └── NetworkGraph
```


### 2. Backend Components

#### API Routes Structure
```
/api
├── /pgm
│   ├── GET  /health                    - Health check
│   ├── GET  /probabilities/{symbol}    - Get predictions
│   ├── GET  /explanation/{symbol}      - Get explanations
│   ├── GET  /signal/{symbol}           - Get trading signal
│   ├── POST /simulate                  - Scenario simulation
│   ├── GET  /feature-impact/{symbol}   - Feature importance
│   ├── GET  /regime/{symbol}           - Market regime
│   ├── GET  /graph                     - Network structure
│   ├── GET  /evaluation/{symbol}       - Model metrics
│   ├── GET  /calibration/{symbol}      - Calibration data
│   ├── GET  /baseline-comparison/{symbol} - Model comparison
│   ├── GET  /failures/{symbol}         - Failure analysis
│   └── GET  /structure-analysis/{symbol} - Dependency analysis
│
├── /market
│   ├── GET  /historical/{symbol}       - Historical data
│   ├── GET  /live/{symbol}             - Live price
│   ├── GET  /overview                  - Market overview
│   ├── GET  /insights                  - AI insights
│   └── GET  /cache/stats               - Cache statistics
│
└── /discretization
    ├── GET  /demo/{feature}            - Discretization demo
    └── GET  /compare                   - Method comparison
```

#### PGM Core Modules (19 modules)
```
backend/models/
├── Core PGM
│   ├── state_encoding.py          - Continuous → Discrete
│   ├── graph_structure.py         - Bayesian Network DAG
│   ├── probability_learning.py    - CPT learning
│   ├── inference_engine.py        - Probabilistic inference
│   ├── explanation_engine.py      - Generate explanations
│   ├── scenario_simulator.py      - What-if analysis
│   └── utils.py                   - PGM utilities
│
├── Evaluation & Analysis
│   ├── evaluation.py              - Model metrics
│   ├── calibration.py             - Probability calibration
│   ├── baseline_models.py         - Model comparison
│   ├── failure_analysis.py        - Error analysis
│   ├── failure_analysis_real.py   - Real failure analysis
│   ├── structure_analysis.py      - Dependency analysis
│   └── discretization.py          - Feature binning
│
├── Feature Engineering
│   ├── features.py                - 50+ indicators
│   └── analyzer.py                - Analytics engine
│
└── Backtesting
    ├── backtest_engine.py         - Backtest framework
    └── strategies.py              - Trading strategies
```


---

## Data Flow

### 1. Real-Time Prediction Flow

```
┌──────────────┐
│   User       │
│  (Browser)   │
└──────┬───────┘
       │ 1. Request prediction for AAPL
       ▼
┌──────────────────────────────────────────┐
│  Frontend (Next.js)                      │
│  api.getProbabilities('AAPL')            │
└──────┬───────────────────────────────────┘
       │ 2. HTTP GET /api/pgm/probabilities/AAPL
       ▼
┌──────────────────────────────────────────┐
│  API Gateway (FastAPI)                   │
│  pgm_routes.get_probabilities()          │
└──────┬───────────────────────────────────┘
       │ 3. Check cache
       ▼
┌──────────────────────────────────────────┐
│  Cache Service                           │
│  Redis (30s TTL) / In-Memory             │
└──────┬───────────────────────────────────┘
       │ 4. Cache miss
       ▼
┌──────────────────────────────────────────┐
│  Data Service                            │
│  Fetch latest market data                │
└──────┬───────────────────────────────────┘
       │ 5. Get OHLCV data
       ▼
┌──────────────────────────────────────────┐
│  Feature Store                           │
│  Load features from Parquet/Redis        │
└──────┬───────────────────────────────────┘
       │ 6. Features ready
       ▼
┌──────────────────────────────────────────┐
│  PGM Model Pipeline                      │
│  ┌────────────────────────────────────┐ │
│  │ 1. State Encoder                   │ │
│  │    Discretize features             │ │
│  └────────┬───────────────────────────┘ │
│           ▼                              │
│  ┌────────────────────────────────────┐ │
│  │ 2. Inference Engine                │ │
│  │    P(Return | Features)            │ │
│  └────────┬───────────────────────────┘ │
│           ▼                              │
│  ┌────────────────────────────────────┐ │
│  │ 3. Explanation Engine              │ │
│  │    Generate reasoning              │ │
│  └────────┬───────────────────────────┘ │
│           ▼                              │
│  ┌────────────────────────────────────┐ │
│  │ 4. Signal Generator                │ │
│  │    BUY/SELL/HOLD                   │ │
│  └────────────────────────────────────┘ │
└──────┬───────────────────────────────────┘
       │ 7. Prediction result
       ▼
┌──────────────────────────────────────────┐
│  Cache Service                           │
│  Store result (30s TTL)                  │
└──────┬───────────────────────────────────┘
       │ 8. Return JSON response
       ▼
┌──────────────────────────────────────────┐
│  Frontend                                │
│  Display prediction + explanation        │
└──────────────────────────────────────────┘
```


### 2. Data Ingestion & Processing Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    BATCH PIPELINE                            │
└─────────────────────────────────────────────────────────────┘

1. DATA INGESTION
   ┌──────────────┐
   │  yfinance    │ ──→ Fetch OHLCV data
   │     API      │     (Historical + Latest)
   └──────┬───────┘
          │
          ▼
   ┌──────────────────────────────────┐
   │  data/raw/                       │
   │  {symbol}_raw.parquet            │
   └──────┬───────────────────────────┘
          │
          ▼
2. DATA VALIDATION
   ┌──────────────────────────────────┐
   │  DataValidator                   │
   │  • Check completeness            │
   │  • Detect anomalies              │
   │  • Validate ranges               │
   └──────┬───────────────────────────┘
          │
          ▼
   ┌──────────────────────────────────┐
   │  data/processed/                 │
   │  {symbol}_validated.parquet      │
   └──────┬───────────────────────────┘
          │
          ▼
3. FEATURE ENGINEERING
   ┌──────────────────────────────────┐
   │  FeatureEngineer                 │
   │  • RSI, MACD, Bollinger Bands    │
   │  • Momentum, Volatility          │
   │  • Regime Detection              │
   │  • 50+ Technical Indicators      │
   └──────┬───────────────────────────┘
          │
          ▼
   ┌──────────────────────────────────┐
   │  Feature Store                   │
   │  ┌────────────┐  ┌────────────┐ │
   │  │  Offline   │  │  Online    │ │
   │  │  (Parquet) │  │  (Redis)   │ │
   │  └────────────┘  └────────────┘ │
   └──────┬───────────────────────────┘
          │
          ▼
4. MODEL TRAINING
   ┌──────────────────────────────────┐
   │  PGM Training Pipeline           │
   │  ┌────────────────────────────┐ │
   │  │ 1. State Encoding          │ │
   │  │    Learn thresholds        │ │
   │  └────────┬───────────────────┘ │
   │           ▼                      │
   │  ┌────────────────────────────┐ │
   │  │ 2. Graph Structure         │ │
   │  │    Build Bayesian Network  │ │
   │  └────────┬───────────────────┘ │
   │           ▼                      │
   │  ┌────────────────────────────┐ │
   │  │ 3. Probability Learning    │ │
   │  │    Learn CPTs from data    │ │
   │  └────────────────────────────┘ │
   └──────┬───────────────────────────┘
          │
          ▼
   ┌──────────────────────────────────┐
   │  data/processed/pgm_model/       │
   │  • encoder_config.json           │
   │  • graph_structure.json          │
   │  • cpts.pkl                      │
   └──────────────────────────────────┘
```


### 3. Caching Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    MULTI-LAYER CACHE                         │
└─────────────────────────────────────────────────────────────┘

Request Flow:
   User Request
        │
        ▼
   ┌─────────────────────────────────┐
   │  L1: Browser Cache              │
   │  • Static assets (CSS, JS)      │
   │  • Images                        │
   │  TTL: 1 hour                     │
   └────────┬────────────────────────┘
            │ Cache miss
            ▼
   ┌─────────────────────────────────┐
   │  L2: Redis Cache                │
   │  • Live prices (30s TTL)        │
   │  • Market overview (60s TTL)    │
   │  • Predictions (30s TTL)        │
   └────────┬────────────────────────┘
            │ Cache miss
            ▼
   ┌─────────────────────────────────┐
   │  L3: In-Memory Cache            │
   │  • Historical data (1h TTL)     │
   │  • Model artifacts              │
   │  • Feature metadata             │
   └────────┬────────────────────────┘
            │ Cache miss
            ▼
   ┌─────────────────────────────────┐
   │  L4: File System                │
   │  • Parquet files                │
   │  • JSON results                 │
   │  • Trained models               │
   └─────────────────────────────────┘

Cache Invalidation:
• Time-based (TTL)
• Event-based (new data arrival)
• Manual (cache clear endpoint)
```

---

## Technology Stack

### Frontend Stack
```
┌─────────────────────────────────────────┐
│ Framework & Libraries                   │
├─────────────────────────────────────────┤
│ • Next.js 14 (App Router)               │
│ • React 18                              │
│ • TypeScript                            │
│ • Tailwind CSS                          │
│ • Framer Motion (animations)           │
│ • Recharts (visualizations)            │
│ • Lucide React (icons)                 │
│ • D3.js (network graphs)               │
└─────────────────────────────────────────┘
```

### Backend Stack
```
┌─────────────────────────────────────────┐
│ Framework & Libraries                   │
├─────────────────────────────────────────┤
│ • Python 3.10+                          │
│ • FastAPI (REST API)                    │
│ • Pydantic (validation)                 │
│ • Uvicorn (ASGI server)                 │
│ • pgmpy (Bayesian Networks)            │
│ • scikit-learn (ML)                     │
│ • pandas (data processing)              │
│ • numpy (numerical computing)           │
│ • ta (technical analysis)               │
│ • yfinance (market data)                │
│ • redis (caching)                       │
└─────────────────────────────────────────┘
```

### Data & Storage
```
┌─────────────────────────────────────────┐
│ Storage Solutions                       │
├─────────────────────────────────────────┤
│ • Parquet (columnar storage)            │
│ • Redis (in-memory cache)               │
│ • JSON (configuration & results)        │
│ • Pickle (model serialization)          │
└─────────────────────────────────────────┘
```


---

## API Design

### RESTful API Principles

1. **Resource-Based URLs**: `/api/pgm/probabilities/{symbol}`
2. **HTTP Methods**: GET for reads, POST for writes
3. **Status Codes**: 200 (OK), 404 (Not Found), 500 (Error)
4. **JSON Responses**: Consistent structure
5. **Versioning**: Future-ready (v1, v2)

### Request/Response Format

#### Example: Get Probabilities
```http
GET /api/pgm/probabilities/AAPL HTTP/1.1
Host: localhost:8000
Accept: application/json
```

```json
{
  "symbol": "AAPL",
  "timestamp": "2026-04-07T10:30:00Z",
  "probabilities": {
    "positive": 0.45,
    "neutral": 0.35,
    "negative": 0.20
  },
  "prediction": "positive",
  "confidence": 0.45,
  "signal": {
    "action": "BUY",
    "strength": "MODERATE",
    "confidence": 0.45
  },
  "explanation": {
    "summary": "Strong bullish momentum with positive RSI...",
    "key_factors": [
      {
        "feature": "rsi_state",
        "value": "neutral",
        "impact": 0.15,
        "direction": "positive"
      }
    ]
  }
}
```

### Error Handling
```json
{
  "detail": "Symbol not found",
  "status_code": 404,
  "timestamp": "2026-04-07T10:30:00Z",
  "path": "/api/pgm/probabilities/INVALID"
}
```

---

## Database Schema

### File-Based Storage Structure

```
data/
├── raw/                          # Raw market data
│   └── {symbol}_raw.parquet
│       Columns: date, open, high, low, close, volume
│
├── processed/                    # Processed data
│   ├── {symbol}_validated.parquet
│   │   Columns: date, open, high, low, close, volume, validated
│   │
│   ├── features/                 # Feature store
│   │   └── offline/
│   │       └── {symbol}_features.parquet
│   │           Columns: date, close, rsi, macd, bb_upper, bb_lower,
│   │                   volatility, momentum, regime, [50+ features]
│   │
│   ├── pgm_model/               # Trained models
│   │   ├── encoder_config.json
│   │   ├── graph_structure.json
│   │   └── cpts.pkl
│   │
│   ├── evaluation/              # Model metrics
│   │   └── {symbol}_evaluation.json
│   │
│   ├── calibration/             # Calibration data
│   │   └── {symbol}_calibration.json
│   │
│   ├── baseline_comparison/     # Model comparison
│   │   └── {symbol}_comparison.json
│   │
│   └── failures/                # Failure analysis
│       └── {symbol}_failures.json
│
└── logs/                        # Application logs
    ├── app_YYYY-MM-DD.log
    └── error_YYYY-MM-DD.log
```


### Redis Cache Schema

```
Key Pattern: {namespace}:{symbol}:{data_type}

Examples:
• market:AAPL:live           → Latest price (30s TTL)
• market:AAPL:historical     → Full dataset (1h TTL)
• pgm:AAPL:probabilities     → Predictions (30s TTL)
• market:overview            → Market summary (60s TTL)
• cache:stats                → Cache statistics

Value Format: JSON string
```

---

## Security & Performance

### Security Measures

1. **CORS Configuration**
   ```python
   allow_origins=["http://localhost:3000"]
   allow_credentials=True
   allow_methods=["*"]
   allow_headers=["*"]
   ```

2. **Input Validation**
   - Pydantic models for all requests
   - Symbol validation (uppercase, 1-5 chars)
   - Parameter range checks

3. **Error Handling**
   - No sensitive data in error messages
   - Structured logging
   - Exception tracking

4. **Rate Limiting** (Future)
   - Per-IP limits
   - Per-endpoint limits
   - Token bucket algorithm

### Performance Optimizations

1. **Caching Strategy**
   - Multi-layer cache (Browser → Redis → Memory → Disk)
   - Smart TTL based on data volatility
   - Cache warming on startup

2. **Data Loading**
   - Lazy loading of models
   - Incremental data updates
   - Parquet for fast columnar access

3. **API Optimization**
   - Response compression (gzip)
   - Pagination for large datasets
   - Field selection (sparse fieldsets)

4. **Frontend Optimization**
   - Code splitting
   - Image optimization
   - Server-side rendering (SSR)
   - Static generation where possible

### Performance Metrics

```
Target Metrics:
• API Response Time: < 100ms (cached)
• API Response Time: < 500ms (uncached)
• Frontend Load Time: < 2s (First Contentful Paint)
• Cache Hit Rate: > 80%
• Model Inference: < 50ms
```


---

## Deployment Architecture

### Development Environment
```
┌─────────────────────────────────────────┐
│ Developer Machine                       │
├─────────────────────────────────────────┤
│ Terminal 1: Backend                     │
│   python3 api_server.py                 │
│   → http://localhost:8000               │
│                                         │
│ Terminal 2: Frontend                    │
│   npm run dev                           │
│   → http://localhost:3000               │
│                                         │
│ Terminal 3: Redis (optional)            │
│   redis-server                          │
│   → localhost:6379                      │
└─────────────────────────────────────────┘
```

### Production Architecture (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Load Balancer                             │
│                  (NGINX / AWS ALB)                           │
└────────┬────────────────────────────┬────────────────────────┘
         │                            │
         ▼                            ▼
┌─────────────────┐          ┌─────────────────┐
│  Frontend       │          │  Frontend       │
│  (Next.js)      │          │  (Next.js)      │
│  Port 3000      │          │  Port 3000      │
└────────┬────────┘          └────────┬────────┘
         │                            │
         └────────────┬───────────────┘
                      │
         ┌────────────▼────────────┐
         │   API Gateway           │
         │   (NGINX)               │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   Backend Cluster       │
         │   ┌──────────────────┐  │
         │   │ FastAPI Instance │  │
         │   │ Port 8000        │  │
         │   └──────────────────┘  │
         │   ┌──────────────────┐  │
         │   │ FastAPI Instance │  │
         │   │ Port 8001        │  │
         │   └──────────────────┘  │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   Redis Cluster         │
         │   (Cache Layer)         │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   File Storage          │
         │   (S3 / NFS)            │
         │   • Parquet files       │
         │   • Model artifacts     │
         └─────────────────────────┘
```

### Container Architecture (Docker)

```yaml
services:
  frontend:
    image: alphaforge-frontend:latest
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    
  backend:
    image: alphaforge-backend:latest
    ports: ["8000:8000"]
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - ./data:/app/data
    
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes:
      - redis-data:/data
```


---

## Future Enhancements

### Phase 1: Core Improvements (Q2 2026)
- [ ] Real-time WebSocket connections for live updates
- [ ] User authentication and authorization (JWT)
- [ ] Portfolio management and tracking
- [ ] Advanced backtesting with multiple strategies
- [ ] Model retraining pipeline automation

### Phase 2: Advanced Features (Q3 2026)
- [ ] Multi-asset portfolio optimization
- [ ] Options pricing and Greeks calculation
- [ ] Sentiment analysis from news/social media
- [ ] Deep learning model integration (LSTM, Transformers)
- [ ] Risk management dashboard

### Phase 3: Enterprise Features (Q4 2026)
- [ ] Multi-user support with role-based access
- [ ] Custom model training interface
- [ ] API rate limiting and quotas
- [ ] Audit logging and compliance
- [ ] White-label deployment options

### Phase 4: Scaling (2027)
- [ ] Kubernetes deployment
- [ ] Microservices architecture
- [ ] Event-driven architecture (Kafka)
- [ ] Real-time streaming with Apache Flink
- [ ] Global CDN deployment

---

## Appendix

### A. PGM Model Details

#### Bayesian Network Structure
```
                    ┌─────────────┐
                    │   RSI       │
                    │   State     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Momentum   │
                    │   Score     │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Volatility  │    │   Regime    │    │    MACD     │
│   State     │    │   State     │    │    Diff     │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Risk      │
                   │   State     │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Future    │
                   │   Return    │
                   └─────────────┘

Total Nodes: 11
Total Edges: 13
```

#### State Discretization Rules
```
Feature: RSI
• oversold:    RSI < 30
• neutral:     30 ≤ RSI ≤ 70
• overbought:  RSI > 70

Feature: Volatility
• low:         σ < threshold_low
• medium:      threshold_low ≤ σ ≤ threshold_high
• high:        σ > threshold_high

Feature: Momentum
• weak:        momentum < -0.5
• moderate:    -0.5 ≤ momentum ≤ 0.5
• strong:      momentum > 0.5
```


### B. Feature Engineering Pipeline

```
Raw OHLCV Data
      │
      ▼
┌─────────────────────────────────────────┐
│ Technical Indicators (50+)              │
├─────────────────────────────────────────┤
│ Momentum Indicators:                    │
│ • RSI (14-period)                       │
│ • MACD (12, 26, 9)                      │
│ • Stochastic Oscillator                 │
│ • ROC (Rate of Change)                  │
│                                         │
│ Trend Indicators:                       │
│ • SMA (10, 30, 50, 200)                 │
│ • EMA (12, 26)                          │
│ • ADX (Average Directional Index)      │
│                                         │
│ Volatility Indicators:                  │
│ • Bollinger Bands (20, 2σ)              │
│ • ATR (Average True Range)              │
│ • Standard Deviation                    │
│                                         │
│ Volume Indicators:                      │
│ • OBV (On-Balance Volume)               │
│ • Volume SMA                            │
│ • Volume Ratio                          │
│                                         │
│ Custom Features:                        │
│ • Momentum Score (composite)            │
│ • Regime Detection (Bull/Bear/Sideways) │
│ • Trend Slope                           │
│ • Price Position (relative to bands)    │
└─────────────────────────────────────────┘
      │
      ▼
Feature Vector (50+ dimensions)
```

### C. Model Evaluation Metrics

```
Classification Metrics:
• Accuracy:     (TP + TN) / Total
• Precision:    TP / (TP + FP)
• Recall:       TP / (TP + FN)
• F1 Score:     2 × (Precision × Recall) / (Precision + Recall)

Probabilistic Metrics:
• Brier Score:  Mean squared error of probabilities
• Log Loss:     -Σ(y × log(p) + (1-y) × log(1-p))
• Calibration:  Reliability diagram analysis

Trading Metrics:
• Sharpe Ratio: (Return - Risk-free) / Volatility
• Max Drawdown: Maximum peak-to-trough decline
• Win Rate:     Winning trades / Total trades
• Profit Factor: Gross profit / Gross loss
```

### D. API Endpoints Summary

| Endpoint | Method | Purpose | Cache TTL |
|----------|--------|---------|-----------|
| `/api/pgm/probabilities/{symbol}` | GET | Get predictions | 30s |
| `/api/pgm/explanation/{symbol}` | GET | Get explanations | 30s |
| `/api/pgm/signal/{symbol}` | GET | Get trading signal | 30s |
| `/api/pgm/evaluation/{symbol}` | GET | Model metrics | None |
| `/api/pgm/calibration/{symbol}` | GET | Calibration data | None |
| `/api/pgm/baseline-comparison/{symbol}` | GET | Model comparison | None |
| `/api/market/historical/{symbol}` | GET | Historical data | 1h |
| `/api/market/live/{symbol}` | GET | Live price | 30s |
| `/api/market/overview` | GET | Market summary | 60s |
| `/api/market/insights` | GET | AI insights | 60s |

---

## Glossary

**PGM**: Probabilistic Graphical Model - A statistical model using graph theory

**CPT**: Conditional Probability Table - Stores P(X|Parents(X))

**DAG**: Directed Acyclic Graph - Graph structure with no cycles

**RSI**: Relative Strength Index - Momentum oscillator (0-100)

**MACD**: Moving Average Convergence Divergence - Trend indicator

**Bayesian Network**: Probabilistic graphical model representing variables and dependencies

**Feature Engineering**: Process of creating new features from raw data

**Backtesting**: Testing trading strategy on historical data

**Sharpe Ratio**: Risk-adjusted return metric

**Calibration**: Alignment of predicted probabilities with actual outcomes

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-07 | System | Initial design document |

---

**End of Design Document**
