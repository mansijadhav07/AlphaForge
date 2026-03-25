# PGM Integration Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install networkx>=3.0 scikit-learn>=1.3.0
```

### 2. Run Example Workflow

```bash
# First, ensure you have feature data
python example_workflow.py

# Then run PGM workflow
python example_pgm_workflow.py
```

### 3. Expected Output

The workflow will:
- ✓ Load features from offline store
- ✓ Encode 10+ features to discrete states
- ✓ Build Bayesian Network with 11 nodes
- ✓ Learn conditional probabilities
- ✓ Perform probabilistic inference
- ✓ Generate explanations
- ✓ Simulate scenarios
- ✓ Evaluate on test set
- ✓ Save trained model

## Integration Steps

### Step 1: Update Main Pipeline

Add PGM predictions to your main pipeline:

```python
# In main.py or pipelines/batch_pipeline.py

from pgm_model.utils import load_pgm_model

# Load trained PGM model
encoder, graph_structure, prob_learner = load_pgm_model('data/pgm_model')

# Create inference engine
from pgm_model.inference_engine import InferenceEngine
inference_engine = InferenceEngine(graph_structure, prob_learner)

# In your pipeline
def add_pgm_predictions(features_df):
    # Encode features
    encoded_df = encoder.transform(features_df)
    
    # Get state columns
    state_cols = [col for col in encoded_df.columns if col.endswith('_state')]
    evidence_cols = [col for col in state_cols if col != 'future_return_state']
    
    # Perform inference
    predictions = inference_engine.batch_inference(
        encoded_df,
        query_vars=['future_return_state'],
        evidence_cols=evidence_cols
    )
    
    return predictions
```

### Step 2: Add API Endpoints

Create `pgm_api.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

from pgm_model.utils import load_pgm_model
from pgm_model.inference_engine import InferenceEngine
from pgm_model.explanation_engine import ExplanationEngine
from pgm_model.scenario_simulator import ScenarioSimulator

# Load model
encoder, graph_structure, prob_learner = load_pgm_model('data/pgm_model')
inference_engine = InferenceEngine(graph_structure, prob_learner)
explanation_engine = ExplanationEngine(graph_structure, inference_engine)
scenario_simulator = ScenarioSimulator(inference_engine, explanation_engine)

app = FastAPI()

class ScenarioRequest(BaseModel):
    scenario: Dict[str, str]
    query_vars: List[str] = ['future_return_state']

@app.get("/api/pgm/probabilities/{symbol}")
async def get_probabilities(symbol: str):
    """Get probabilistic predictions for a symbol."""
    try:
        # Get latest features for symbol
        from feature_store.offline_store import OfflineFeatureStore
        store = OfflineFeatureStore()
        features = store.read_latest_features('market_features')
        features = features[features['ticker'] == symbol].iloc[-1:]
        
        if len(features) == 0:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        # Encode
        encoded = encoder.transform(features)
        
        # Build evidence
        state_cols = [col for col in encoded.columns if col.endswith('_state')]
        evidence = {col: encoded[col].iloc[0] for col in state_cols 
                   if col != 'future_return_state' and pd.notna(encoded[col].iloc[0])}
        
        # Infer
        result = inference_engine.query(['future_return_state'], evidence)
        
        # Get trading signals
        signals = inference_engine.compute_signal_probabilities(evidence)
        
        return {
            'symbol': symbol,
            'probabilities': result['future_return_state'],
            'signals': signals,
            'evidence': evidence
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pgm/explanation/{symbol}")
async def get_explanation(symbol: str):
    """Get explanation for prediction."""
    try:
        # Similar to above, get features and encode
        from feature_store.offline_store import OfflineFeatureStore
        store = OfflineFeatureStore()
        features = store.read_latest_features('market_features')
        features = features[features['ticker'] == symbol].iloc[-1:]
        
        if len(features) == 0:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        encoded = encoder.transform(features)
        state_cols = [col for col in encoded.columns if col.endswith('_state')]
        evidence = {col: encoded[col].iloc[0] for col in state_cols 
                   if col != 'future_return_state' and pd.notna(encoded[col].iloc[0])}
        
        # Infer
        result = inference_engine.query(['future_return_state'], evidence)
        
        # Explain
        explanation = explanation_engine.explain_prediction(
            'future_return_state',
            evidence,
            result['future_return_state']
        )
        
        return {
            'symbol': symbol,
            'explanation': explanation
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pgm/simulate")
async def simulate_scenario(request: ScenarioRequest):
    """Simulate a custom scenario."""
    try:
        result = scenario_simulator.simulate_scenario(
            request.scenario,
            request.query_vars
        )
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pgm/sensitivity/{symbol}")
async def sensitivity_analysis(symbol: str, vary_feature: str):
    """Perform sensitivity analysis."""
    try:
        # Get base scenario
        from feature_store.offline_store import OfflineFeatureStore
        store = OfflineFeatureStore()
        features = store.read_latest_features('market_features')
        features = features[features['ticker'] == symbol].iloc[-1:]
        
        encoded = encoder.transform(features)
        state_cols = [col for col in encoded.columns if col.endswith('_state')]
        base_scenario = {col: encoded[col].iloc[0] for col in state_cols 
                        if col != 'future_return_state' and pd.notna(encoded[col].iloc[0])}
        
        # Perform sensitivity analysis
        sensitivity_df = scenario_simulator.sensitivity_analysis(
            base_scenario,
            'future_return_state',
            vary_feature
        )
        
        return {
            'symbol': symbol,
            'vary_feature': vary_feature,
            'results': sensitivity_df.to_dict(orient='records')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Step 3: Update Frontend

Add PGM components to Next.js:

#### API Client (`frontend/lib/api.ts`)

```typescript
export interface PGMProbabilities {
  symbol: string;
  probabilities: Record<string, number>;
  signals: {
    buy: number;
    hold: number;
    sell: number;
  };
  evidence: Record<string, string>;
}

export interface PGMExplanation {
  symbol: string;
  explanation: {
    prediction: string;
    confidence: number;
    confidence_level: string;
    key_factors: Array<{
      feature: string;
      state: string;
      impact_score: number;
      description: string;
    }>;
    reasoning_chain: string[];
    risk_assessment: {
      level: string;
      factors: string[];
      recommendation: string;
    };
  };
}

export async function getPGMProbabilities(symbol: string): Promise<PGMProbabilities> {
  const response = await fetch(`http://localhost:8001/api/pgm/probabilities/${symbol}`);
  if (!response.ok) throw new Error('Failed to fetch PGM probabilities');
  return response.json();
}

export async function getPGMExplanation(symbol: string): Promise<PGMExplanation> {
  const response = await fetch(`http://localhost:8001/api/pgm/explanation/${symbol}`);
  if (!response.ok) throw new Error('Failed to fetch PGM explanation');
  return response.json();
}

export async function simulateScenario(scenario: Record<string, string>) {
  const response = await fetch('http://localhost:8001/api/pgm/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario, query_vars: ['future_return_state'] })
  });
  if (!response.ok) throw new Error('Failed to simulate scenario');
  return response.json();
}
```

#### PGM Probability Component

```typescript
// frontend/components/pgm/probability-panel.tsx

'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { getPGMProbabilities } from '@/lib/api';

export function ProbabilityPanel({ symbol }: { symbol: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await getPGMProbabilities(symbol);
        setData(result);
      } catch (error) {
        console.error('Error fetching PGM data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [symbol]);

  if (loading) return <div>Loading probabilistic predictions...</div>;
  if (!data) return <div>No data available</div>;

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold mb-4">Probabilistic Predictions</h3>
      
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold mb-2">Future Return Probability</h4>
          {Object.entries(data.probabilities).map(([state, prob]: [string, any]) => (
            <div key={state} className="flex items-center gap-2 mb-2">
              <span className="w-24 capitalize">{state}</span>
              <div className="flex-1 bg-gray-700 rounded-full h-6">
                <div
                  className={`h-6 rounded-full ${
                    state === 'positive' ? 'bg-green-500' :
                    state === 'negative' ? 'bg-red-500' : 'bg-yellow-500'
                  }`}
                  style={{ width: `${prob * 100}%` }}
                />
              </div>
              <span className="w-16 text-right">{(prob * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        <div>
          <h4 className="font-semibold mb-2">Trading Signals</h4>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(data.signals).map(([signal, prob]: [string, any]) => (
              <div key={signal} className="text-center">
                <div className={`text-2xl font-bold ${
                  signal === 'buy' ? 'text-green-500' :
                  signal === 'sell' ? 'text-red-500' : 'text-yellow-500'
                }`}>
                  {(prob * 100).toFixed(0)}%
                </div>
                <div className="text-sm uppercase">{signal}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
```

#### Add to Stock Detail Page

```typescript
// In frontend/app/stock/[symbol]/page.tsx

import { ProbabilityPanel } from '@/components/pgm/probability-panel';

export default function StockDetailPage({ params }: { params: { symbol: string } }) {
  return (
    <div className="space-y-6">
      {/* Existing components */}
      
      {/* Add PGM Panel */}
      <ProbabilityPanel symbol={params.symbol} />
    </div>
  );
}
```

### Step 4: Test Integration

```bash
# Terminal 1: Start PGM API
python pgm_api.py

# Terminal 2: Start Frontend
cd frontend
npm run dev

# Terminal 3: Test API
curl http://localhost:8001/api/pgm/probabilities/AAPL
```

## Configuration

### Adjust Prediction Horizon

```python
# In example_pgm_workflow.py or your pipeline
encoded_df = prepare_data_for_pgm(
    df, 
    encoder, 
    horizon=10,  # Predict 10 days ahead instead of 5
    threshold=0.02
)
```

### Modify State Thresholds

```python
encoder.add_custom_rule('rsi', {
    'type': 'threshold',
    'thresholds': [25, 75],  # More extreme thresholds
    'labels': ['oversold', 'neutral', 'overbought'],
    'description': 'RSI momentum indicator'
})
```

### Customize Graph Structure

```python
graph = GraphStructure()
graph.build_default_structure()

# Add custom edge
graph.add_edge('custom_feature_state', 'future_return_state')

# Remove edge
graph.remove_edge('volume_to_sma_state', 'future_return_state')
```

## Monitoring

### Log PGM Predictions

```python
logger.info(f"PGM Prediction for {symbol}: {prediction} (confidence: {confidence:.2%})")
```

### Track Performance

```python
# Store predictions and actuals
predictions_log = []
for date, prediction, actual in zip(dates, predictions, actuals):
    predictions_log.append({
        'date': date,
        'prediction': prediction,
        'actual': actual,
        'correct': prediction == actual
    })

# Calculate rolling accuracy
accuracy = sum(p['correct'] for p in predictions_log[-100:]) / 100
```

## Troubleshooting

### Issue: "No data for symbol"

**Solution**: Ensure you've run `example_workflow.py` first to populate the feature store.

### Issue: Import errors

**Solution**: Install dependencies:
```bash
pip install networkx scikit-learn
```

### Issue: Slow inference

**Solution**: Use batch inference instead of single predictions:
```python
# Instead of loop
for row in df.iterrows():
    result = inference_engine.query(...)

# Use batch
results = inference_engine.batch_inference(df, query_vars, evidence_cols)
```

## Next Steps

1. ✅ Run `example_pgm_workflow.py`
2. ✅ Create `pgm_api.py` with endpoints
3. ✅ Update frontend with PGM components
4. ✅ Test end-to-end integration
5. ⬜ Deploy to production
6. ⬜ Monitor performance metrics
7. ⬜ Iterate on graph structure based on results

---

**Need Help?** Check `PGM_DOCUMENTATION.md` for detailed API reference.
