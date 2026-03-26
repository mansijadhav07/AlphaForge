# Calibration Analysis UI Guide

## Overview
The Calibration Analysis page provides a comprehensive view of how well the PGM's predicted probabilities match actual outcomes. This is crucial for understanding when to trust the model's confidence levels.

## Accessing the Page
Navigate to: **http://localhost:3000/calibration**

## Page Sections

### 1. Header
- **Title**: "Probability Calibration"
- **Symbol Selector**: Dropdown to choose between AAPL, TSLA, GOOGL, MSFT
- **Description**: Brief explanation of calibration analysis

### 2. Overall Assessment Card
**Blue gradient card at the top**

Displays:
- Overall calibration quality statement
- Total samples analyzed
- Positive rate (actual frequency of positive outcomes)
- Mean predicted probability

**Example:**
```
"Model probabilities are highly reliable"
Total Samples: 500
Positive Rate: 51.0%
Mean Predicted: 52.0%
```

### 3. Calibration Metrics Cards

#### Expected Calibration Error (ECE) Card
- **Large number**: ECE percentage (e.g., 4.50%)
- **Quality badge**: Excellent/Good/Fair/Poor with color coding
  - Green: Excellent (< 5%)
  - Blue: Good (5-10%)
  - Yellow: Fair (10-15%)
  - Red: Poor (> 15%)
- **Description**: Human-readable interpretation
- **Reliability Score**: Overall calibration quality (higher is better)

#### Brier Score Card
- **Large number**: Brier score (e.g., 0.185)
- **Quality badge**: Similar color coding
- **Description**: Prediction accuracy assessment
- **Additional metrics**:
  - Log Loss
  - Maximum Calibration Error (MCE)

### 4. Calibration Curve Chart
**Interactive scatter plot**

**What it shows:**
- **X-axis**: Predicted Probability (0-100%)
- **Y-axis**: Actual Frequency (0-100%)
- **Diagonal dashed line**: Perfect calibration
- **Blue dots**: Actual model calibration

**How to interpret:**
- **Dots on the line**: Perfect calibration
- **Dots above line**: Model is under-confident
- **Dots below line**: Model is over-confident
- **Closer to line**: Better calibration

**Interaction:**
- Hover over points to see exact values
- Zoom and pan available

### 5. Calibration Bins Table
**Detailed bin-by-bin breakdown**

Columns:
- **Predicted Prob**: Mean predicted probability in this bin
- **Actual Freq**: Actual frequency of positive outcomes
- **Gap**: Absolute difference (color-coded)
  - Green: < 5% (good)
  - Yellow: 5-10% (fair)
  - Red: > 10% (poor)
- **Count**: Number of samples in bin
- **Confidence Interval**: 95% confidence range for actual frequency

**Example row:**
```
Predicted: 45.0% | Actual: 43.2% | Gap: 1.8% | Count: 52 | CI: [35.1%, 51.3%]
```

### 6. Understanding Calibration Info Card
**Blue info card at bottom**

Provides educational content:
- What calibration means
- How to interpret ECE
- What Brier score measures

## Color Coding

### Quality Badges
- **Green** (Excellent): Model performing very well
- **Blue** (Good): Model performing well
- **Yellow** (Fair): Model needs improvement
- **Red** (Poor): Model needs significant improvement

### Gap Colors in Table
- **Green text**: Small gap (< 5%)
- **Yellow text**: Medium gap (5-10%)
- **Red text**: Large gap (> 10%)

## Use Cases

### 1. Model Validation
**Question**: "Can I trust this model's probabilities?"

**Look at:**
- Overall assessment statement
- ECE quality badge
- Calibration curve proximity to diagonal

**Good signs:**
- ECE < 10%
- "Excellent" or "Good" quality badges
- Points clustered near diagonal line

### 2. Comparing Symbols
**Question**: "Which symbol has better calibrated predictions?"

**Steps:**
1. Select first symbol (e.g., AAPL)
2. Note the ECE and reliability score
3. Select second symbol (e.g., GOOGL)
4. Compare metrics

**Lower ECE = Better calibration**

### 3. Identifying Bias
**Question**: "Is the model systematically over/under-confident?"

**Look at:**
- Calibration curve pattern
- Bins table gaps

**Patterns:**
- **All points above line**: Under-confident (predicts too low)
- **All points below line**: Over-confident (predicts too high)
- **Mixed**: Good calibration or inconsistent bias

### 4. Confidence in Decisions
**Question**: "When should I trust a 70% prediction?"

**Look at:**
- Find the bin containing 70% predicted probability
- Check actual frequency in that bin
- Check confidence interval width

**Example:**
```
Predicted: 70% | Actual: 68% | CI: [62%, 74%]
→ Can trust 70% predictions (within 2% of actual)
```

## Tips for Interpretation

### ECE (Expected Calibration Error)
- **< 5%**: Excellent - Trust probabilities directly
- **5-10%**: Good - Probabilities are reliable
- **10-15%**: Fair - Use with caution
- **> 15%**: Poor - Don't trust raw probabilities

### Brier Score
- **< 0.10**: Excellent prediction accuracy
- **0.10-0.20**: Good accuracy
- **0.20-0.30**: Fair accuracy
- **> 0.30**: Poor accuracy

### Calibration Curve
- **Tight clustering near diagonal**: Well calibrated
- **Systematic deviation**: Consistent bias
- **Random scatter**: Inconsistent predictions
- **Wide confidence intervals**: Need more data

### Sample Size
- **> 500 samples**: Reliable analysis
- **200-500 samples**: Moderate reliability
- **< 200 samples**: Use with caution

## Common Questions

**Q: What's the difference between ECE and Brier score?**
A: ECE measures calibration (do probabilities match frequencies?), while Brier score measures overall accuracy (are predictions correct?). You can have good accuracy but poor calibration.

**Q: Why are some bins missing?**
A: Bins with no samples are excluded. This happens when the model rarely predicts certain probability ranges.

**Q: What if confidence intervals are very wide?**
A: Wide intervals indicate few samples in that bin. The actual frequency estimate is less reliable. Consider collecting more data.

**Q: Can calibration be too good?**
A: Not really, but ECE near 0% with very few samples might indicate overfitting to the validation set.

**Q: How often should I check calibration?**
A: Check calibration:
- After training a new model
- When deploying to production
- Periodically (monthly/quarterly) to detect drift
- After significant data distribution changes

## Troubleshooting

### "Insufficient data" error
- Need at least 100 samples for reliable calibration analysis
- Collect more historical data for the symbol

### All bins show similar probabilities
- Model might be outputting constant predictions
- Check model training and feature engineering

### Very high ECE (> 20%)
- Model is poorly calibrated
- Consider:
  - Recalibration techniques (Platt scaling)
  - Feature engineering
  - Different model architecture
  - More training data

## Next Steps

After reviewing calibration:
1. **Good calibration**: Deploy with confidence
2. **Fair calibration**: Consider recalibration methods
3. **Poor calibration**: Investigate model issues before deployment

## Related Pages
- **Model Evaluation** (`/model-evaluation`): Overall model performance
- **Baseline Comparison** (`/baseline-comparison`): Compare with baseline models
- **Feature Impact** (`/feature-impact`): Understand feature contributions
