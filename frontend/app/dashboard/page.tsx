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
      <div className="container mx-auto px-4 py-8 space-y-8">
        <div className="space-y-2">
          <div className="h-10 w-64 skeleton" />
          <div className="h-5 w-96 skeleton" />
        </div>
        <SkeletonStats />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  const regimeTrend = marketData.market_regime === 'Bull' ? 'up' : marketData.market_regime === 'Bear' ? 'down' : 'neutral'
  const volatilityTrend = marketData.volatility_index > 20 ? 'up' : 'neutral'

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header with Premium Animation */}
      <motion.div 
        className="space-y-2"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
      >
        <div className="flex items-center gap-3">
          <h1 className="text-5xl font-bold gradient-text">Market Dashboard</h1>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <Sparkles className="w-8 h-8 text-neon-blue" />
          </motion.div>
        </div>
        <p className="text-muted-premium text-lg">
          Real-time market intelligence powered by probabilistic graphical models
        </p>
      </motion.div>

      {/* Premium Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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

      {/* Top Stocks - Premium Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Card className="glass-card border-0 overflow-hidden">
          <div className="absolute inset-0 bg-mesh opacity-30" />
          <CardHeader className="relative">
            <CardTitle className="text-2xl font-bold flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-neon-blue" />
              Top Performing Stocks
            </CardTitle>
          </CardHeader>
          <CardContent className="relative">
            <motion.div 
              className="space-y-3"
              variants={container}
              initial="hidden"
              animate="show"
            >
              {marketData.top_stocks.map((stock, index) => (
                <motion.div key={stock.ticker} variants={item}>
                  <Link
                    href={`/stock/${stock.ticker}`}
                    className="block"
                  >
                    <motion.div
                      className="flex items-center justify-between p-5 rounded-xl glass-hover group relative overflow-hidden"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {/* Animated background gradient */}
                      <div className="absolute inset-0 bg-gradient-to-r from-neon-blue/0 via-neon-blue/5 to-neon-blue/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                      
                      <div className="flex items-center space-x-4 relative z-10">
                        <motion.div 
                          className="w-14 h-14 rounded-xl bg-gradient-to-br from-neon-blue/20 to-neon-teal/20 flex items-center justify-center font-bold text-lg group-hover:from-neon-blue/40 group-hover:to-neon-teal/40 transition-all duration-300"
                          whileHover={{ rotate: 5 }}
                        >
                          {stock.ticker.slice(0, 2)}
                        </motion.div>
                        <div>
                          <div className="font-bold text-lg">{stock.ticker}</div>
                          <div className="text-sm text-muted-foreground">
                            {formatCurrency(stock.price)}
                          </div>
                        </div>
                      </div>
                      <div className="text-right relative z-10">
                        <motion.div 
                          className={`font-bold text-lg ${getChangeColor(stock.change)}`}
                          initial={{ opacity: 0, x: 10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          {stock.change > 0 ? '+' : ''}{formatCurrency(stock.change)}
                        </motion.div>
                        <div className={`text-sm font-semibold ${getChangeColor(stock.change)}`}>
                          {stock.change > 0 ? '+' : ''}{formatPercentage(stock.change_pct)}
                        </div>
                      </div>
                    </motion.div>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Trading Signals - Premium Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <Card className="glass-card border-0 overflow-hidden">
          <div className="absolute inset-0 bg-mesh opacity-30" />
          <CardHeader className="relative">
            <CardTitle className="text-2xl font-bold flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-neon-teal" />
              AI-Powered Trading Signals
            </CardTitle>
          </CardHeader>
          <CardContent className="relative">
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
                  className="flex items-start justify-between p-5 rounded-xl glass-hover group relative overflow-hidden"
                  whileHover={{ x: 4 }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-neon-teal/0 via-neon-teal/5 to-neon-teal/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  
                  <div className="flex items-start space-x-4 flex-1 relative z-10">
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      transition={{ type: "spring", stiffness: 400 }}
                    >
                      <Badge className={`${getSignalColor(signal.signal)} px-3 py-1 text-sm font-semibold`}>
                        {signal.signal}
                      </Badge>
                    </motion.div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="font-bold text-lg">{signal.ticker}</span>
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-2 rounded-full bg-neon-blue animate-pulse" />
                          <span className="text-sm text-muted-foreground font-medium">
                            {(signal.confidence * 100).toFixed(0)}% confidence
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-muted-premium leading-relaxed">
                        {signal.reason}
                      </p>
                    </div>
                  </div>
                  <Link
                    href={`/stock/${signal.ticker}`}
                    className="text-sm font-semibold text-neon-blue hover:text-neon-teal transition-colors relative z-10 flex items-center gap-1 group-hover:gap-2 transition-all"
                  >
                    Analyze
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
