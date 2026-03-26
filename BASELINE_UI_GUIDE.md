# Baseline Comparison UI - Quick Guide

## ✓ UI Created!

A new frontend page has been created to visualize baseline model comparison.

## How to View in UI

### Step 1: Restart API Server (to load new endpoint)
```bash
# Stop the current server (Ctrl+C in the terminal running api_server.py)
# Then restart:
source venv/bin/activate
python3 api_server.py
```

### Step 2: Start Frontend (if not running)
```bash
cd frontend
npm run dev
```

### Step 3: Open in Browser
Navigate to: **http://localhost:3000/baseline-comparison**

Or click **"Baselines"** in the navigation bar (between "Discretization" and "Feature Impact")

## What You'll See

### 1. Symbol Selector
Choose which stock to analyze:
- AAPL, TSLA, GOOGL, MSFT

### 2. Winner Card
Prominent display of the best performing model:
- Model name (e.g., "PGM (Bayesian Network)")
- Accuracy and F1 Score
- Improvement over random baseline

### 3. Performance Summary (3 Cards)
Quick comparison showing improvement:
- **vs Random Baseline**: +46% (absolute improvement)
- **vs Majority Baseline**: +29% (over naive strategy)
- **vs Logistic Regression**: +9% (over ML baseline)

### 4. Model Cards (4 Models)
Interactive cards for each model:
- **Random** - Uniform random predictions (gray)
- **Majority Class** - Always predict most common (yellow)
- **Logistic Regression** - Linear classifier (blue)
- **PGM (Bayesian Network)** - Probabilistic model (purple, with trophy)

Each card shows:
- Accuracy (large number)
- Precision, Recall, F1 Score
- Log Loss
- Winner badge (for best model)

### 5. Detailed Metrics Table
Comprehensive comparison table with:
- All metrics side-by-side
- Training and prediction times
- Winner highlighted
- Sorted by accuracy

### 6. Confusion Matrix
Click any model card to see its confusion matrix:
- 3x3 matrix (Negative, Neutral, Positive)
- Diagonal (green) = correct predictions
- Off-diagonal (red) = errors
- Shows where model makes mistakes

### 7. Interpretation Guide
Educational section explaining:
- **Model Descriptions**: What each model does
- **Performance Ranges**: What accuracy levels mean
  - < 40%: Worse than random
  - 40-55%: Weak signal
  - 55-70%: Moderate
  - 70-85%: Good
  - > 85%: Excellent

## Interactive Features

### Switch Symbols
Click different symbol buttons to see how models perform on different stocks

### Select Models
Click model cards to view their confusion matrices

### Compare Metrics
Use the detailed table to compare all metrics at once

## Example Insights

### Typical Results

**Random Baseline**
- Accuracy: 33% (1/3 for 3-class problem)
- Shows absolute minimum performance
- Any model should beat this

**Majority Class**
- Accuracy: 50% (if classes are balanced)
- Simple but surprisingly effective
- Hard to beat if data is imbalanced

**Logistic Regression**
- Accuracy: 70%
- Standard ML baseline
- Fast and interpretable

**PGM (Bayesian Network)**
- Accuracy: 79% ✓
- Best performer
- Captures non-linear patterns and dependencies

### What This Tells You

**PGM Improvement**:
- +46% over random → PGM is learning meaningful patterns
- +29% over majority → PGM is better than naive strategy
- +9% over LR → PGM's complexity is justified

**When PGM Wins**:
- Non-linear relationships exist
- Feature dependencies matter
- Probabilistic reasoning adds value

**When LR Might Win**:
- Linear relationships dominate
- Simple patterns sufficient
- Limited data available

## Visual Elements

### Color Coding
- **Purple**: PGM (Bayesian Network) - winner
- **Blue**: Logistic Regression - ML baseline
- **Yellow**: Majority Class - naive baseline
- **Gray**: Random - absolute minimum

### Icons
- **Trophy**: Winner badge
- **Award**: Improvement metrics
- **Target**: Logistic Regression
- **TrendingUp**: Majority Class
- **Zap**: Random

### Badges
- Winner badge on best model
- Color-coded model names
- Metric badges

## API Endpoint

The page uses:
```
GET /api/pgm/baseline-comparison/{symbol}
```

Example:
```bash
curl http://localhost:8000/api/pgm/baseline-comparison/AAPL
```

## Files Created/Modified

### New Files
- `frontend/app/baseline-comparison/page.tsx` - UI page
- `BASELINE_UI_GUIDE.md` - This guide

### Modified Files
- `frontend/components/layout/navbar.tsx` - Added "Baselines" link

## Navigation

The page is accessible from:
1. **Navbar**: Click "Baselines" (Scale icon)
2. **Direct URL**: http://localhost:3000/baseline-comparison
3. **From any page**: Use the navigation bar at the top

## Troubleshooting

### "Failed to fetch baseline comparison"
- Make sure API server is running: `python3 api_server.py`
- Make sure you restarted the server after adding the endpoint
- Check API is accessible: `curl http://localhost:8000/api/pgm/baseline-comparison/AAPL`

### Page not found
- Make sure frontend is built: `cd frontend && npm run build`
- Or run in dev mode: `cd frontend && npm run dev`

### No data showing
- Check browser console (F12) for errors
- Verify API endpoint works: http://localhost:8000/docs
- Look for "Compare PGM with Baseline Models" endpoint

## Educational Value

This page helps you understand:

1. **PGM Performance Context** - Is 70% accuracy good? (Depends on baseline!)
2. **Model Comparison** - How much better is PGM than simple models?
3. **Justification** - Does the PGM's complexity provide value?
4. **Error Analysis** - Where does each model make mistakes?

## Use Cases

### For Data Scientists
- Validate PGM performance
- Understand model improvements
- Identify areas for improvement

### For Developers
- See API response format
- Understand metrics
- Debug model issues

### For Stakeholders
- Visualize model value
- Understand performance gains
- See ROI of complex modeling

## Next Steps (Optional)

### Enhancements
- [ ] Add ROC curves
- [ ] Add precision-recall curves
- [ ] Add learning curves
- [ ] Add feature importance comparison
- [ ] Add statistical significance tests

### Integration
- [ ] Link from model evaluation page
- [ ] Add to dashboard
- [ ] Export comparison report

## Summary

You now have a complete UI to compare PGM performance against baseline models! The page provides:
- Visual performance comparison
- Detailed metrics
- Confusion matrices
- Educational interpretation guide

Visit **http://localhost:3000/baseline-comparison** to see it in action!

---

**Remember**: Restart the API server first to load the new endpoint!
```bash
# Stop server (Ctrl+C), then:
source venv/bin/activate
python3 api_server.py
```
