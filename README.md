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

## 🏆 Why Bayesian Network (PGM)?

AlphaForge uses a **Bayesian Network (Probabilistic Graphical Model)** as its primary prediction engine. Here's why:

### Performance Comparison

| Model | Accuracy | F1 Score | Explainability | Uncertainty |
|-------|----------|----------|----------------|-------------|
| **Bayesian Network (PGM)** | **69.1%** | **0.691** | ✅ Full | ✅ Yes |
| Logistic Regression | 38.8% | 0.379 | ⚠️ Limited | ⚠️ Partial |
| Majority Class | 34.0% | 0.173 | ❌ None | ❌ No |
| Random | 33.5% | 0.335 | ❌ None | ❌ No |

### Key Advantages

1. **Explainability**: Shows exactly how features influence predictions with causal reasoning
2. **Probabilistic**: Outputs probability distributions, not just point predictions
3. **Uncertainty Quantification**: Provides confidence levels for every prediction
4. **Scenario Analysis**: Test "what-if" scenarios by changing feature values
5. **Domain-Appropriate**: Models feature dependencies (RSI → Momentum → Return)
6. **Regulatory Compliance**: Transparent decision-making for financial regulations

**78% higher accuracy** than Logistic Regression | **103% improvement** over random baseline

📖 **Read more**: [Why Bayesian Network?](docs/WHY_BAYESIAN_NETWORK.md)

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
- **Feature Intelligence Pipeline**: NEW! Visual data transformation flow from raw data to model input
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
│                     Frontend (Next.js 14)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Dashboard │  │PGM Graph │  │ Feature  │  │  Model   │     │
│  │          │  │          │  │ Pipeline │  │   Eval   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│         Glassmorphism UI + Framer Motion Animations         │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              backend/models/ (Core AI)               │   │
│  │  • State Encoding    • Inference Engine              │   │
│  │  • Graph Structure   • Explanation Engine            │   │
│  │  • Probability Learn • Scenario Simulator            │   │
│  │  • Evaluation        • Failure Analysis              │   │
│  │  • Feature Engineering • Analytics • Backtesting     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           backend/api/ & backend/services/           │   │
│  │  • REST Endpoints    • Business Logic                │   │
│  │  • Caching Service   • Data Service                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              backend/pipelines/                      │   │
│  │  • Batch Pipeline    • Streaming Pipeline            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ yfinance │  │ Parquet  │  │  Redis   │  │  Logs    │     │
│  │   API    │  │  Files   │  │  Cache   │  │          │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│     data/        data/         data/          logs/         │
│   ingestion/   features/     features/                      │
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

**6. Explore Key Features**
- **Dashboard**: Market overview with live signals
- **Feature Intelligence**: NEW! Visual data pipeline (Model Intelligence → Feature Pipeline)
- **PGM Graph**: Interactive Bayesian Network
- **Model Evaluation**: Performance metrics and comparisons

## 📖 Documentation

All documentation is organized in the [`docs/`](./docs/) folder:

### Core Documentation
- **[Project Structure](./PROJECT_STRUCTURE.md)** - Project organization
- **[Design Document](./DESIGN.md)** - System architecture and design
- **[Installation Guide](./INSTALLATION.md)** - Setup instructions

### Feature Documentation
- **[PGM Documentation](./docs/pgm/PGM_DOCUMENTATION.md)** - Probabilistic Graphical Models
- **[Features Overview](./docs/overview/FEATURES.md)** - All implemented features
- **[Architecture](./docs/architecture/ARCHITECTURE.md)** - System design

### Quick Links
- **[Setup Guide](./docs/setup/INSTALLATION.md)** - Complete setup instructions
- **[Quick Start](./docs/setup/QUICKSTART.md)** - Get running in 5 minutes
- **[Frontend Guide](./frontend/README.md)** - Frontend documentation

📚 **See [docs/README.md](./docs/README.md) for complete documentation index**

## 📁 Project Structure

```
AlphaForge/
├── 🔧 backend/                # All backend logic
│   ├── api/                   # FastAPI routes & schemas
│   ├── services/              # Business logic (cache, data)
│   ├── models/                # ML models (PGM, analytics, backtesting)
│   └── pipelines/             # Data processing orchestration
│
├── 🎨 frontend/               # Next.js 14 Frontend
│   ├── app/                   # Pages (App Router)
│   ├── components/            # React components
│   └── lib/                   # Utilities and API client
│
├── 💾 data/                   # Data layer
│   ├── ingestion/             # Data fetching (yfinance)
│   ├── validation/            # Data quality checks
│   ├── features/              # Feature store (Parquet + Redis)
│   ├── raw/                   # Raw market data (gitignored)
│   └── processed/             # Computed features (gitignored)
│
├── 🧪 tests/                  # Unit & integration tests
├── 🛠️ utils/                  # Shared utilities (logger, helpers)
├── ⚙️ config/                 # Configuration files
└── 📚 docs/                   # Documentation
    └── examples/              # Example usage scripts
```

**Clean root directory** with only 8 essential files:
- `api_server.py`, `main.py` - Entry points
- `README.md`, `INSTALLATION.md` - Documentation
- `requirements.txt`, `setup.py` - Dependencies
- `Makefile`, `.gitignore` - Build & config

## 🎮 Usage Examples

### 1. Run Complete PGM Workflow
```bash
python scripts/example_pgm_workflow.py
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

### Feature Intelligence (NEW!)
Visual data pipeline showing transformation from raw market data to model-ready features with interactive discretization toggle.

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
