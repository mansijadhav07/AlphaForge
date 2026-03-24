# AlphaForge Frontend

Modern, production-grade Next.js frontend for the AlphaForge Financial Intelligence Platform.

## 🚀 Tech Stack

- **Next.js 14** (App Router)
- **React 18**
- **TypeScript**
- **Tailwind CSS**
- **Recharts** (Charts)
- **Zustand** (State Management)
- **Framer Motion** (Animations)

## 🎨 Design Features

- Dark theme with glassmorphism effects
- Neon blue/teal accent colors
- Smooth animations and transitions
- Responsive design (mobile + desktop)
- Real-time data updates
- Professional fintech UI

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
```

## 🌐 Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── dashboard/          # Dashboard page
│   ├── stock/[symbol]/     # Stock detail pages
│   ├── backtesting/        # Backtesting UI
│   ├── insights/           # Insights page
│   ├── layout.tsx          # Root layout
│   └── globals.css         # Global styles
├── components/
│   ├── ui/                 # UI components (Card, Badge, etc.)
│   ├── layout/             # Layout components (Navbar)
│   └── charts/             # Chart components
├── lib/
│   ├── api.ts              # API service layer
│   └── utils.ts            # Utility functions
└── public/                 # Static assets
```

## 🎯 Pages

### Dashboard (`/dashboard`)
- Market overview cards
- Top stocks with real-time prices
- Trading signals
- Auto-refresh every 10 seconds

### Stock Detail (`/stock/[symbol]`)
- Interactive price chart
- Technical indicators overlay
- Feature panel with all computed features
- Regime indicator

### Backtesting (`/backtesting`)
- Strategy selection
- Performance metrics
- Equity curve chart
- Strategy comparison

### Insights (`/insights`)
- AI-like market insights
- Alerts and warnings
- Highlighted cards with icons

## 🔗 API Integration

The frontend connects to the Python backend via REST API:

- `GET /api/features/{symbol}` - Stock features
- `GET /api/market-overview` - Market overview
- `GET /api/backtest/{strategy}` - Backtest results
- `GET /api/insights` - Market insights

## 🎨 Color Palette

- **Background**: Dark (black/gray)
- **Accent**: Neon blue (#06b6d4) / Teal (#14b8a6)
- **Bullish**: Green (#10b981)
- **Bearish**: Red (#ef4444)
- **Neutral**: Yellow (#f59e0b)

## 🚀 Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

## 📝 Notes

- Mock data is used when backend is unavailable
- Auto-refresh is enabled for real-time feel
- All components are TypeScript-typed
- Responsive design works on all screen sizes

## 🎯 Next Steps

1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Open browser: `http://localhost:3000`
4. Connect to backend API (optional)

## 🔧 Customization

- Edit `tailwind.config.ts` for theme changes
- Modify `lib/api.ts` for API endpoints
- Update `app/globals.css` for global styles
- Add new pages in `app/` directory

## 📚 Documentation

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Recharts](https://recharts.org/)
- [TypeScript](https://www.typescriptlang.org/docs)
