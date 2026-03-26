# Baseline Models for PGM Comparison

## Overview

The baseline models module provides simple comparison models to demonstrate the value of the Probabilistic Graphical Model (PGM) approach. By comparing against well-known baselines, we can quantify the improvement that the PGM provides.

## Why Baseline Comparison?

**"How do we know the PGM is actually good?"**

Without baselines, we can't answer this question. Baseline models provide:

1. **Context** - Is 70% accuracy good? (Depends on the baseline!)
2. **Validation** - Ensures the PGM is learning meaningful patterns
3. **Justification** - Demonstrates the value of the complex approach
4. **Debugging** - If PGM performs worse than simple baselines, something is wrong

## Baseline Models

### 1. Random Baseline

**Description**: Predicts classes with uniform random probability.

**Purpose**: Absolute minimum performance - any model should beat this.

**Expected Performance**: ~33% accuracy for 3-class problem

```python
from pgm_model.baseline_models import RandomBaseline

model = RandomBaseline()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

**When to use**: 
- Sanity check
- Verify data isn't completely random

### 2. Majority Class Baseline

**Description**: Always predicts the most common class.

**Purpose**: Simple but often surprisingly effective baseline.

**Expected Performance**: Depends on class imbalance (e.g., 50% if balanced, 80% if 80/20 split)

```python
from pgm_model.baseline_models import MajorityBaseline

model = MajorityBaseline()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

**When to use**:
- Check for class imbalance
- Minimum "smart" baseline

### 3. Logistic Regression

**Description**: Simple linear classifier.

**Purpose**: Standard ML baseline - fast, interpretable, often effective.

**Expected Performance**: 60-75% accuracy for moderately complex problems

```python
from pgm_model.baseline_models import LogisticRegressionBaseline

model = LogisticRegressionBaseline()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)
```

**When to use**:
- Standard ML comparison
- Check if linear relationships exist

## Comparison Framework

### BaselineComparison Class

Comprehensive comparison framework:

```python
from pgm_model.baseline_models import BaselineComparison

# Initialize
comparison = BaselineComparison()

# Add models
comparison.add_model('Random', RandomBaseline())
comparison.add_model('Majority', MajorityBaseline())
comparison.add_model('Logistic Regression', LogisticRegressionBaseline())

# Run comparison
results = comparison.compare_all(X_train, y_train, X_test, y_test)

# Get summary
summary_df = comparison.get_comparison_summary()
print(summary_df)

# Get best model
best_name, best_metrics = comparison.get_best_model('accuracy')
print(f"Best model: {best_name} with accuracy {best_metrics.accuracy:.4f}")
```

### Metrics Provided

For each model:
- **Accuracy**: Overall correctness
- **Precision**: Positive predictive value
- **Recall**: Sensitivity
- **F1 Score**: Harmonic mean of precision and recall
- **Log Loss**: Probabilistic loss (if probabilities available)
- **Confusion Matrix**: Detailed error analysis
- **Training Time**: Time to fit model
- **Prediction Time**: Time to make predictions

## Quick Start

### Simple Comparison

```python
from pgm_model.baseline_models import create_baseline_comparison
from sklearn.model_selection import train_test_split

# Prepare data
X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.3, random_state=42
)

# Run comparison
results = create_baseline_comparison(
    X_train, y_train, X_test, y_test
)

# View results
print(f"Best model: {results['best_model']['name']}")
print(f"Accuracy: {results['best_model']['accuracy']:.4f}")

# View summary
import pandas as pd
summary_df = pd.DataFrame(results['summary'])
print(summary_df)
```

### Include PGM in Comparison

```python
# Get PGM predictions
pgm_predictions = pgm_model.predict(X_test)

# Run comparison with PGM
results = create_baseline_comparison(
    X_train, y_train, X_test, y_test,
    include_pgm=True,
    pgm_predictions=pgm_predictions
)

# Compare
print(f"PGM Accuracy: {results['results']['PGM (Bayesian Network)'].accuracy:.4f}")
print(f"Logistic Regression Accuracy: {results['results']['Logistic Regression'].accuracy:.4f}")
print(f"Improvement: {results['results']['PGM (Bayesian Network)'].accuracy - results['results']['Logistic Regression'].accuracy:.4f}")
```

## API Usage

### Endpoint

```
GET /api/pgm/baseline-comparison/{symbol}
```

### Example Request

```bash
curl http://localhost:8000/api/pgm/baseline-comparison/AAPL
```

### Example Response

```json
{
  "symbol": "AAPL",
  "timestamp": "2026-03-26T10:30:00",
  "models": {
    "Random": {
      "model_name": "Random",
      "accuracy": 0.33,
      "precision": 0.33,
      "recall": 0.33,
      "f1_score": 0.33,
      "log_loss": 1.10,
      "confusion_matrix": [[10, 12, 11], [11, 10, 12], [12, 11, 10]],
      "training_time": 0.001,
      "prediction_time": 0.001
    },
    "Majority Class": {
      "model_name": "Majority Class",
      "accuracy": 0.50,
      "precision": 0.25,
      "recall": 0.50,
      "f1_score": 0.33,
      "log_loss": null,
      "confusion_matrix": [[0, 0, 0], [0, 50, 0], [0, 50, 0]],
      "training_time": 0.001,
      "prediction_time": 0.001
    },
    "Logistic Regression": {
      "model_name": "Logistic Regression",
      "accuracy": 0.70,
      "precision": 0.69,
      "recall": 0.70,
      "f1_score": 0.69,
      "log_loss": 0.75,
      "confusion_matrix": [[18, 8, 7], [6, 25, 2], [3, 4, 27]],
      "training_time": 0.15,
      "prediction_time": 0.01
    },
    "PGM (Bayesian Network)": {
      "model_name": "PGM (Bayesian Network)",
      "accuracy": 0.79,
      "precision": 0.78,
      "recall": 0.79,
      "f1_score": 0.78,
      "log_loss": null,
      "confusion_matrix": [[22, 6, 5], [5, 28, 0], [2, 3, 29]],
      "training_time": 2.5,
      "prediction_time": 0.05
    }
  },
  "summary": [
    {
      "Model": "PGM (Bayesian Network)",
      "Accuracy": 0.79,
      "Precision": 0.78,
      "Recall": 0.79,
      "F1 Score": 0.78,
      "Log Loss": null,
      "Training Time (s)": 2.5,
      "Prediction Time (s)": 0.05
    },
    ...
  ],
  "best_model": {
    "name": "PGM (Bayesian Network)",
    "accuracy": 0.79,
    "f1_score": 0.78
  },
  "winner": "PGM (Bayesian Network)",
  "improvement_over_random": 0.46,
  "improvement_over_majority": 0.29
}
```

## Interpretation Guide

### Accuracy Ranges

| Accuracy | Interpretation |
|----------|---------------|
| < 0.40 | Worse than random - something is wrong |
| 0.40-0.55 | Slightly better than random - weak signal |
| 0.55-0.70 | Moderate performance - learning patterns |
| 0.70-0.85 | Good performance - strong patterns |
| > 0.85 | Excellent performance - very strong patterns |

### Comparison Insights

**PGM vs Random**
- Shows absolute improvement
- Should be large (>0.30 for 3-class problem)

**PGM vs Majority**
- Shows improvement over naive strategy
- Should be positive (>0.10)

**PGM vs Logistic Regression**
- Shows value of complex modeling
- Positive = PGM captures non-linear patterns
- Negative = Linear relationships dominate (PGM may be overkill)

### When PGM Should Win

PGM should outperform baselines when:
1. **Non-linear relationships** exist between features
2. **Feature dependencies** are important
3. **Probabilistic reasoning** adds value
4. **Domain structure** (graph) captures real relationships

### When Logistic Regression Might Win

Logistic Regression might win when:
1. **Linear relationships** dominate
2. **Simple patterns** are sufficient
3. **Limited data** available (PGM needs more data)
4. **Speed** is critical (LR is much faster)

## Testing

Run tests:
```bash
pytest tests/test_baseline_models.py -v
```

## Integration with PGM

### In Training Pipeline

```python
# After training PGM
from pgm_model.baseline_models import create_baseline_comparison

# Compare performance
results = create_baseline_comparison(
    X_train, y_train, X_test, y_test,
    include_pgm=True,
    pgm_predictions=pgm.predict(X_test)
)

# Log results
logger.info(f"PGM Accuracy: {results['results']['PGM (Bayesian Network)'].accuracy:.4f}")
logger.info(f"Improvement over LR: {results['results']['PGM (Bayesian Network)'].accuracy - results['results']['Logistic Regression'].accuracy:.4f}")

# Save comparison
with open('model_comparison.json', 'w') as f:
    json.dump(results['summary'], f, indent=2)
```

### In Model Selection

```python
# Compare multiple PGM configurations
from pgm_model.baseline_models import BaselineComparison

comparison = BaselineComparison()

# Add baselines
comparison.add_model('Random', RandomBaseline())
comparison.add_model('Logistic Regression', LogisticRegressionBaseline())

# Add PGM variants
comparison.add_model('PGM (3 bins)', pgm_3bins)
comparison.add_model('PGM (5 bins)', pgm_5bins)
comparison.add_model('PGM (quantile)', pgm_quantile)

# Compare
results = comparison.compare_all(X_train, y_train, X_test, y_test)

# Select best
best_name, best_metrics = comparison.get_best_model('f1_score')
print(f"Best configuration: {best_name}")
```

## Best Practices

1. **Always include baselines** - Never report PGM performance in isolation
2. **Use multiple baselines** - Random, Majority, and Logistic Regression minimum
3. **Report multiple metrics** - Accuracy alone is insufficient
4. **Check confusion matrices** - Understand error patterns
5. **Consider training time** - PGM should justify its complexity
6. **Use proper train/test split** - Avoid data leakage
7. **Stratify splits** - Maintain class balance in train/test

## Common Issues

### Issue: PGM worse than Logistic Regression

**Possible causes**:
- Insufficient training data
- Poor discretization
- Incorrect graph structure
- Overfitting

**Solutions**:
- Collect more data
- Improve discretization (use quantile binning)
- Simplify graph structure
- Add regularization

### Issue: All models perform similarly

**Possible causes**:
- Weak signal in data
- Features not predictive
- Target variable noisy

**Solutions**:
- Feature engineering
- Collect better features
- Check data quality

### Issue: All models worse than majority baseline

**Possible causes**:
- Severe class imbalance
- Features not informative
- Data leakage in majority baseline

**Solutions**:
- Balance classes (resampling)
- Feature selection
- Check evaluation methodology

## Files

- **Module**: `pgm_model/baseline_models.py`
- **Tests**: `tests/test_baseline_models.py`
- **API**: `api/pgm_routes.py` (baseline-comparison endpoint)
- **Schemas**: `api/schemas.py` (BaselineComparisonResponse)
- **Documentation**: This file

## References

- [Scikit-learn Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Baseline Models in ML](https://machinelearningmastery.com/how-to-develop-a-baseline-model-for-classification/)
- [Model Comparison Best Practices](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6279924/)

---

**Status**: ✓ Complete and tested
