# Probability Calibration Module

## Overview

The Calibration module provides comprehensive analysis of how well the PGM's predicted probabilities match actual outcomes. Well-calibrated models are essential for reliable decision-making, as they ensure that predicted probabilities accurately reflect real-world frequencies.

## What is Calibration?

Calibration measures whether predicted probabilities match observed frequencies. For example:
- If a model predicts 70% probability for an event, it should occur approximately 70% of the time
- A well-calibrated model's predictions can be directly interpreted as confidence levels
- Poor calibration means probabilities are systematically over or under-confident

## Features

### 1. Calibration Curves
- Visual representation of predicted vs actual frequencies
- Binned analysis across probability ranges
- Confidence intervals for each bin
- Comparison against perfect calibration line

### 2. Reliability Diagrams
- Graphical assessment of calibration quality
- Gap analysis between predictions and reality
- Sample distribution across probability bins

### 3. Calibration Metrics

#### Expected Calibration Error (ECE)
- Average difference between predicted and actual frequencies
- Weighted by number of samples in each bin
- Range: 0 (perfect) to 1 (worst)
- **Interpretation:**
  - < 0.05: Excellent calibration
  - 0.05-0.10: Good calibration
  - 0.10-0.15: Fair calibration
  - > 0.15: Poor calibration

#### Maximum Calibration Error (MCE)
- Worst-case calibration error across all bins
- Identifies regions of poorest calibration
- More sensitive to outliers than ECE

#### Brier Score
- Measures accuracy of probabilistic predictions
- Mean squared error between predictions and outcomes
- Range: 0 (perfect) to 1 (worst)
- **Interpretation:**
  - < 0.10: Excellent
  - 0.10-0.20: Good
  - 0.20-0.30: Fair
  - > 0.30: Poor

#### Log Loss
- Penalizes confident wrong predictions heavily
- Lower is better
- Commonly used for model comparison

#### Reliability Score
- Computed as 1 - ECE
- Higher is better (1 = perfect)
- Easy-to-interpret overall metric

## Module Structure

```python
pgm_model/calibration.py
├── ProbabilityCalibration      # Main calibration analyzer
├── CalibrationBin              # Single bin data structure
├── CalibrationMetrics          # Metrics container
└── create_calibration_analysis # Convenience function
```

## Usage

### Basic Usage

```python
from pgm_model.calibration import create_calibration_analysis
import numpy as np

# Your predictions and true labels
y_true = np.array([0, 1, 1, 0, 1, ...])  # Binary outcomes
y_prob = np.array([0.2, 0.8, 0.7, 0.3, 0.9, ...])  # Predicted probabilities

# Create complete analysis
analysis = create_calibration_analysis(y_true, y_prob, n_bins=10)

# Access results
print(f"ECE: {analysis['calibration_curve']['metrics']['ece']:.4f}")
print(f"Reliability: {analysis['calibration_curve']['metrics']['reliability_score']:.2%}")
print(f"Overall: {analysis['interpretation']['overall']}")
```

### Advanced Usage

```python
from pgm_model.calibration import ProbabilityCalibration

# Initialize calibrator
calibrator = ProbabilityCalibration(n_bins=10)

# Compute calibration curve
bins, metrics = calibrator.compute_calibration_curve(
    y_true, 
    y_prob,
    strategy='uniform'  # or 'quantile'
)

# Get reliability diagram data
diagram_data = calibrator.compute_reliability_diagram_data(y_true, y_prob)

# Compare multiple models
models_data = {
    'PGM': (y_true, y_prob_pgm),
    'Logistic Regression': (y_true, y_prob_lr),
    'Random Forest': (y_true, y_prob_rf)
}
comparison_df = calibrator.compare_calibration(models_data)
print(comparison_df)
```

### Multiclass Calibration

```python
# For multiclass problems
y_true = np.array([0, 1, 2, 0, 1, ...])  # Class labels
y_prob = np.array([
    [0.7, 0.2, 0.1],  # Probabilities for sample 1
    [0.1, 0.8, 0.1],  # Probabilities for sample 2
    ...
])

results = calibrator.analyze_multiclass_calibration(
    y_true, 
    y_prob,
    class_names=['Negative', 'Neutral', 'Positive']
)

for class_name, (bins, metrics) in results.items():
    print(f"{class_name}: ECE = {metrics.expected_calibration_error:.4f}")
```

## API Endpoint

### GET /api/pgm/calibration/{symbol}

Returns calibration analysis for a specific symbol.

**Response:**
```json
{
  "symbol": "AAPL",
  "timestamp": "2026-03-26T11:00:00",
  "calibration_curve": {
    "bins": [
      {
        "predicted_prob": 0.15,
        "actual_freq": 0.14,
        "count": 52,
        "confidence_lower": 0.08,
        "confidence_upper": 0.20
      },
      ...
    ],
    "metrics": {
      "ece": 0.045,
      "mce": 0.082,
      "brier_score": 0.185,
      "log_loss": 0.512,
      "reliability_score": 0.955
    }
  },
  "interpretation": {
    "ece": {
      "quality": "Excellent",
      "description": "Model is very well calibrated",
      "value": 0.045
    },
    "brier": {
      "quality": "Good",
      "description": "Brier score of 0.185",
      "value": 0.185
    },
    "overall": "Model probabilities are highly reliable"
  }
}
```

## Frontend UI

Access the calibration analysis at: `http://localhost:3000/calibration`

**Features:**
- Symbol selector for different stocks
- Overall assessment card with key metrics
- ECE and Brier score cards with quality badges
- Interactive calibration curve chart
- Detailed bin-by-bin analysis table
- Educational information about calibration

## Interpretation Guide

### ECE Quality Levels

| ECE Range | Quality | Meaning |
|-----------|---------|---------|
| < 0.05 | Excellent | Model is very well calibrated |
| 0.05-0.10 | Good | Model has good calibration |
| 0.10-0.15 | Fair | Model calibration could be improved |
| > 0.15 | Poor | Model is poorly calibrated |

### Brier Score Quality Levels

| Brier Score | Quality | Meaning |
|-------------|---------|---------|
| < 0.10 | Excellent | Very accurate predictions |
| 0.10-0.20 | Good | Good prediction accuracy |
| 0.20-0.30 | Fair | Moderate prediction accuracy |
| > 0.30 | Poor | Poor prediction accuracy |

### Calibration Curve Interpretation

- **Points on diagonal**: Perfect calibration
- **Points above diagonal**: Model is under-confident (predicts lower probabilities than actual)
- **Points below diagonal**: Model is over-confident (predicts higher probabilities than actual)
- **Tight confidence intervals**: More reliable estimates
- **Wide confidence intervals**: Less reliable (fewer samples)

## Improving Calibration

If your model shows poor calibration:

1. **Platt Scaling**: Fit a logistic regression on validation set
2. **Isotonic Regression**: Non-parametric calibration method
3. **Temperature Scaling**: Scale logits before softmax
4. **Collect more data**: Especially in poorly calibrated regions
5. **Feature engineering**: Add features that improve probability estimates

## Testing

Run calibration tests:
```bash
pytest tests/test_calibration.py -v
```

**Test Coverage:**
- Perfect calibration scenarios
- Poor calibration scenarios
- Uniform and quantile binning
- Confidence interval computation
- Multiclass calibration
- Edge cases (empty bins, extreme probabilities)

## References

- Guo et al. (2017): "On Calibration of Modern Neural Networks"
- Niculescu-Mizil & Caruana (2005): "Predicting Good Probabilities with Supervised Learning"
- Brier (1950): "Verification of Forecasts Expressed in Terms of Probability"

## Best Practices

1. **Always check calibration** before deploying probabilistic models
2. **Use ECE as primary metric** for calibration quality
3. **Examine calibration curves visually** to identify systematic biases
4. **Monitor calibration over time** as data distribution shifts
5. **Calibrate on separate validation set** to avoid overfitting
6. **Consider domain requirements** - some applications need better calibration than others
