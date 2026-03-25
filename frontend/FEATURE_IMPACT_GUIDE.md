# Feature Contribution Analysis - User Guide

## 🎯 What Is It?

Feature Contribution Analysis shows you **exactly how much each feature influences** the probabilistic predictions in AlphaForge. Think of it as an X-ray into the model's decision-making process.

## 🔍 How It Works

### The Science Behind It

1. **Baseline Prediction**: Model makes a prediction using all features
2. **Feature Removal**: Remove one feature and predict again
3. **Measure Change**: Calculate how much the prediction changed
4. **Repeat**: Do this for every feature
5. **Rank**: Sort features by their impact

### The Math
We use **Total Variation Distance** (TVD) to measure how different two probability distributions are:

```
Impact = TVD(Prediction with all features, Prediction without feature X)
```

Higher impact = more influential feature

## 📊 Reading the Chart

### Bar Chart
- **Horizontal bars** show each feature
- **Length** indicates impact strength
- **Colors** show impact level:
  - 🔵 **Blue** (>20%): Very high impact
  - 🟢 **Teal** (15-20%): High impact
  - 🟣 **Purple** (10-15%): Medium impact
  - ⚪ **Gray** (<10%): Low impact

### Hover for Details
Move your mouse over any bar to see:
- Feature name
- Exact impact percentage
- Current state (e.g., "oversold", "strong")

## 📍 Where to Find It

### Option 1: Dedicated Page
1. Click **"Feature Impact"** in the navbar
2. Select a symbol from dropdown
3. View full analysis with statistics

### Option 2: Stock Detail Page
1. Go to any stock page (e.g., `/stock/AAPL`)
2. Scroll to bottom
3. See **"Feature Contribution Analysis"** section

## 💡 How to Use It

### For Trading Decisions

**Scenario**: You see a BUY signal for AAPL

1. Check feature impact page
2. Look at top 3 features
3. Verify they support the signal:
   - RSI (23%) - Oversold ✅
   - Momentum (19%) - Strong ✅
   - Regime (16%) - Bull ✅
4. High confidence in signal!

**Red Flag**: If top features contradict the signal, be cautious.

### For Model Understanding

**Question**: Why did the model predict positive returns?

1. View feature impact
2. Top feature: RSI (23%) - Oversold
3. Interpretation: Model sees oversold conditions as bullish
4. Makes sense! Oversold often precedes rebounds

### For Risk Assessment

**High Risk Indicators**:
- Volatility has high impact (>15%)
- Risk feature is prominent
- Conflicting signals in top features

**Low Risk Indicators**:
- Clear consensus in top features
- Momentum indicators dominate
- Low volatility impact

## 📈 Example Analysis

### Bullish Setup
```
1. RSI (23.4%) - Oversold
2. Momentum (18.9%) - Strong
3. Regime (15.6%) - Bull
4. Volatility (12.3%) - Low
```

**Interpretation**: Strong bullish signal
- Oversold RSI suggests reversal
- Strong momentum confirms direction
- Bull regime supports upside
- Low volatility reduces risk

### Uncertain Setup
```
1. Volatility (22.1%) - High
2. Risk (18.3%) - High
3. RSI (15.2%) - Neutral
4. Momentum (12.8%) - Weak
```

**Interpretation**: High uncertainty
- Volatility dominates prediction
- Risk is elevated
- Technical indicators mixed
- Wait for clearer signals

## 🎓 Understanding the Numbers

### Impact Score (Raw)
- Range: 0.000 to 1.000
- Example: 0.234 = 23.4% impact
- Sum of all impacts ≈ 1.0

### Normalized Percentage
- Shows relative contribution
- All percentages sum to 100%
- Easier to compare features

### Influence Level
- **Very High**: Critical for prediction
- **High**: Important factor
- **Medium**: Moderate influence
- **Low**: Minor contribution

## 🔧 Statistics Explained

### Total Features
Number of features analyzed (typically 8-11)

### Average Impact
Mean impact across all features
- High average (>12%): Distributed influence
- Low average (<10%): Concentrated in few features

### Top Feature
Most influential feature
- Check its current state
- Understand why it matters

### Top Impact
Highest impact score
- >25%: Single feature dominates
- 15-25%: Strong but balanced
- <15%: Distributed influence

## 🎨 Visual Elements

### Color Coding
Colors help you quickly identify important features:
- **Blue bars**: Pay attention! High impact
- **Teal bars**: Important factors
- **Purple bars**: Moderate influence
- **Gray bars**: Minor factors

### Progress Bars
In the detailed table, progress bars show:
- Visual comparison of impacts
- Relative contribution
- Quick scanning

### Badges
State badges show current feature values:
- "oversold", "overbought" for RSI
- "strong", "weak" for momentum
- "bull", "bear" for regime
- "high", "low" for volatility

## 🚀 Pro Tips

### 1. Focus on Top 3
The top 3 features usually account for 50-60% of total influence. Master these first.

### 2. Watch for Changes
If top features change dramatically:
- Market regime may be shifting
- Model adapting to new conditions
- Review your strategy

### 3. Combine with Confidence
Use feature impact WITH prediction confidence:
- High confidence + clear top features = Strong signal
- Low confidence + mixed features = Uncertain signal

### 4. Compare Symbols
Look at feature impact across different stocks:
- Some stocks driven by momentum
- Others by volatility
- Tailor strategy accordingly

### 5. Monitor Over Time
Track how feature importance evolves:
- Stable patterns = reliable model
- Sudden changes = regime shift
- Use for model validation

## ❓ Common Questions

### Q: Why do percentages not add to exactly 100%?
A: Raw impact scores are normalized. Small rounding differences may occur.

### Q: Can a feature have 0% impact?
A: Rare, but possible if feature is independent of prediction target.

### Q: What if all features have similar impact?
A: Indicates distributed influence. No single dominant factor.

### Q: Should I only trade when top feature is >30%?
A: Not necessarily. Consider total picture and confidence level.

### Q: How often do impact scores change?
A: They update with each new prediction based on current market state.

## 🎯 Best Practices

### DO:
✅ Check feature impact before major trades
✅ Understand top 3 features
✅ Combine with other analysis
✅ Monitor changes over time
✅ Use for model validation

### DON'T:
❌ Rely solely on one feature
❌ Ignore low-impact features completely
❌ Trade against top features
❌ Forget about prediction confidence
❌ Overlook current states

## 🔗 Related Features

- **PGM Graph**: See how features connect
- **Insights Page**: Get AI-generated insights
- **Stock Detail**: View all technical indicators
- **Backtesting**: Test strategies with features

## 📚 Learn More

### Concepts
- Sensitivity Analysis
- Total Variation Distance
- Feature Importance
- Model Interpretability
- Bayesian Networks

### Resources
- `FEATURE_CONTRIBUTION_COMPLETE.md` - Technical details
- `PGM_DOCUMENTATION.md` - Model architecture
- `PGM_INTEGRATION_GUIDE.md` - Integration guide

## 🎉 Summary

Feature Contribution Analysis transforms the "black box" of machine learning into a transparent, understandable system. By showing exactly which features drive predictions, you can:

- Make more informed trading decisions
- Understand model behavior
- Identify key market drivers
- Validate prediction signals
- Build confidence in the system

**Remember**: The model is a tool. Use feature impact to enhance your judgment, not replace it.

Happy trading! 📊🚀
