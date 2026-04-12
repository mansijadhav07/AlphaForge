# Feature Intelligence Page

## Overview

The **Feature Intelligence** page provides a comprehensive visualization of how raw stock market data is transformed into model-ready features for the Bayesian Network. This educational interface helps users understand the complete data pipeline.

## Page Structure

### 1. Header Section
- **Title**: "Feature Intelligence"
- **Subtitle**: "From Raw Data to Model Input - Visualizing the Feature Engineering Pipeline"
- **Ticker Selector**: Quick toggle between AAPL, TSLA, GOOGL, MSFT

### 2. Pipeline Flow (Horizontal Cards)
Visual representation of the 5-stage transformation process:

```
Raw Market Data → Data Cleaning → Feature Engineering → Discretization → Model Input
```

Each stage includes:
- Icon with gradient background
- Stage title
- Brief description
- Animated arrows between stages

### 3. Raw Data Preview
Table showing the latest 5 trading days:
- Columns: Date, Open, High, Low, Close, Volume
- Color-coded values (green/red for high/low)
- Formatted currency and volume display

### 4. Engineered Features Panel
Grid of 6 key technical indicators:

| Feature | Description | States |
|---------|-------------|--------|
| RSI | Relative Strength Index | OVERSOLD / NEUTRAL / OVERBOUGHT |
| Momentum | Price momentum indicator | WEAK / MODERATE / STRONG |
| Volatility (10d) | 10-day rolling volatility | LOW / MEDIUM / HIGH |
| MACD Diff | MACD histogram | BEARISH / NEUTRAL / BULLISH |
| SMA 10 | 10-day moving average | ABOVE / BELOW |
| ATR | Average True Range | LOW / MEDIUM / HIGH |

Each feature card shows:
- Icon and label
- Continuous value
- Discretized state (when toggled)
- Tooltip with explanation

### 5. Discretization Section
Side-by-side transformation visualization:

```
RSI: 28.45 → OVERSOLD
Volatility: 0.032 → HIGH
Momentum: 0.67 → STRONG
MACD Diff: 1.23 → BULLISH
```

Features:
- Animated arrows showing transformation
- Color-coded states (green/yellow/red)
- Toggle button to show/hide discretized values
- Explanation box: "Why Discretization?"

### 6. Model Connection
Visual flow diagram:

```
Discretized Features → Bayesian Network → Predictions
```

Includes:
- List of all 8 feature states used as inputs
- CTA buttons:
  - "View Model Structure" → `/pgm-graph`
  - "Learn More About Discretization" → `/discretization`

## Design Features

### Visual Style
- **Dark theme** with glassmorphism effects
- **Gradient accents**: cyan → teal → emerald → green → lime
- **Subtle animations**: fade-ins, hovers, scale effects
- **Consistent spacing**: 8px grid system

### Color Coding
- **Blue/Cyan**: Raw data stage
- **Teal**: Data cleaning
- **Emerald**: Feature engineering
- **Green**: Discretization
- **Lime**: Model input

### State Colors
- **Green**: Positive/Low risk (OVERSOLD, LOW volatility, STRONG momentum)
- **Yellow**: Neutral/Medium (NEUTRAL, MODERATE)
- **Red**: Negative/High risk (OVERBOUGHT, HIGH volatility, WEAK momentum)

## Technical Implementation

### Components
```
frontend/
├── app/
│   └── feature-intelligence/
│       └── page.tsx                    # Main page component
└── components/
    └── feature-intelligence/
        ├── pipeline-flow.tsx           # 5-stage pipeline
        ├── raw-data-preview.tsx        # Data table
        ├── feature-panel.tsx           # Feature cards
        ├── discretization-section.tsx  # Transformation view
        └── model-connection.tsx        # Model link
```

### State Management
- `selectedTicker`: Current stock symbol
- `stockData`: Array of StockFeatures
- `showDiscretized`: Toggle for discretized values
- `loading`: Loading state

### API Integration
- Uses existing `api.getFeatures(ticker)` endpoint
- No backend changes required
- Works with mock data in development

## Navigation

Access via:
1. **Main Menu**: Model Intelligence → Feature Pipeline
2. **Direct URL**: `/feature-intelligence`
3. **Related Pages**:
   - PGM Graph (`/pgm-graph`)
   - Discretization (`/discretization`)
   - Structure Analysis (`/structure-analysis`)

## Educational Value

This page helps users understand:
1. **Data Flow**: How raw prices become model inputs
2. **Feature Engineering**: What indicators are computed
3. **Discretization**: Why and how continuous values are binned
4. **Model Integration**: How features feed into the Bayesian Network

## Future Enhancements

Potential additions:
- [ ] Interactive feature selection
- [ ] Custom discretization thresholds
- [ ] Historical feature evolution charts
- [ ] Feature correlation heatmap
- [ ] Real-time feature updates
- [ ] Export feature data
- [ ] Compare multiple tickers side-by-side

## Accessibility

- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Tooltips for additional context
- High contrast color scheme
- Responsive design for all screen sizes
