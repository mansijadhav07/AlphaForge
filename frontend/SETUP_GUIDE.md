# AlphaForge Frontend - Setup Guide

## 🎯 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Configure Environment
```bash
# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 3: Run Development Server
```bash
npm run dev
```

### Step 4: Open Browser
Navigate to: http://localhost:3000

## ✅ What's Included - Phase 1 Complete!

### Pages Created
✓ Dashboard (`/dashboard`) - Market overview with real-time data  
✓ Root redirect (`/`) - Automatically redirects to dashboard

### Components Built
✓ Navbar - Professional navigation with logo and links  
✓ Card - Glassmorphism card component  
✓ Badge - Signal and status badges  
✓ Layout - Root layout with dark theme

### Features Implemented
✓ Dark theme with glassmorphism  
✓ Neon blue/teal accent colors  
✓ Auto-refresh every 10 seconds  
✓ Responsive design  
✓ Smooth animations  
✓ Real-time market data  
✓ Trading signals display  
✓ Top stocks monitoring

### API Integration
✓ API service layer (`lib/api.ts`)  
✓ Mock data for development  
✓ Automatic fallback when backend unavailable  
✓ TypeScript types for all data

## 📊 Dashboard Features

### Market Overview Cards
- Market Regime (Bull/Bear/Sideways)
- Volatility Index
- Active Signals Count
- Tracked Stocks Count

### Top Stocks Section
- Real-time prices
- Price changes ($ and %)
- Color-coded gains/losses
- Click to view stock details

### Top Signals Section
- BUY/SELL/HOLD badges
- Confidence scores
- Signal reasoning
- Quick navigation to stocks

## 🎨 Design System

### Colors
- Background: Dark (#0a0a0a)
- Accent: Neon Blue (#06b6d4) / Teal (#14b8a6)
- Bullish: Green (#10b981)
- Bearish: Red (#ef4444)
- Neutral: Yellow (#f59e0b)

### Effects
- Glassmorphism cards
- Glow effects on hover
- Smooth transitions
- Pulse animations for live indicators

## 🚀 Running the App

### Development
```bash
cd frontend
npm run dev
```
Opens at: http://localhost:3000

### Production Build
```bash
npm run build
npm start
```

## 📝 Next Steps

### Phase 2: Stock Detail Page (Coming Next)
- Interactive price chart with Recharts
- Technical indicators overlay (RSI, MACD, MA)
- Feature panel showing all computed features
- Regime indicator with visual feedback

### Phase 3: Backtesting UI
- Strategy selection dropdown
- Performance metrics display
- Equity curve chart
- Strategy comparison table

### Phase 4: Insights Page
- AI-like market insights
- Alert cards with icons
- Market warnings
- Opportunity highlights

## 🎯 Current Status

**Phase 1: Dashboard** ✅ COMPLETE

**Files Created:**
- 15+ TypeScript/React files
- Complete dashboard with real-time data
- Professional UI components
- API integration layer
- Full styling system

**Ready to Use:**
- Install dependencies: `npm install`
- Run dev server: `npm run dev`
- View at: http://localhost:3000

---

**Status**: Phase 1 Complete ✅  
**Next**: Build Stock Detail Page with Charts
