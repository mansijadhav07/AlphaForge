# Structure Analysis UI - Quick Guide

## ✓ Implementation Complete

A new frontend page has been created to visualize the Bayesian Network structure analysis.

## How to View in UI

### Step 1: Restart API Server
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
Navigate to: **http://localhost:3000/structure-analysis**

Or click **"Structure"** in the navigation bar (between "PGM Graph" and "Feature Impact")

## What You'll See

### 1. Network Summary Cards (Top)
- **Total Nodes**: 11 nodes in the network
- **Total Edges**: 13 connections
- **DAG Status**: Valid/Invalid (should be Valid)
- **Cycles**: None (should be None)

### 2. Structure Validation
Text summary confirming the network is a valid DAG with empirical support

### 3. Correlation Matrix (Heatmap)
- Interactive heatmap showing correlations between all features
- **Green**: Positive correlation
- **Red**: Negative correlation  
- **Blue**: Self-correlation (1.0)
- Hover over cells to see exact values
- Uses Pearson correlation by default

### 4. Edge Explanations (13 edges)
Each edge shows:
- **Parent → Child** relationship (e.g., RSI → momentum_regime)
- **Strength badge**: Strong/Medium/Weak (color-coded)
- **Edge type**: Category (momentum_indicator, volatility_indicator, etc.)
- **Reasoning**: Brief explanation

**Click any edge** to expand and see:
- **Financial Theory**: Theoretical foundation
- **Empirical Support**: Data-driven evidence
- **Causal Mechanism**: How parent influences child

## Example Edges You'll See

1. **RSI → momentum_regime** (Strong)
   - Type: momentum_indicator
   - Explains how RSI determines momentum classification

2. **MACD → momentum_regime** (Strong)
   - Type: momentum_indicator
   - Explains MACD's role in momentum detection

3. **BB_width → volatility_regime** (Strong)
   - Type: volatility_indicator
   - Explains Bollinger Band width's role in volatility classification

4. **momentum_regime → return_target** (Strong)
   - Type: regime_influence
   - Explains how momentum affects returns

... and 9 more edges with detailed explanations!

## Features

### Interactive Elements
- Click edge cards to expand/collapse detailed explanations
- Hover over correlation cells for exact values
- Color-coded strength badges (green=strong, yellow=medium, orange=weak)

### Visual Design
- Premium glassmorphism cards
- Gradient text headers
- Color-coded correlation heatmap
- Responsive layout (works on mobile)

### Data Insights
- See which features are most correlated
- Understand why each edge exists in the network
- Validate the network structure (DAG, no cycles)
- Learn the financial theory behind each connection

## Navigation

The page is accessible from:
1. **Navbar**: Click "Structure" (GitBranch icon)
2. **Direct URL**: http://localhost:3000/structure-analysis
3. **From any page**: Use the navigation bar at the top

## Files Created/Modified

### New Files
- `frontend/app/structure-analysis/page.tsx` - Main page component
- `STRUCTURE_UI_GUIDE.md` - This guide

### Modified Files
- `frontend/components/layout/navbar.tsx` - Added "Structure" link

## Troubleshooting

### "Failed to fetch structure analysis"
- Make sure API server is running: `python3 api_server.py`
- Make sure you restarted the server after adding the endpoint
- Check API is accessible: `curl http://localhost:8000/api/pgm/health`

### Page not found
- Make sure frontend is built: `cd frontend && npm run build`
- Or run in dev mode: `cd frontend && npm run dev`

### No data showing
- Check browser console (F12) for errors
- Verify API endpoint: `curl 'http://localhost:8000/api/pgm/structure-analysis?symbol=AAPL'`

## Next Steps (Optional)

### Enhancements
- Add symbol selector to analyze different stocks
- Add correlation method selector (Pearson/Spearman/Kendall)
- Add network topology visualization (graph diagram)
- Add export functionality (download as PDF/CSV)
- Add comparison view (compare structures for different symbols)

### Integration
- Link from PGM Graph page to Structure Analysis
- Add "Learn More" buttons on edge cards
- Add tooltips with additional context
- Add search/filter for edges

## Summary

You now have a complete UI to explore and understand the Bayesian Network structure! The page provides:
- Visual correlation heatmap
- Detailed edge explanations with financial theory
- Structure validation results
- Interactive exploration of the network design

Visit **http://localhost:3000/structure-analysis** to see it in action!
