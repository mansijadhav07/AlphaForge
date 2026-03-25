# AlphaForge Frontend ✨

<div align="center">

![Next.js](https://img.shields.io/badge/Next.js-14.2-000000?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white)

**Premium fintech UI with glassmorphism effects and smooth animations**

</div>

---

## 🎨 Overview

A modern, production-grade Next.js 14 frontend featuring:
- ✨ **Premium glassmorphism design** with backdrop blur
- 🎭 **Framer Motion animations** for smooth interactions
- 📊 **Interactive visualizations** (Recharts, React Flow)
- 🎯 **Real-time updates** with auto-refresh
- 📱 **Fully responsive** design
- 🌙 **Dark theme** optimized for long sessions

## 🚀 Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | Next.js 14 (App Router) |
| **UI Library** | React 18.3 |
| **Language** | TypeScript 5.4 |
| **Styling** | Tailwind CSS 3.4 |
| **Animations** | Framer Motion 11.0 |
| **Charts** | Recharts 2.12 |
| **Graphs** | React Flow 11.11 |
| **State** | Zustand 4.5 |
| **Icons** | Lucide React |
| **Date** | date-fns 3.3 |

## ✨ Premium Features

### Glassmorphism Design
- Backdrop blur effects (xl)
- Multi-layered shadows
- Gradient borders
- Semi-transparent cards
- Smooth hover transitions

### Animations
- Page entrance animations
- Staggered list reveals
- Hover lift effects
- Loading skeletons
- Micro-interactions
- 60fps smooth performance

### Interactive Components
- **PGM Graph**: Interactive Bayesian Network with React Flow
- **Feature Impact**: Animated bar charts
- **Confusion Matrix**: Interactive heatmap
- **Calibration Curves**: Line charts with tooltips
- **Equity Curves**: Time-series charts
- **Price Charts**: Candlestick with indicators

## 📦 Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 🌐 Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── dashboard/                # Market dashboard
│   ├── stock/[symbol]/           # Stock detail pages
│   ├── backtesting/              # Strategy backtesting
│   ├── insights/                 # AI insights
│   ├── pgm-graph/                # 🆕 PGM visualization
│   ├── feature-impact/           # 🆕 Feature contribution
│   ├── model-evaluation/         # 🆕 Model metrics
│   ├── model-failures/           # 🆕 Failure analysis
│   ├── layout.tsx                # Root layout with navbar
│   ├── page.tsx                  # Premium splash screen
│   └── globals.css               # Global styles + utilities
│
├── components/
│   ├── ui/                       # Base UI components
│   │   ├── card.tsx              # Premium glass cards
│   │   ├── badge.tsx             # Gradient badges
│   │   ├── animated-card.tsx     # 🆕 Animated wrapper
│   │   ├── stat-card.tsx         # 🆕 Premium stat cards
│   │   ├── skeleton-loader.tsx   # 🆕 Loading skeletons
│   │   ├── insight-card.tsx      # Insight cards
│   │   ├── regime-indicator.tsx  # Market regime badge
│   │   └── feature-badge.tsx     # Feature badges
│   │
│   ├── charts/                   # Chart components
│   │   ├── price-chart.tsx       # Candlestick charts
│   │   ├── indicator-chart.tsx   # Technical indicators
│   │   ├── equity-curve-chart.tsx # Backtest equity
│   │   ├── feature-impact-chart.tsx # 🆕 Feature bars
│   │   ├── confusion-matrix.tsx  # 🆕 Heatmap
│   │   └── calibration-curve.tsx # 🆕 Calibration
│   │
│   ├── pgm/                      # 🆕 PGM components
│   │   └── network-graph.tsx     # Interactive graph
│   │
│   └── layout/                   # Layout components
│       └── navbar.tsx            # Animated navigation
│
├── lib/
│   ├── api.ts                    # API service layer
│   └── utils.ts                  # Utility functions
│
├── public/                       # Static assets
├── tailwind.config.ts            # Tailwind configuration
├── tsconfig.json                 # TypeScript config
└── package.json                  # Dependencies
```

## 🎯 Pages & Routes

### 🏠 Home (`/`)
Premium animated splash screen with:
- Rotating logo animation
- Pulsing background orbs
- Feature icons with stagger
- Auto-redirect to dashboard (2s)

### 📊 Dashboard (`/dashboard`)
Market overview with:
- 4 animated stat cards
- Top stocks with gradient hover
- AI-powered signals
- Real-time updates (10s refresh)
- Mesh background effects

### 📈 Stock Detail (`/stock/[symbol]`)
Individual stock analysis:
- Interactive price chart
- Technical indicators overlay
- Feature panel (50+ features)
- Regime indicator
- Real-time updates

### 🧪 Backtesting (`/backtesting`)
Strategy evaluation:
- Strategy selector
- Performance metrics grid
- Equity curve chart
- Trade analysis table

### 💡 Insights (`/insights`)
AI-powered insights:
- Categorized insights (warnings, opportunities)
- Stat cards with trends
- Filterable insight cards
- Icon-based categorization

### 🕸️ PGM Graph (`/pgm-graph`)
Interactive Bayesian Network:
- 11-node graph visualization
- Hierarchical layout
- Click nodes for details
- Color-coded by type
- Zoom and pan controls

### 🎯 Feature Impact (`/feature-impact`)
Feature contribution analysis:
- Horizontal bar charts
- Color-coded by impact level
- Statistics dashboard
- Sensitivity analysis results

### 📊 Model Evaluation (`/model-evaluation`)
Model performance metrics:
- Accuracy, Brier score
- Confusion matrix heatmap
- Calibration curves
- Classification report

### ⚠️ Model Failures (`/model-failures`)
Failure case analysis:
- Summary statistics
- Detailed failure table
- Severity indicators
- Actionable insights

## 🔗 API Integration

### Endpoints Used

```typescript
// Market data
GET /api/market-overview
GET /api/features/{symbol}

// PGM endpoints
GET /api/pgm/graph
GET /api/pgm/probabilities/{symbol}
GET /api/pgm/explanation/{symbol}
GET /api/pgm/feature-impact/{symbol}
GET /api/pgm/evaluation/{symbol}
GET /api/pgm/failures/{symbol}

// Backtesting
GET /api/backtest/{strategy}?ticker={symbol}

// Insights
GET /api/insights
```

### API Service (`lib/api.ts`)

```typescript
import { api } from '@/lib/api'

// Usage examples
const overview = await api.getMarketOverview()
const features = await api.getFeatures('AAPL')
const graph = await api.getPGMGraph()
const impact = await api.getPGMFeatureImpact('AAPL')
```

### Mock Data Fallback
All API calls have mock data fallback for development without backend.

## 🎨 Design System

### Color Palette

```css
/* Primary Colors */
--neon-blue: #06b6d4      /* Primary accent */
--neon-teal: #14b8a6      /* Secondary accent */
--neon-purple: #a855f7    /* Tertiary accent */

/* Semantic Colors */
--bullish: #10b981        /* Positive/Up */
--bearish: #ef4444        /* Negative/Down */
--neutral: #f59e0b        /* Neutral/Sideways */

/* Background */
--background: hsl(0 0% 3.9%)
--foreground: hsl(0 0% 98%)
```

### Typography

```css
/* Headers */
font-weight: 700 (bold)
letter-spacing: -0.025em (tight)

/* Body */
font-weight: 500 (medium)
line-height: 1.5

/* Muted */
opacity: 0.7
font-size: 0.875rem
```

### Spacing

```css
/* Card padding */
padding: 1.5rem (24px)

/* Grid gaps */
gap: 1.5rem (24px)

/* Section spacing */
margin-bottom: 2rem (32px)
```

## 🎭 Animation Patterns

### Entrance Animation
```typescript
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5, delay: 0.1 }}
>
```

### Hover Effect
```typescript
<motion.div
  whileHover={{ y: -4, scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
>
```

### Stagger Children
```typescript
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}
```

## 🚀 Development

### Start Development Server
```bash
npm run dev
```
Open http://localhost:3000

### Build for Production
```bash
npm run build
npm start
```

### Type Checking
```bash
npx tsc --noEmit
```

### Linting
```bash
npm run lint
```

## 📊 Performance

### Build Output
```
Route                    Size      First Load JS
/                        2.24 kB   125 kB
/dashboard               3.99 kB   147 kB
/pgm-graph              49.6 kB    141 kB
/stock/[symbol]         10.1 kB    228 kB
```

### Optimization
- Code splitting by route
- Image optimization
- CSS purging
- Tree shaking
- Lazy loading

## 🎯 Key Components

### AnimatedCard
```typescript
<AnimatedCard delay={0.1} hover glow>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</AnimatedCard>
```

### StatCard
```typescript
<StatCard
  title="Market Regime"
  value="Bull"
  change={15.3}
  icon={Activity}
  trend="up"
  delay={0}
/>
```

### Skeleton Loaders
```typescript
{loading ? <SkeletonStats /> : <ActualContent />}
```

## 📚 Documentation

- **[PREMIUM_UI_COMPLETE.md](PREMIUM_UI_COMPLETE.md)** - UI enhancement details
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Setup instructions
- **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)** - Project completion report

## 🔧 Customization

### Change Theme Colors
Edit `tailwind.config.ts`:
```typescript
colors: {
  'neon-blue': '#06b6d4',  // Change this
  'neon-teal': '#14b8a6',  // And this
}
```

### Add New Page
```bash
# Create new route
mkdir app/my-page
touch app/my-page/page.tsx
```

### Modify API Endpoint
Edit `lib/api.ts`:
```typescript
async getMyData() {
  return await this.fetchWithTimeout(
    `${API_BASE_URL}/api/my-endpoint`
  )
}
```

## 🐛 Troubleshooting

### Port 3000 in use
```bash
PORT=3001 npm run dev
```

### Build errors
```bash
rm -rf .next
npm run build
```

### Type errors
```bash
npm install --save-dev @types/node @types/react
```

## 📝 Best Practices

1. **Use TypeScript** - All components are typed
2. **Responsive Design** - Test on mobile/tablet/desktop
3. **Accessibility** - Use semantic HTML and ARIA labels
4. **Performance** - Lazy load heavy components
5. **Error Handling** - Always have fallback UI

## 🎉 Features Showcase

✨ Glassmorphism cards with backdrop blur  
🎭 Smooth Framer Motion animations  
💎 Gradient text and glowing effects  
⚡ Loading skeletons for better UX  
🌊 Hover effects with scale and lift  
🎯 Animated navigation with active indicators  
💫 Pulsing status indicators  
🎪 Staggered list animations  

---

<div align="center">

**Built with ❤️ using Next.js 14 and Framer Motion**

</div>
