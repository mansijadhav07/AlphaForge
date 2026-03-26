'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, TrendingUp, TrendingDown, AlertTriangle, Sparkles } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { StatCard } from '@/components/ui/stat-card'
import { SkeletonStats, SkeletonCard } from '@/components/ui/skeleton-loader'
import { api, type MarketOverview } from '@/lib/api'
import { formatCurrency, formatPercentage, getChangeColor, getSignalColor } from '@/lib/utils'
import { config } from '@/lib/config'
import Link from 'next/link'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

export default function DashboardPage() {
  const [marketData, setMarketData] = useState<MarketOverview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      // Only show loading on initial load, not on refresh
      if (!marketData) {
        setLoading(true)
      }
      const data = await api.getMarketOverview()
      setMarketData(data)
      setLoading(false)
    }

    fetchData()
    
    // Auto-refresh based on config
    if (config.features.autoRefresh) {
      const interval = setInterval(fetchData, config.refresh.dashboard)
      return () => clearInterval(interval)
    }
  }, [])

  if (loading || !marketData) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div className="h-10 w-64 skeleton mb-3" />
          <div className="h-5 w-96 skeleton" />
        </div>
        <div className="card-grid-4 mb-8">
          <SkeletonStats />
        </div>
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  const regimeTrend = marketData.market_regime === 'Bull' ? 'up' : marketData.market_regime === 'Bear' ? 'down' : 'neutral'
  const volatilityTrend = marketData.volatility_index > 20 ? 'up' : 'neutral'

  return (
    <div className="page-container">
      {/* Header */}
      <motion.div 
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-3">
          <h1 className="page-title">Market Dashboard</h1>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <Sparkles className="w-7 h-7 text-cyan-400" />
          </motion.div>
        </div>
        <p className="page-description">
          Real-time market intelligence powered by probabilistic graphical models
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="card-grid-4 mb-8">
        <StatCard
          title="Market Regime"
          value={marketData.market_regime}
          icon={Activity}
          trend={regimeTrend}
          delay={0}
        />
        <StatCard
          title="Volatility Index"
          value={marketData.volatility_index.toFixed(2)}
          change={marketData.volatility_index > 20 ? 15.3 : -5.2}
          icon={AlertTriangle}
          trend={volatilityTrend}
          delay={0.1}
        />
        <StatCard
          title="Active Signals"
          value={marketData.signals.length}
          icon={TrendingUp}
          trend="up"
          delay={0.2}
        />
        <StatCard
          title="Tracked Stocks"
          value={marketData.top_stocks.length}
          icon={Activity}
          trend="neutral"
          delay={0.3}
        />
      </div>

      {/* Top Stocks */}
      <motion.div
        className="section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <div className="glass-card glass-hover">
          <div className="card-header">
            <h2 className="card-title flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-cyan-400" />
              Top Performing Stocks
            </h2>
            <p className="card-subtitle">Live market data with real-time updates</p>
          </div>
          <div className="card-body">
            <motion.div 
              className="space-y-3"
              variants={container}
              initial="hidden"
              animate="show"
            >
              {marketData.top_stocks.map((stock, index) => (
                <motion.div key={stock.ticker} variants={item}>
                  <Link href={`/stock/${stock.ticker}`} className="block">
                    <motion.div
                      className="flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-cyan-500/30 transition-all duration-200 group"
                      whileHover={{ scale: 1.01, x: 4 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500/20 to-teal-500/20 flex items-center justify-center font-bold text-base border border-cyan-500/20">
                          {stock.ticker.slice(0, 2)}
                        </div>
                        <div>
                          <div className="font-semibold text-base text-white">{stock.ticker}</div>
                          <div className="text-sm text-gray-400">
                            {formatCurrency(stock.price)}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`font-semibold text-base ${getChangeColor(stock.change)}`}>
                          {stock.change > 0 ? '+' : ''}{formatCurrency(stock.change)}
                        </div>
                        <div className={`text-sm ${getChangeColor(stock.change)}`}>
                          {stock.change > 0 ? '+' : ''}{formatPercentage(stock.change_pct)}
                        </div>
                      </div>
                    </motion.div>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Trading Signals */}
      <motion.div
        className="section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <div className="glass-card glass-hover">
          <div className="card-header">
            <h2 className="card-title flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-teal-400" />
              AI-Powered Trading Signals
            </h2>
            <p className="card-subtitle">Probabilistic predictions with confidence scores</p>
          </div>
          <div className="card-body">
            <motion.div 
              className="space-y-3"
              variants={container}
              initial="hidden"
              animate="show"
            >
              {marketData.signals.map((signal, index) => (
                <motion.div
                  key={index}
                  variants={item}
                  className="flex items-start justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-teal-500/30 transition-all duration-200"
                  whileHover={{ x: 4 }}
                >
                  <div className="flex items-start space-x-4 flex-1">
                    <Badge className={`${getSignalColor(signal.signal)} px-3 py-1 text-xs font-semibold`}>
                      {signal.signal}
                    </Badge>
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="font-semibold text-base text-white">{signal.ticker}</span>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse" />
                          <span className="text-xs text-gray-400 font-medium">
                            {(signal.confidence * 100).toFixed(0)}% confidence
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-400 leading-relaxed">
                        {signal.reason}
                      </p>
                    </div>
                  </div>
                  <Link
                    href={`/stock/${signal.ticker}`}
                    className="text-sm font-semibold text-cyan-400 hover:text-teal-400 transition-colors flex items-center gap-1"
                  >
                    View
                    <span>→</span>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
