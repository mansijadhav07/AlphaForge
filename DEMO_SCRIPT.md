# AlphaForge - Demo Script for Judges

## 🎯 Demo Duration: 10-15 minutes

---

## 🚀 Setup (Before Judges Arrive)

### Terminal 1 - Backend
```bash
source venv/bin/activate  # or: venv\Scripts\activate on Windows
python3 api_server.py
```
✅ Wait for: "Uvicorn running on http://127.0.0.1:8000"

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
✅ Wait for: "Ready on http://localhost:3000"

### Browser
- Open: `http://localhost:3000`
- Clear cache (Cmd+Shift+R / Ctrl+Shift+R)
- Verify all pages load
- Close unnecessary tabs

---

## 📖 Demo Script

### 1. Introduction (1 minute)

**Say**:
> "AlphaForge is an AI-powered financial intelligence platform that uses Probabilistic Graphical Models to provide explainable, transparent predictions for stock market analysis. Unlike traditional black-box ML models, our Bayesian Network approach provides causal reasoning and uncertainty quantification."

**Show**: Home page with animated splash screen

**Key Points**:
- Explainable AI vs black box
- Probabilistic predictions with confidence
- Modern, professional UI

---

### 2. Dashboard Overview (2 minutes)

**Navigate**: Click "Dashboard" or wait for auto-redirect

**Say**:
> "The dashboard provides real-time market intelligence. We track multiple stocks with live data, market regime detection, and AI-powered trading signals."

**Highlight**:
- ✨ **Market Regime**: Bull/Bear/Sideways classification
- 📊 **Volatility Index**: Real-time market volatility
- 📈 **Top Stocks**: Live price updates with changes
- 🎯 **AI Signals**: BUY/SELL/HOLD with confidence scores

**Interact**:
- Hover over cards (show glow effects)
- Point out confidence percentages
- Click on a stock (e.g., AAPL)

---

### 3. Stock Detail Page (2 minutes)

**Current Page**: Stock detail for AAPL

**Say**:
> "For each stock, we compute 50+ technical indicators in real-time. The system performs feature engineering, discretization, and feeds these into our Bayesian Network for probabilistic inference."

**Highlight**:
- 📈 **Price Chart**: Interactive with live updates
- 📊 **Technical Indicators**: RSI, MACD, Bollinger Bands
- 🎯 **AI Prediction**: Probability distribution (Positive/Neutral/Negative)
- 💡 **Explanation**: Why the model made this prediction
- ⚠️ **Risk Level**: Quantified uncertainty

**Interact**:
- Scroll through indicators
- Show the explanation section
- Point out probability percentages

---

### 4. Feature Intelligence (3 minutes) ⭐ NEW!

**Navigate**: Model Intelligence → Feature Pipeline

**Say**:
> "This is our newest feature - a visual explanation of how raw market data transforms into model-ready features. This educational interface helps users understand the complete data pipeline."

**Highlight**:
- 🔄 **Pipeline Flow**: 5-stage transformation
  - Raw Data → Cleaning → Feature Engineering → Discretization → Model Input
- 📊 **Raw Data Table**: Latest 5 trading days
- ⚡ **Engineered Features**: 6 key technical indicators
- 🎯 **Discretization**: Continuous → Categorical transformation
- 🌿 **Model Connection**: How features feed into Bayesian Network

**Interact**:
- Switch tickers (AAPL → TSLA)
- Toggle discretization view
- Hover over feature cards (show tooltips)
- Click "View Model Structure"

**Key Point**:
> "Notice how RSI value 28.45 becomes 'OVERSOLD' - this discretization makes the Bayesian Network more efficient while preserving essential information."

---

### 5. PGM Graph (2 minutes)

**Current Page**: PGM Graph (from previous click)

**Say**:
> "This is the heart of our system - an 11-node Bayesian Network that models causal relationships between market features. Unlike correlation-based models, this captures how features influence each other."

**Highlight**:
- 🕸️ **Network Structure**: 11 nodes, 13 edges
- ➡️ **Directed Edges**: Causal relationships
- 🎯 **Target Node**: Future Return (what we predict)
- 🔍 **Feature Dependencies**: RSI → Momentum → Return

**Interact**:
- Zoom in/out on graph
- Hover over nodes (show connections)
- Point out key relationships

**Key Point**:
> "This is a Directed Acyclic Graph (DAG) - it models causality, not just correlation. For example, volatility influences risk, which influences future returns."

---

### 6. Feature Impact (1 minute)

**Navigate**: Model Intelligence → Feature Impact

**Say**:
> "We can quantify exactly how much each feature contributes to predictions. This is crucial for regulatory compliance and trader trust."

**Highlight**:
- 📊 **Bar Chart**: Feature importance scores
- 🎯 **Top Features**: RSI, Momentum, Market Regime
- 📈 **Current States**: Live feature values

**Key Point**:
> "RSI has the highest impact at 23.4%. This transparency is impossible with neural networks."

---

### 7. Model Evaluation (1 minute)

**Navigate**: Model Intelligence → Model Eval

**Say**:
> "We rigorously evaluate our model against multiple baselines. Our Bayesian Network achieves 69.1% accuracy - 78% better than logistic regression."

**Highlight**:
- ✅ **Accuracy**: 69.1% vs 38.8% baseline
- 📊 **Confusion Matrix**: Classification breakdown
- 📈 **Calibration**: Well-calibrated probabilities
- 🎯 **Brier Score**: 0.18 (lower is better)

**Key Point**:
> "More importantly, we provide calibrated probabilities and explanations - not just predictions."

---

### 8. Baseline Comparison (1 minute)

**Navigate**: Model Intelligence → Baselines

**Say**:
> "We compare against three baselines: Logistic Regression, Majority Class, and Random. Our PGM significantly outperforms all of them."

**Highlight**:
- 🏆 **PGM**: 69.1% accuracy, 0.691 F1
- 📉 **Logistic Regression**: 38.8% accuracy
- 📉 **Majority Class**: 34.0% accuracy
- 📉 **Random**: 33.5% accuracy

**Key Point**:
> "78% improvement over logistic regression, with full explainability."

---

### 9. Backtesting (1 minute)

**Navigate**: Backtesting

**Say**:
> "We can backtest trading strategies using our predictions. This shows how the model would perform in real trading scenarios."

**Highlight**:
- 📈 **Equity Curve**: Strategy performance over time
- 💰 **Returns**: Total return percentage
- 📊 **Sharpe Ratio**: Risk-adjusted returns
- 📉 **Max Drawdown**: Worst loss period
- 🎯 **Win Rate**: Percentage of profitable trades

**Interact**:
- Switch strategies (RSI → MACD)
- Show different performance

---

### 10. Wrap-Up (1 minute)

**Navigate**: Back to Dashboard

**Say**:
> "To summarize, AlphaForge combines three key innovations:
> 
> 1. **Explainable AI**: Bayesian Networks provide transparent, causal reasoning
> 2. **Probabilistic Predictions**: Confidence levels and uncertainty quantification
> 3. **Premium UX**: Modern glassmorphism UI with smooth animations
> 
> The result is a platform that traders can trust and understand, with 78% better accuracy than traditional baselines."

**Final Highlight**:
- 🧠 **Technical Innovation**: PGM approach
- 🎨 **Design Excellence**: Premium UI/UX
- 📚 **Comprehensive**: 16 pages, 20+ API endpoints
- 🔬 **Well-Tested**: 41 passing tests
- 📖 **Documented**: 20+ documentation files

---

## 🎯 Key Messages to Emphasize

### 1. Explainability
"Unlike neural networks, we can explain every prediction. This is crucial for financial regulations and trader trust."

### 2. Uncertainty Quantification
"We don't just predict 'BUY' - we say 'BUY with 75% confidence'. This helps traders manage risk."

### 3. Causal Reasoning
"Our model understands that volatility causes risk, which influences returns. Not just correlation."

### 4. Performance
"69.1% accuracy, 78% better than logistic regression, with full transparency."

### 5. Production Quality
"Clean architecture, comprehensive testing, extensive documentation. This is production-grade code."

---

## 💡 Handling Questions

### Q: "Why not use deep learning?"
**A**: "Deep learning is a black box. Financial regulations require explainable decisions. Our Bayesian Network provides causal reasoning and uncertainty quantification while achieving competitive accuracy."

### Q: "How does it handle market crashes?"
**A**: "The model outputs probability distributions, not point predictions. During high uncertainty (like crashes), it shows lower confidence levels, helping traders avoid risky decisions."

### Q: "Can it trade automatically?"
**A**: "It provides signals and confidence levels. Traders make final decisions. This human-in-the-loop approach is safer and more regulatory-compliant."

### Q: "What's the latency?"
**A**: "Inference is under 10ms per prediction. Feature engineering is cached. The system can handle real-time trading requirements."

### Q: "How do you prevent overfitting?"
**A**: "We use cross-validation, test on out-of-sample data, and compare against multiple baselines. The 69.1% accuracy is on held-out test data."

---

## 🚨 Troubleshooting

### If Demo Breaks

**Plan B**: Show documentation
1. Open `README.md` - show project overview
2. Open `DESIGN.md` - show architecture
3. Open `docs/` folder - show comprehensive docs
4. Show code in editor - demonstrate quality

**Plan C**: Show screenshots
1. Have screenshots ready in a folder
2. Walk through the UI using images
3. Explain the architecture verbally

### Common Issues

**Frontend won't load**:
- Check `npm run dev` is running
- Try `http://localhost:3000` directly
- Clear browser cache

**Backend errors**:
- Check `python3 api_server.py` is running
- Verify port 8000 is free
- Mock data will load if API fails

**Slow performance**:
- Close other applications
- Use Chrome/Edge (best performance)
- Reduce animation complexity if needed

---

## ✅ Pre-Demo Checklist

### 5 Minutes Before
- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Browser open to localhost:3000
- [ ] All pages load correctly
- [ ] No console errors
- [ ] Animations smooth
- [ ] Practice demo flow once

### During Demo
- [ ] Speak clearly and confidently
- [ ] Highlight key innovations
- [ ] Show interactive features
- [ ] Explain technical decisions
- [ ] Be honest about limitations
- [ ] Engage with judges' questions

### After Demo
- [ ] Thank judges for their time
- [ ] Offer to show code/docs
- [ ] Provide GitHub link
- [ ] Answer follow-up questions

---

## 🎉 You're Ready!

**Remember**:
- You've built something impressive
- The technical innovation is real
- The UI is professional
- The documentation is comprehensive
- Be confident and enthusiastic

**Good luck!** 🚀
