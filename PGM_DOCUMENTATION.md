# Probabilistic Graphical Model (PGM) Module

## Overview

The PGM module extends AlphaForge with advanced probabilistic reasoning capabilities using Bayesian Networks. It models dependencies between financial features and performs probabilistic inference to generate explainable, uncertainty-aware predictions.

## Architecture

```
pgm_model/
├── __init__.py                 # Module initialization
├── state_encoding.py           # Continuous → Discrete encoding
├── graph_structure.py          # Bayesian Network DAG definition
├── probability_learning.py     # CPT learning from data
├── inference_engine.py         # Variable Elimination inference
├── explanation_engine.py       # Human-readable explanations
├── scenario_simulator.py       # What-if analysis
└── utils.py                    # Utility functions
```

## Core Components

### 1. State Encoding Layer (`state_encoding.py`)

Converts continuous financial features into discrete states suitable for Bayesian Networks.

**Key Features:**
- Threshold-based binning (e.g., RSI: oversold/neutral/overbought)
- Quantile-based binning (e.g., volatility: low/medium/high)
- Direct mapping (e.g., regime: -1→bear, 0→sideways, 1→bull)
- Configurable encoding rules
- Automatic threshold learning from data

**Example Usage:**
```python
from pgm_model.state_encoding import StateEncoder

encoder = StateEncoder()
encoder.fit(df)  # Learn quantile thresholds
encoded_df = encoder.transform(df)  # Apply encoding
```

**Default Encodings:**
- `rsi`: oversold (<30), neutral (30-70), overbought (>70)
- `return`: negative (<-1%), neutral (-1% to 1%), positive (>1%)
- `volatility_10`: low/medium/high (quantile-based)
- `momentum_score`: weak/moderate/strong
- `regime`: bear/sideways/bull

### 2. Graph Structure (`graph_structure.py`)

Defines the Directed Acyclic Graph (DAG) representing causal and probabilistic dependencies.

**Default Structure:**
```
Technical Indicators → Future Return
    ├── RSI
    ├── Momentum Score
    ├── MACD
    └── Bollinger Bands

Volatility + ATR → Risk → Future Return

Trend + Momentum → Regime → Future Return

Volume → Future Return
```

**Key Features:**
- DAG validation
- Markov blanket computation
- Topological ordering
- Graph visualization
- Save/load structure

**Example Usage:**
```python
from pgm_model.graph_structure import GraphStructure

graph = GraphStructure()
graph.build_default_structure()
graph.visualize(output_path='graph.png')
```

### 3. Probability Learning (`probability_learning.py`)

Learns Conditional Probability Tables (CPTs) from historical data using frequency-based estimation with Laplace smoothing.

**Key Features:**
- Marginal probability learning for root nodes
- Conditional probability learning for non-root nodes
- Laplace smoothing to handle sparse data
- CPT validation (probabilities sum to 1)
- Save/load learned probabilities

**Example Usage:**
```python
from pgm_model.probability_learning import ProbabilityLearner

learner = ProbabilityLearner(graph_structure, smoothing_alpha=1.0)
learner.learn_from_data(train_df)
learner.print_cpt('future_return_state')
```

**CPT Format:**
```
P(Future Return | RSI, Momentum, Regime)

Given RSI=oversold, Momentum=strong, Regime=bull:
  positive: 0.65
  neutral:  0.25
  negative: 0.10
```

### 4. Inference Engine (`inference_engine.py`)

Performs exact probabilistic inference using the Variable Elimination algorithm.

**Key Features:**
- Exact inference via Variable Elimination
- Query multiple variables simultaneously
- Compute posterior probabilities given evidence
- Most likely state prediction
- Trading signal generation
- Batch inference

**Example Usage:**
```python
from pgm_model.inference_engine import InferenceEngine

engine = InferenceEngine(graph_structure, prob_learner)

# Query with evidence
evidence = {
    'rsi_state': 'oversold',
    'momentum_score_state': 'strong',
    'regime_state': 'bull'
}

result = engine.query(['future_return_state'], evidence)
# Returns: {'future_return_state': {'positive': 0.65, 'neutral': 0.25, 'negative': 0.10}}

# Trading signals
signals = engine.compute_signal_probabilities(evidence)
# Returns: {'buy': 0.65, 'hold': 0.25, 'sell': 0.10}
```

### 5. Explanation Engine (`explanation_engine.py`)

Generates human-readable explanations for probabilistic predictions.

**Key Features:**
- Feature contribution analysis (sensitivity-based)
- Reasoning chain construction
- Alternative scenario generation
- Risk assessment
- Confidence categorization
- Formatted text reports

**Example Usage:**
```python
from pgm_model.explanation_engine import ExplanationEngine

explainer = ExplanationEngine(graph_structure, inference_engine)

explanation = explainer.explain_prediction(
    'future_return_state',
    evidence,
    prediction_result
)

text = explainer.generate_text_explanation(explanation)
print(text)
```

**Explanation Components:**
- **Prediction**: Most likely outcome
- **Confidence**: Probability and level (High/Moderate/Low)
- **Key Factors**: Top 5 influential features with impact scores
- **Reasoning Chain**: Causal path from evidence to prediction
- **Alternative Scenarios**: All possible outcomes with probabilities
- **Risk Assessment**: Risk level and management recommendations

### 6. Scenario Simulator (`scenario_simulator.py`)

Enables what-if analysis and scenario exploration.

**Key Features:**
- Single scenario simulation
- Multi-scenario comparison
- Sensitivity analysis (vary one feature)
- Multi-feature sensitivity (vary multiple features)
- Optimal scenario search
- 2D scenario grids
- Batch simulation

**Example Usage:**
```python
from pgm_model.scenario_simulator import ScenarioSimulator

simulator = ScenarioSimulator(inference_engine, explanation_engine)

# Sensitivity analysis
sensitivity_df = simulator.sensitivity_analysis(
    base_scenario=evidence,
    query_var='future_return_state',
    vary_feature='rsi_state'
)

# Find optimal scenario
optimal = simulator.find_optimal_scenario(
    query_var='future_return_state',
    desired_outcome='positive',
    fixed_features={'volatility_10_state': 'low'}
)
```

## Complete Workflow

### Step 1: Prepare Data
```python
from pgm_model.utils import prepare_data_for_pgm
from pgm_model.state_encoding import StateEncoder

encoder = StateEncoder()
encoded_df = prepare_data_for_pgm(df, encoder, horizon=5, threshold=0.02)
```

### Step 2: Build Graph
```python
from pgm_model.graph_structure import GraphStructure

graph_structure = GraphStructure()
graph_structure.build_default_structure()
```

### Step 3: Learn Probabilities
```python
from pgm_model.probability_learning import ProbabilityLearner

prob_learner = ProbabilityLearner(graph_structure, smoothing_alpha=1.0)
prob_learner.learn_from_data(train_df)
```

### Step 4: Perform Inference
```python
from pgm_model.inference_engine import InferenceEngine

inference_engine = InferenceEngine(graph_structure, prob_learner)

evidence = {'rsi_state': 'oversold', 'regime_state': 'bull'}
result = inference_engine.query(['future_return_state'], evidence)
```

### Step 5: Generate Explanations
```python
from pgm_model.explanation_engine import ExplanationEngine

explanation_engine = ExplanationEngine(graph_structure, inference_engine)
explanation = explanation_engine.explain_prediction(
    'future_return_state', evidence, result['future_return_state']
)
```

### Step 6: Simulate Scenarios
```python
from pgm_model.scenario_simulator import ScenarioSimulator

simulator = ScenarioSimulator(inference_engine, explanation_engine)
report = simulator.generate_scenario_report(evidence, ['future_return_state'])
```

## Integration with AlphaForge

### 1. Pipeline Integration

Add PGM layer to batch pipeline:

```python
# In pipelines/batch_pipeline.py

from pgm_model import StateEncoder, InferenceEngine

class BatchPipeline:
    def __init__(self):
        # ... existing code ...
        self.pgm_encoder = StateEncoder()
        self.pgm_inference = InferenceEngine(graph, learner)
    
    def run(self):
        # ... existing pipeline ...
        
        # Add PGM predictions
        encoded_df = self.pgm_encoder.transform(features_df)
        pgm_predictions = self.pgm_inference.batch_inference(
            encoded_df, ['future_return_state'], evidence_cols
        )
        
        # Store PGM outputs
        self.feature_store.write_features(pgm_predictions, 'pgm_predictions')
```

### 2. API Endpoints

Add to `main.py`:

```python
from pgm_model import InferenceEngine, ExplanationEngine, ScenarioSimulator

@app.get("/api/pgm/probabilities/{symbol}")
async def get_probabilities(symbol: str):
    """Get probabilistic predictions for a symbol."""
    # Get current features
    features = feature_store.get_latest_features(symbol)
    
    # Encode
    encoded = encoder.transform(features)
    
    # Infer
    evidence = {col: encoded[col].iloc[-1] for col in state_cols}
    result = inference_engine.query(['future_return_state'], evidence)
    
    return result

@app.get("/api/pgm/explanation/{symbol}")
async def get_explanation(symbol: str):
    """Get explanation for prediction."""
    # ... similar to above ...
    explanation = explanation_engine.explain_prediction(...)
    return explanation

@app.post("/api/pgm/simulate")
async def simulate_scenario(scenario: dict):
    """Simulate a custom scenario."""
    result = simulator.simulate_scenario(scenario, ['future_return_state'])
    return result
```

### 3. Frontend Integration

Add to Next.js frontend:

```typescript
// In frontend/lib/api.ts

export async function getPGMProbabilities(symbol: string) {
  const response = await fetch(`/api/pgm/probabilities/${symbol}`);
  return response.json();
}

export async function getPGMExplanation(symbol: string) {
  const response = await fetch(`/api/pgm/explanation/${symbol}`);
  return response.json();
}

export async function simulateScenario(scenario: object) {
  const response = await fetch('/api/pgm/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scenario)
  });
  return response.json();
}
```

## Performance Considerations

### Computational Complexity

- **State Encoding**: O(n) where n = number of samples
- **CPT Learning**: O(n × m) where m = number of parent combinations
- **Inference**: O(exp(w)) where w = treewidth of graph (typically small for financial networks)

### Optimization Tips

1. **Limit Parent Nodes**: Keep each node's parents ≤ 3 for efficiency
2. **Batch Processing**: Use batch inference for multiple predictions
3. **Caching**: Cache CPTs and reuse for multiple queries
4. **Quantization**: Use 3-5 states per variable (avoid over-discretization)

## Evaluation Metrics

### Classification Metrics
- Accuracy
- Precision, Recall, F1-Score
- Confusion Matrix

### Probabilistic Metrics
- Calibration curves
- Brier score
- Log-likelihood

### Trading Metrics
- Sharpe ratio with probabilistic signals
- Win rate by confidence level
- Risk-adjusted returns

## Advanced Features

### Custom Graph Structures

```python
graph = GraphStructure()
graph.add_node('custom_feature_state', description='Custom feature')
graph.add_edge('custom_feature_state', 'future_return_state')
```

### Custom Encoding Rules

```python
encoder.add_custom_rule('custom_feature', {
    'type': 'threshold',
    'thresholds': [10, 20],
    'labels': ['low', 'medium', 'high'],
    'description': 'Custom feature description'
})
```

### Dynamic Bayesian Networks (Future)

For temporal modeling:
- Add time-sliced nodes
- Model temporal dependencies
- Perform filtering and smoothing

## Troubleshooting

### Issue: Low Prediction Accuracy

**Solutions:**
- Increase training data
- Adjust state thresholds
- Add more relevant features to graph
- Check for data quality issues

### Issue: Slow Inference

**Solutions:**
- Reduce number of parent nodes
- Use batch inference
- Simplify graph structure
- Cache frequently used queries

### Issue: Invalid CPTs (don't sum to 1)

**Solutions:**
- Check for NaN values in data
- Increase Laplace smoothing alpha
- Verify data encoding correctness

## References

- Koller, D., & Friedman, N. (2009). *Probabilistic Graphical Models*
- Pearl, J. (1988). *Probabilistic Reasoning in Intelligent Systems*
- Murphy, K. P. (2012). *Machine Learning: A Probabilistic Perspective*

## Future Enhancements

1. **Structure Learning**: Automatic graph structure discovery from data
2. **Dynamic Bayesian Networks**: Temporal modeling
3. **Continuous Variables**: Gaussian Bayesian Networks
4. **Approximate Inference**: Sampling methods for large networks
5. **Causal Inference**: Interventional queries and counterfactuals
6. **Online Learning**: Incremental CPT updates

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-25  
**Author**: AlphaForge Team
