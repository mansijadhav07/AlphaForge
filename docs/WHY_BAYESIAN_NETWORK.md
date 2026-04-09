# Why Bayesian Network (PGM) for Stock Market Prediction?

## Executive Summary

The Bayesian Network (Probabilistic Graphical Model) was chosen as the primary model for AlphaForge because it provides **explainable, probabilistic predictions** with clear reasoning - essential for financial decision-making. Unlike black-box models, it shows exactly how features influence predictions and quantifies uncertainty.

## Key Advantages Over Baseline Models

### 1. Explainability & Interpretability

**Bayesian Network:**
- Shows causal relationships between features (e.g., RSI → Momentum → Future Return)
- Provides human-readable explanations for every prediction
- Visualizes feature dependencies in a graph structure
- Enables "what-if" scenario analysis

**Logistic Regression:**
- Only provides feature weights (coefficients)
- No causal relationships
- Limited interpretability for non-technical users

**Random/Majority Baselines:**
- No explainability whatsoever

### 2. Probabilistic Reasoning

**Bayesian Network:**
- Outputs probability distributions: P(positive)=0.45, P(neutral)=0.35, P(negative)=0.20
- Quantifies uncertainty in predictions
- Allows risk-aware decision making
- Supports confidence levels (high/moderate/low)

**Logistic Regression:**
- Provides probabilities but no causal reasoning
- Cannot explain why certain probabilities are assigned

### 3. Performance Comparison

Based on our baseline comparison results:

| Model | Accuracy | F1 Score | Explainability | Uncertainty |
|-------|----------|----------|----------------|-------------|
| **Bayesian Network (PGM)** | **69.1%** | **0.691** | ✅ Full | ✅ Yes |
| Logistic Regression | 38.8% | 0.379 | ⚠️ Limited | ⚠️ Partial |
| Majority Class | 34.0% | 0.173 | ❌ None | ❌ No |
| Random | 33.5% | 0.335 | ❌ None | ❌ No |

**Key Findings:**
- Bayesian Network achieves **78% higher accuracy** than Logistic Regression
- **103% improvement** over random baseline
- **103% improvement** over majority class baseline

### 4. Domain-Specific Advantages for Finance

#### a) Handles Feature Dependencies
Financial indicators are highly correlated:
- RSI influences momentum
- Volatility affects risk assessment
- Trend slope determines market regime

Bayesian Networks explicitly model these dependencies, while Logistic Regression assumes feature independence.

#### b) Regime Detection
Markets operate in different regimes (bull/bear/sideways). The Bayesian Network:
- Explicitly models regime as a latent variable
- Adjusts predictions based on current regime
- Provides regime probability distributions

#### c) Risk Assessment
The model includes a dedicated "risk_state" node that:
- Combines volatility and ATR indicators
- Influences return predictions
- Enables risk-adjusted trading signals

#### d) Scenario Simulation
Users can ask "what-if" questions:
- "What if RSI becomes oversold?"
- "What if volatility spikes?"
- "What if we enter a bear market?"

The Bayesian Network can answer these by updating probabilities given hypothetical evidence.

## Technical Justification

### 1. Model Architecture

```
Bayesian Network Structure (11 nodes, 13 edges):

Technical Indicators → Derived Features → Future Return
    ├─ RSI ──────────┐
    ├─ Momentum ─────┼──→ Regime ──┐
    ├─ MACD ─────────┤             │
    ├─ Volatility ───┼──→ Risk ────┼──→ Future Return
    ├─ ATR ──────────┘             │
    ├─ Trend Slope ─────────────────┘
    ├─ BB Position ─────────────────┘
    └─ Volume Ratio ────────────────┘
```

### 2. Inference Algorithm

Uses **Variable Elimination** for exact probabilistic inference:
- Computes P(Future Return | Evidence) exactly
- No approximation errors
- Efficient for networks of this size (~50ms inference time)

### 3. Learning Algorithm

Uses **Maximum Likelihood Estimation** with Laplace smoothing:
- Learns Conditional Probability Tables (CPTs) from historical data
- Handles sparse data gracefully
- Prevents overfitting with smoothing parameter α=1.0

### 4. State Discretization

Continuous features are discretized into meaningful states:
- RSI: oversold (<30), neutral (30-70), overbought (>70)
- Volatility: low, medium, high (based on quantiles)
- Returns: negative, neutral, positive (based on ±2% threshold)

This enables:
- Robust predictions (less sensitive to noise)
- Interpretable states
- Efficient probability learning

## Comparison with Alternative Approaches

### Why Not Deep Learning (LSTM/Transformers)?

**Pros of Deep Learning:**
- Can capture complex non-linear patterns
- Potentially higher accuracy on large datasets

**Cons (Why We Chose Bayesian Network Instead):**
- ❌ Black-box: No explainability
- ❌ Requires massive amounts of data (we have ~1500 samples per stock)
- ❌ Computationally expensive
- ❌ Difficult to debug when predictions fail
- ❌ No uncertainty quantification
- ❌ Cannot perform scenario analysis

### Why Not Random Forest/XGBoost?

**Pros of Tree Ensembles:**
- High accuracy
- Feature importance scores

**Cons:**
- ⚠️ Limited explainability (feature importance ≠ causal reasoning)
- ❌ No probabilistic reasoning
- ❌ Cannot model feature dependencies explicitly
- ❌ No scenario simulation capability

### Why Not Simple Logistic Regression?

**Pros:**
- Fast training
- Simple to understand

**Cons:**
- ❌ Assumes feature independence (violated in financial data)
- ❌ Linear decision boundaries (markets are non-linear)
- ❌ No causal reasoning
- ❌ Lower accuracy (38.8% vs 69.1%)

## Real-World Use Cases

### 1. Regulatory Compliance
Financial institutions need to explain model decisions to regulators. Bayesian Networks provide:
- Clear audit trail
- Causal explanations
- Transparent decision-making process

### 2. Risk Management
Portfolio managers need to understand:
- Why a prediction was made
- What factors contributed most
- How confident the model is
- What could change the prediction

Bayesian Networks answer all these questions.

### 3. Educational Value
For retail investors learning about markets:
- Visualize how indicators interact
- Understand market dynamics
- Learn causal relationships
- Test hypotheses with simulations

## Performance Metrics

### Accuracy by Symbol (Test Set)

| Symbol | Accuracy | Precision | Recall | F1 Score |
|--------|----------|-----------|--------|----------|
| AAPL | 69.1% | 0.693 | 0.691 | 0.691 |
| TSLA | 69.1% | 0.693 | 0.691 | 0.691 |
| GOOGL | 67.9% | 0.680 | 0.679 | 0.678 |
| MSFT | 67.9% | 0.680 | 0.679 | 0.678 |

### Confusion Matrix (AAPL Example)

```
                Predicted
              Neg  Neu  Pos
Actual  Neg   89   16   19   (71.8% correct)
        Neu   20   84   24   (65.6% correct)
        Pos   21   16   87   (70.2% correct)
```

### Calibration
The model is well-calibrated:
- Predicted probabilities match actual frequencies
- Brier Score: ~0.18 (lower is better)
- Reliable confidence estimates

## Limitations & Future Work

### Current Limitations

1. **Discretization Loss**: Converting continuous features to discrete states loses some information
2. **Linear CPTs**: Conditional probabilities are learned from frequency counts (non-parametric)
3. **Static Structure**: Graph structure is manually defined, not learned from data
4. **Limited Temporal Modeling**: Doesn't explicitly model time-series dynamics

### Planned Improvements

1. **Dynamic Bayesian Networks (DBNs)**: Model temporal dependencies explicitly
2. **Structure Learning**: Automatically learn optimal graph structure from data
3. **Hybrid Models**: Combine with neural networks for feature extraction
4. **Online Learning**: Update CPTs in real-time as new data arrives

## Conclusion

The Bayesian Network (PGM) was chosen because it provides the **best balance** of:
- ✅ High accuracy (69% vs 39% for Logistic Regression)
- ✅ Full explainability (causal reasoning)
- ✅ Probabilistic predictions (uncertainty quantification)
- ✅ Domain-appropriate (models feature dependencies)
- ✅ Practical utility (scenario simulation, risk assessment)

For financial applications where **trust, transparency, and interpretability** are paramount, Bayesian Networks are the superior choice over black-box alternatives.

## References

1. Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*. Cambridge University Press.
2. Koller, D., & Friedman, N. (2009). *Probabilistic Graphical Models: Principles and Techniques*. MIT Press.
3. Murphy, K. P. (2012). *Machine Learning: A Probabilistic Perspective*. MIT Press.
4. Rudin, C. (2019). "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead." *Nature Machine Intelligence*.

---

**For examiner questions, refer to:**
- Baseline comparison results: `data/processed/baseline_comparison/`
- Model evaluation metrics: `data/processed/evaluation/`
- Graph structure visualization: `data/processed/analytics/pgm_graph_structure.png`
- API documentation: `docs/ARCHITECTURE_DIAGRAM.md`
