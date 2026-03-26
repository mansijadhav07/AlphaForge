# Improved Feature Discretization Module

## Overview

The discretization module provides flexible, data-driven methods for converting continuous features into discrete states for the Probabilistic Graphical Model (PGM).

## Key Improvements

### 1. Quantile-Based Binning
- **Equal frequency bins** instead of equal width
- Handles skewed distributions better
- Ensures balanced class distribution

### 2. Data-Driven Thresholds
- Thresholds learned from data statistics
- Adapts to data distribution
- No hardcoded values

### 3. Multiple Methods
- **Quantile**: Equal frequency bins
- **K-means**: Natural cluster detection
- **Threshold**: Fixed or data-driven thresholds
- **Equal-width**: Equal-sized intervals
- **Auto**: Automatic method selection

### 4. Configurable & Reusable
- Fit once, transform many times
- Consistent train/test discretization
- Configurable number of bins
- Custom labels

## Installation

The module is already included in the project:
```python
from pgm_model.discretization import (
    FeatureDiscretizer,
    DiscretizationConfig,
    discretize_quantile,
    discretize_kmeans,
    discretize_threshold,
    auto_discretize
)
```

## Quick Start

### Quantile-Based Binning
```python
import pandas as pd
from pgm_model.discretization import discretize_quantile

# Your data
volatility = pd.Series([0.01, 0.02, 0.03, ...], name='volatility')

# Discretize into 3 equal-frequency bins
result = discretize_quantile(volatility, n_bins=3, labels=['low', 'medium', 'high'])
```

### K-Means Clustering
```python
from pgm_model.discretization import discretize_kmeans

# Find natural clusters
result = discretize_kmeans(momentum, n_bins=3, labels=['weak', 'moderate', 'strong'])
```

### Threshold-Based
```python
from pgm_model.discretization import discretize_threshold

# RSI with standard thresholds
rsi_discrete = discretize_threshold(
    rsi,
    thresholds=[30, 70],
    labels=['oversold', 'neutral', 'overbought']
)
```

### Automatic Method Selection
```python
from pgm_model.discretization import auto_discretize

# Automatically choose best method
result, info = auto_discretize(feature, n_bins=3)
print(f"Selected method: {info['config']['method']}")
```

## Advanced Usage

### Reusable Discretizer (Train/Test Split)

```python
from pgm_model.discretization import FeatureDiscretizer, DiscretizationConfig

# Create discretizer
discretizer = FeatureDiscretizer()

# Configure
config = DiscretizationConfig(
    method='quantile',
    n_bins=3,
    labels=['low', 'medium', 'high']
)

# Fit on training data
discretizer.fit(train_df, 'volatility', config)

# Transform training data
train_discrete = discretizer.transform(train_df, 'volatility')

# Transform test data (using same thresholds!)
test_discrete = discretizer.transform(test_df, 'volatility')
```

### Data-Driven Thresholds

```python
# Calculate thresholds from data
mean = df['momentum'].mean()
std = df['momentum'].std()
thresholds = [mean - 0.5*std, mean + 0.5*std]

# Apply
config = DiscretizationConfig(
    method='threshold',
    n_bins=3,
    thresholds=thresholds,
    labels=['weak', 'moderate', 'strong']
)

result = discretizer.fit_transform(df, 'momentum', config)
```

### Get Bin Information

```python
# Fit discretizer
discretizer.fit(df, 'feature', config)

# Get bin edges
edges = discretizer.get_bin_edges('feature')
print(f"Bin edges: {edges}")

# Get detailed bin info
bin_info = discretizer.get_bin_info('feature')
print(bin_info)
# Output:
#    bin    label     lower     upper              range
#      0      low    0.0000   33.3333   (0.0000, 33.3333]
#      1   medium   33.3333   66.6667  (33.3333, 66.6667]
#      2     high   66.6667  100.0000  (66.6667, 100.0000]

# Get complete info
info = discretizer.get_feature_info('feature')
print(info['stats'])  # Statistics
print(info['config'])  # Configuration
```

## Methods Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Quantile** | Skewed distributions | Equal frequency, balanced classes | Bin edges vary with data |
| **K-means** | Natural clusters | Finds data patterns | Requires sklearn |
| **Threshold** | Domain knowledge | Interpretable, consistent | May be imbalanced |
| **Equal-width** | Uniform distributions | Simple, intuitive | Poor for skewed data |
| **Auto** | Unknown distributions | Adaptive | Less control |

## Financial Feature Examples

### RSI (Relative Strength Index)
```python
# Domain knowledge: 30/70 thresholds
config = DiscretizationConfig(
    method='threshold',
    n_bins=3,
    thresholds=[30, 70],
    labels=['oversold', 'neutral', 'overbought']
)
```

### Returns
```python
# Symmetric around zero
config = DiscretizationConfig(
    method='threshold',
    n_bins=3,
    thresholds=[-0.01, 0.01],
    labels=['negative', 'neutral', 'positive']
)
```

### Volatility
```python
# Data-driven quantiles
config = DiscretizationConfig(
    method='quantile',
    n_bins=3,
    labels=['low', 'medium', 'high']
)
```

### Volume Ratio
```python
# Natural clusters
config = DiscretizationConfig(
    method='kmeans',
    n_bins=3,
    labels=['low', 'normal', 'high']
)
```

## Integration with PGM

### Update State Encoder

The discretization module can be integrated with the existing `StateEncoder`:

```python
from pgm_model.state_encoding import StateEncoder
from pgm_model.discretization import FeatureDiscretizer, DiscretizationConfig

# Create encoder
encoder = StateEncoder()

# Create discretizer for data-driven thresholds
discretizer = FeatureDiscretizer()

# Fit discretizer on training data
for feature in ['volatility_10', 'atr_pct']:
    config = DiscretizationConfig(method='quantile', n_bins=3)
    discretizer.fit(train_df, feature, config)
    
    # Get learned thresholds
    thresholds = discretizer.fitted_configs[feature]['thresholds']
    
    # Update encoder with learned thresholds
    encoder.add_custom_rule(feature, {
        'type': 'threshold',
        'thresholds': thresholds,
        'labels': ['low', 'medium', 'high']
    })

# Now encode with learned thresholds
encoded_df = encoder.transform(df)
```

## Testing

Run tests:
```bash
pytest tests/test_discretization.py -v
```

Run examples:
```bash
python examples/discretization_example.py
```

## API Reference

### DiscretizationConfig

```python
@dataclass
class DiscretizationConfig:
    method: str  # 'quantile', 'kmeans', 'threshold', 'equal_width'
    n_bins: int = 3
    labels: Optional[List[str]] = None
    thresholds: Optional[List[float]] = None
    quantiles: Optional[List[float]] = None
```

### FeatureDiscretizer

```python
class FeatureDiscretizer:
    def fit(df, feature, config) -> Self
    def transform(df, feature, handle_unseen='nearest') -> pd.Series
    def fit_transform(df, feature, config) -> pd.Series
    def get_bin_edges(feature) -> List[float]
    def get_bin_info(feature) -> pd.DataFrame
    def get_feature_info(feature) -> Dict
```

### Convenience Functions

```python
discretize_quantile(series, n_bins=3, labels=None) -> pd.Series
discretize_kmeans(series, n_bins=3, labels=None) -> pd.Series
discretize_threshold(series, thresholds, labels=None) -> pd.Series
auto_discretize(series, n_bins=3, method='auto', labels=None) -> Tuple[pd.Series, Dict]
```

## Benefits

### 1. Better Model Performance
- Balanced class distribution
- Captures data patterns
- Reduces overfitting

### 2. Flexibility
- Multiple methods for different features
- Configurable bins
- Custom labels

### 3. Consistency
- Same discretization for train/test
- Reproducible results
- Reusable configurations

### 4. Interpretability
- Clear bin boundaries
- Meaningful labels
- Detailed bin information

## Migration Guide

### From Fixed Thresholds

**Before:**
```python
# Fixed thresholds
df['volatility_state'] = pd.cut(
    df['volatility'],
    bins=[0, 0.01, 0.03, np.inf],
    labels=['low', 'medium', 'high']
)
```

**After:**
```python
# Data-driven quantiles
from pgm_model.discretization import discretize_quantile

df['volatility_state'] = discretize_quantile(
    df['volatility'],
    n_bins=3,
    labels=['low', 'medium', 'high']
)
```

### From Manual Binning

**Before:**
```python
# Manual binning
def discretize_momentum(x):
    if x < -0.3:
        return 'weak'
    elif x < 0.3:
        return 'moderate'
    else:
        return 'strong'

df['momentum_state'] = df['momentum'].apply(discretize_momentum)
```

**After:**
```python
# Automatic with K-means
from pgm_model.discretization import discretize_kmeans

df['momentum_state'] = discretize_kmeans(
    df['momentum'],
    n_bins=3,
    labels=['weak', 'moderate', 'strong']
)
```

## Best Practices

1. **Use quantile binning for skewed distributions** (volatility, volume)
2. **Use threshold binning for domain knowledge** (RSI, returns)
3. **Use K-means for unknown distributions** (composite scores)
4. **Fit on training data, transform on test data** (avoid data leakage)
5. **Check bin distributions** (ensure no empty bins)
6. **Document discretization choices** (for reproducibility)

## Troubleshooting

### Empty Bins
```python
# Check bin distribution
result = discretizer.fit_transform(df, 'feature', config)
print(result.value_counts())

# If bins are empty, reduce n_bins or use different method
```

### Duplicate Thresholds
```python
# Happens with discrete data
# Discretizer automatically handles this by reducing n_bins
```

### Out-of-Range Values
```python
# Control with handle_unseen parameter
result = discretizer.transform(df, 'feature', handle_unseen='clip')
# Options: 'nearest', 'clip', 'nan'
```

## Future Enhancements

- [ ] Supervised discretization (using target variable)
- [ ] Multi-feature discretization
- [ ] Discretization quality metrics
- [ ] Visualization tools
- [ ] Integration with feature engineering pipeline

## References

- [Discretization in Machine Learning](https://en.wikipedia.org/wiki/Discretization_of_continuous_features)
- [Quantile-based Discretization](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.KBinsDiscretizer.html)
- [K-means Clustering](https://scikit-learn.org/stable/modules/clustering.html#k-means)

## Support

For issues or questions:
1. Check examples: `examples/discretization_example.py`
2. Run tests: `pytest tests/test_discretization.py -v`
3. Review documentation: This file

---

**Module**: `pgm_model/discretization.py`  
**Tests**: `tests/test_discretization.py`  
**Examples**: `examples/discretization_example.py`  
**Status**: ✓ Complete and tested
