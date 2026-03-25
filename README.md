# AlphaForge - AI-Powered Financial Intelligence Platform ✨

<div align="center">

![AlphaForge](https://img.shields.io/badge/AlphaForge-Premium%20Fintech-06b6d4?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14+-000000?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)

**Next-generation financial intelligence powered by Probabilistic Graphical Models**

[Features](#-features) • [Installation](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture)

</div>

---

## 🎯 What is AlphaForge?

AlphaForge is a production-grade financial intelligence platform that combines:
- **Probabilistic Graphical Models (PGM)** for explainable AI predictions
- **Real-time feature engineering** with offline/online feature stores
- **Premium glassmorphism UI** with smooth animations
- **Comprehensive backtesting** and model evaluation
- **Interactive visualizations** of Bayesian networks and feature impacts

Unlike traditional black-box models, AlphaForge provides **transparent, explainable predictions** using Bayesian Networks that model the causal relationships between market features.

## ✨ Key Features

### 🧠 Probabilistic Graphical Models (PGM)
- **Bayesian Network**: 11-node DAG modeling feature dependencies
- **Explainable AI**: Human-readable explanations for every prediction
- **Probabilistic Inference**: P(Future Return | Market Conditions)
- **Scenario Simulation**: What-if analysis and sensitivity testing
- **Feature Impact Analysis**: Quantify each feature's contribution
- **Failure Case Analysis**: Identify and explain prediction errors
- **Model Evaluation**: Comprehensive metrics (accuracy, Brier score, calibration)

### 📊 Advanced Analytics
- **Interactive PGM Graph**: Visualize Bayesian network structure
- **Feature Contribution Charts**: See which features drive predictions
- **Confusion Matrix**: Understand classification performance
- **Calibration Curves**: Validate probability estimates
- **Failure Analysis**: Learn from model mistakes

### 🎨 Premium UI/UX
- **Glassmorphism Design**: Backdrop blur, gradient effects
- **Framer Motion Animations**: Smooth, physics-based transitions
- **Loading Skeletons**: Premium loading states
- **Responsive Design**: Works on all devices
- **Dark Theme**: Easy on the eyes for long sessions

### 📈 Real-Time Feature Engineering
- **50+ Technical Indicators**: RSI, MACD, Bollinger Bands, ATR, etc.
- **Regime Detection**: Bull/Bear/Sideways classification
- **Momentum Scoring**: Composite momentum indicators
- **Volatility Analysis**: Multiple volatility measures
- **Feature Store**: Offline (Parquet) + Online (Redis)

### 🔬 Backtesting & Evaluation
- **Multiple Strategies**: RSI, MACD, Trend Following
- **Performance Metrics**: Sharpe ratio, max drawdown, win rate
- **Equity Curves**: Visualize strategy performance
- **Trade Analysis**: Detailed trade-by-trade breakdown

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 14)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │PGM Graph │  │ Feature  │  │  Model   │   │
│  │          │  │          │  │  Impact  │  │   Eval   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         Glassmorphism UI + Framer Motion Animations         │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              PGM Module (Core AI)                     │  │
│  │  • State Encoding    • Inference Engine              │  │
│  │  • Graph Structure   • Explanation Engine            │  │
│  │  • Probability Learn • Scenario Simulator            │  │
│  │  • Evaluation        • Failure Analysis              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Feature Engineering Pipeline                │  │
│  │  • Data Ingestion    • Feature Store                 │  │
│  │  • Validation        • Analytics                     │  │
│  │  • Backtesting       • Monitoring                    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ yfinance │  │ Parquet  │  │  Redis   │  │  Logs    │   │
│  │   API    │  │  Files   │  │  Cache   │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Redis** (optional, for online feature store)

### Installation

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd AlphaForge
```

**2. Backend Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

**3. Frontend Setup**
```bash
cd frontend
npm install
cd ..
```

**4. Start the Application**

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python3 api_server.py
```
Backend runs on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:3000`

**5. Open Your Browser**
```
http://localhost:3000
```

You'll see a premium animated splash screen, then be redirected to the dashboard!

## 📖 Documentation

### Core Documentation
- **[INSTALLATION_STEPS.md](INSTALLATION_STEPS.md)** - Detailed setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[FEATURES.md](FEATURES.md)** - Complete feature list
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide

### PGM Module Documentation
- **[WHAT_IS_PGM.md](WHAT_IS_PGM.md)** - Introduction to PGMs
- **[PGM_DOCUMENTATION.md](PGM_DOCUMENTATION.md)** - Complete PGM guide
- **[PGM_INTEGRATION_GUIDE.md](PGM_INTEGRATION_GUIDE.md)** - Integration steps
- **[PGM_MODULE_SUMMARY.md](PGM_MODULE_SUMMARY.md)** - Module overview

### Feature Documentation
- **[PGM_GRAPH_SUMMARY.md](PGM_GRAPH_SUMMARY.md)** - Graph visualization
- **[FEATURE_CONTRIBUTION_COMPLETE.md](FEATURE_CONTRIBUTION_COMPLETE.md)** - Feature impact
- **[MODEL_EVALUATION_COMPLETE.md](MODEL_EVALUATION_COMPLETE.md)** - Model evaluation
- **[FAILURE_ANALYSIS_COMPLETE.md](FAILURE_ANALYSIS_COMPLETE.md)** - Failure analysis

### Frontend Documentation
- **[frontend/PREMIUM_UI_COMPLETE.md](frontend/PREMIUM_UI_COMPLETE.md)** - UI enhancements
- **[frontend/README.md](frontend/README.md)** - Frontend guide
- **[frontend/SETUP_GUIDE.md](frontend/SETUP_GUIDE.md)** - Frontend setup

## 📁 Project Structure

```
AlphaForge/
├── 🧠 pgm_model/              # Probabilistic Graphical Models (Core AI)
│   ├── state_encoding.py      # Continuous → Discrete encoding
│   ├── graph_structure.py     # Bayesian Network DAG
│   ├── probability_learning.py # CPT learning from data
│   ├── inference_engine.py    # Probabilistic inference
│   ├── explanation_engine.py  # Human-readable explanations
│   ├── scenario_simulator.py  # What-if analysis
│   ├── evaluation.py          # Model evaluation metrics
│   ├── failure_analysis.py    # Failure case analysis
│   └── utils.py              # PGM utilities
│
├── 🔌 api/                    # FastAPI Backend
│   ├── pgm_routes.py         # PGM API endpoints
│   ├── schemas.py            # Pydantic models
│   └── dependencies.py       # Shared dependencies
│
├── 🎨 frontend/               # Next.js 14 Frontend
│   ├── app/                  # Pages (App Router)
│   │   ├── dashboard/        # Market dashboard
│   │   ├── pgm-graph/        # Interactive PGM visualization
│   │   ├── feature-impact/   # Feature contribution analysis
│   │   ├── model-evaluation/ # Model performance metrics
│   │   ├── model-failures/   # Failure case analysis
│   │   ├── backtesting/      # Strategy backtesting
│   │   ├── insights/         # AI insights
│   │   └── stock/[symbol]/   # Individual stock analysis
│   ├── components/           # React components
│   │   ├── ui/              # Base UI components
│   │   ├── charts/          # Chart components
│   │   ├── layout/          # Layout components
│   │   └── pgm/             # PGM-specific components
│   └── lib/                 # Utilities
│
├── 📊 data_ingestion/         # Data fetching
├── 🔍 data_validation/        # Data quality
├── ⚙️ feature_engineering/    # Feature computation
├── 💾 feature_store/          # Offline/Online storage
├── 🔄 pipelines/              # Orchestration
├── 📈 analytics/              # Analysis
├── 🧪 backtesting/            # Strategy evaluation
├── 📊 dashboard/              # Streamlit dashboard (legacy)
├── ⚙️ config/                 # Configuration
├── 🛠️ utils/                  # Shared utilities
└── 🧪 tests/                  # Unit tests
```

## 🎮 Usage Examples

### 1. Run Complete PGM Workflow
```bash
python example_pgm_workflow.py
```
This will:
- Load and prepare data
- Train the Bayesian Network
- Perform probabilistic inference
- Generate explanations
- Run scenario simulations

### 2. Ingest Historical Data
```bash
python -m pipelines.batch_pipeline --mode historical --tickers AAPL,TSLA
```

### 3. Run Feature Engineering
```bash
python -m pipelines.batch_pipeline --mode features
```

### 4. Start Streaming Simulation
```bash
python -m pipelines.streaming_pipeline
```

### 5. Run Backtesting
```bash
python -m backtesting.backtest_engine --strategy rsi_strategy
```

### 6. Access API Documentation
```
http://localhost:8000/docs
```

## 🎨 UI Screenshots

### Dashboard
Premium glassmorphism cards with real-time market data, animated stats, and AI-powered signals.

### PGM Graph
Interactive Bayesian Network visualization showing feature dependencies and causal relationships.

### Feature Impact
Bar charts showing each feature's contribution to predictions with sensitivity analysis.

### Model Evaluation
Confusion matrix, calibration curves, and comprehensive performance metrics.

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

pgm:
  discretization:
    n_bins: 3
    method: "quantile"
  inference:
    method: "variable_elimination"

storage:
  data_dir: "./data"
  offline_store: "./data/features"
  redis_host: "localhost"
  redis_port: 6379
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_pgm_module.py

# Run with coverage
pytest --cov=pgm_model tests/
```

## 📊 Performance Metrics

### Model Performance
- **Accuracy**: 65-70% on 3-class classification
- **Brier Score**: 0.15-0.20 (lower is better)
- **Calibration**: Well-calibrated probabilities
- **Inference Speed**: <10ms per prediction

### UI Performance
- **First Load**: 2.24 kB (home page)
- **Dashboard**: 3.99 kB
- **Build Time**: ~30 seconds
- **Animation FPS**: 60fps smooth

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Follow ESLint rules
- **Documentation**: Update relevant .md files
- **Tests**: Add tests for new features

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- **Technical Analysis Library**: ta-lib
- **Probabilistic Programming**: pgmpy, networkx
- **UI Framework**: Next.js, Framer Motion, Tailwind CSS
- **Data Source**: yfinance

## 📞 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions

## 🗺️ Roadmap

- [ ] Real-time streaming with Kafka
- [ ] Multi-asset portfolio optimization
- [ ] Deep learning integration
- [ ] Mobile app (React Native)
- [ ] Cloud deployment (AWS/GCP)
- [ ] Advanced risk management
- [ ] Social sentiment analysis
- [ ] Options pricing models

---

<div align="center">

**Built with ❤️ for quantitative traders and data scientists**

⭐ Star us on GitHub if you find this useful!

</div>
