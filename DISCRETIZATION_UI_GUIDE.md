# Discretization UI - Quick Guide

## ✓ UI Created!

A new frontend page has been created to visualize and compare different discretization methods.

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
Navigate to: **http://localhost:3000/discretization**

Or click **"Discretization"** in the navigation bar (between "Structure" and "Feature Impact")

## What You'll See

### 1. Feature Selector
Choose which feature to discretize:
- **Volatility** - Exponential distribution (skewed)
- **RSI** - Uniform distribution (0-100)
- **Return** - Normal distribution (centered at 0)
- **Momentum** - Bimodal distribution (two peaks)

### 2. Data Statistics
View statistics for 1000 sample data points:
- Min, Max, Mean, Median, Std, Q25, Q75

### 3. Discretization Methods
Compare 4 different methods:

**Quantile-Based** (Blue)
- Equal frequency bins
- Best for skewed distributions
- Ensures balanced classes

**K-Means Clustering** (Purple)
- Natural cluster detection
- Best for unknown distributions
- Finds data patterns

**Equal-Width** (Green)
- Equal-sized intervals
- Best for uniform distributions
- Simple and intuitive

**Threshold-Based** (Orange)
- Fixed or data-driven thresholds
- Best for domain knowledge
- Interpretable boundaries

### 4. Selected Method Details

**Thresholds**
- See the exact threshold values used to split the data

**Bin Information Table**
- Bin number and label
- Lower and upper bounds
- Range notation
- Count and percentage of samples in each bin

**Distribution Visualization**
- Visual bar chart showing distribution across bins
- Percentage of samples in each bin
- Color-coded by method

### 5. Method Comparison Table
Quick reference showing:
- Method name and description
- Number of bins
- Best use case

## Interactive Features

### Switch Features
Click different feature buttons to see how methods perform on different data distributions:
- Volatility shows quantile working best (skewed data)
- RSI shows all methods working similarly (uniform data)
- Momentum shows K-means finding natural clusters (bimodal data)

### Switch Methods
Click different method buttons to compare:
- See how thresholds differ
- Compare bin distributions
- Understand which method creates balanced bins

## Example Insights

### Volatility (Exponential/Skewed)
- **Quantile**: Creates balanced bins (33%, 33%, 33%)
- **Equal-width**: Creates imbalanced bins (80%, 15%, 5%)
- **Recommendation**: Use quantile for balanced classes

### RSI (Uniform)
- **All methods**: Work similarly well
- **Threshold**: Uses domain knowledge (30/70)
- **Recommendation**: Use threshold for interpretability

### Return (Normal)
- **Quantile**: Balanced bins
- **Threshold**: Symmetric around zero (-0.01, 0.01)
- **Recommendation**: Use threshold for financial meaning

### Momentum (Bimodal)
- **K-means**: Finds two natural clusters
- **Quantile**: Splits clusters artificially
- **Recommendation**: Use K-means to preserve patterns

## API Endpoints

The page uses these new endpoints:

### GET /api/discretization/demo
```bash
curl 'http://localhost:8000/api/discretization/demo?feature=volatility&n_samples=1000'
```

Returns:
- Feature statistics
- Histogram data
- 4 discretization methods with thresholds, bins, and distributions

### GET /api/discretization/compare
```bash
curl 'http://localhost:8000/api/discretization/compare?n_bins=3'
```

Returns:
- Comparison across different data distributions
- Balance scores for each method
- Recommendations

## Files Created/Modified

### New Files
- `api/discretization_routes.py` - API endpoints
- `frontend/app/discretization/page.tsx` - UI page
- `DISCRETIZATION_UI_GUIDE.md` - This guide

### Modified Files
- `api_server.py` - Added discretization router
- `frontend/components/layout/navbar.tsx` - Added "Discretization" link

## Navigation

The page is accessible from:
1. **Navbar**: Click "Discretization" (Layers icon)
2. **Direct URL**: http://localhost:3000/discretization
3. **From any page**: Use the navigation bar at the top

## Troubleshooting

### "Failed to fetch discretization demo"
- Make sure API server is running: `python3 api_server.py`
- Make sure you restarted the server after adding the endpoint
- Check API is accessible: `curl http://localhost:8000/api/discretization/demo?feature=volatility`

### Page not found
- Make sure frontend is built: `cd frontend && npm run build`
- Or run in dev mode: `cd frontend && npm run dev`

### No data showing
- Check browser console (F12) for errors
- Verify API endpoint works in browser: http://localhost:8000/docs
- Look for "Discretization Demo" endpoint

## Educational Value

This page helps you understand:

1. **Why quantile binning is better** - See balanced vs imbalanced distributions
2. **When to use each method** - Compare performance on different data types
3. **How thresholds are learned** - See data-driven vs fixed thresholds
4. **Impact on model performance** - Balanced bins = better model performance

## Use Cases

### For Data Scientists
- Understand discretization trade-offs
- Choose best method for your features
- Validate discretization choices

### For Developers
- See how the discretization module works
- Understand API responses
- Integrate discretization into pipelines

### For Stakeholders
- Visualize feature engineering
- Understand model preprocessing
- See data-driven decisions

## Next Steps (Optional)

### Enhancements
- [ ] Add custom threshold input
- [ ] Add file upload for custom data
- [ ] Add download discretization config
- [ ] Add comparison across multiple features
- [ ] Add histogram overlay with bin boundaries

### Integration
- [ ] Link from feature engineering page
- [ ] Add to model training workflow
- [ ] Export discretization rules

## Summary

You now have a complete UI to explore and understand feature discretization! The page provides:
- Interactive feature selection
- Method comparison
- Visual distribution analysis
- Educational insights

Visit **http://localhost:3000/discretization** to see it in action!

---

**Remember**: Restart the API server first to load the new endpoint!
```bash
# Stop server (Ctrl+C), then:
source venv/bin/activate
python3 api_server.py
```
