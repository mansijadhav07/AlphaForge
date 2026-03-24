'use client'

import { useEffect, useState } from 'react'
import { Activity, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { api, type MarketOverview } from '@/lib/api'
import { formatCurrency, formatPercentage, getChangeColor, getSignalColor } from '@/lib/utils'
import Link from 'next/link'

export default function DashboardPage() {
  const [marketData, setMarketData] = useState<MarketOverview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      const data = await api.getMarketOverview()
      setMarketData(data)
      setLoading(false)
    }

    fetchData()
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading || !marketData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-white/10 rounded w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-white/10 rounded w-3/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8 animate-slide-in">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold gradient-text">Market Dashboard</h1>
        <p className="text-muted-foreground">
          Real-time market intelligence and feature analysis
        </p>
      </div>

      {/* Market Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Market Regime */}
        <Card className="card-glow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Market Regime
            </CardTitle>
            <Activity className="h-4 w-4 text-neon-blue" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {marketData.market_regime}
            </div>
            <Badge 
              variant={marketData.market_regime === 'Bull' ? 'bullish' : marketData.market_regime === 'Bear' ? 'bearish' : 'neutral'}
              className="mt-2"
            >
              {marketData.market_regime === 'Bull' ? 'Bullish Trend' : marketData.market_regime === 'Bear' ? 'Bearish Trend' : 'Sideways'}
            </Badge>
          </CardContent>
        </Card>

        {/* Volatility Index */}
        <Card className="card-glow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Volatility Index
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-neutral" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {marketData.volatility_index.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {marketData.volatility_index > 20 ? 'High volatility' : 'Normal volatility'}
            </p>
          </CardContent>
        </Card>

        {/* Active Signals */}
        <Card className="card-glow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Signals
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-bullish" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {marketData.signals.length}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Trading opportunities
            </p>
          </CardContent>
        </Card>

        {/* Tracked Stocks */}
        <Card className="card-glow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tracked Stocks
            </CardTitle>
            <Activity className="h-4 w-4 text-neon-teal" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {marketData.top_stocks.length}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Real-time monitoring
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Top Stocks */}
      <Card>
        <CardHeader>
          <CardTitle>Top Stocks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {marketData.top_stocks.map((stock) => (
              <Link
                key={stock.ticker}
                href={`/stock/${stock.ticker}`}
                className="flex items-center justify-between p-4 rounded-lg glass-hover cursor-pointer group"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-neon-blue/20 to-neon-teal/20 flex items-center justify-center group-hover:from-neon-blue/30 group-hover:to-neon-teal/30 transition-all">
                    <span className="text-lg font-bold">{stock.ticker.slice(0, 2)}</span>
                  </div>
                  <div>
                    <div className="font-semibold">{stock.ticker}</div>
                    <div className="text-sm text-muted-foreground">
                      {formatCurrency(stock.price)}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-semibold ${getChangeColor(stock.change)}`}>
                    {stock.change > 0 ? '+' : ''}{formatCurrency(stock.change)}
                  </div>
                  <div className={`text-sm ${getChangeColor(stock.change)}`}>
                    {stock.change > 0 ? '+' : ''}{formatPercentage(stock.change_pct)}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Top Signals */}
      <Card>
        <CardHeader>
          <CardTitle>Top Signals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {marketData.signals.map((signal, index) => (
              <div
                key={index}
                className="flex items-start justify-between p-4 rounded-lg glass-hover"
              >
                <div className="flex items-start space-x-4 flex-1">
                  <Badge className={getSignalColor(signal.signal)}>
                    {signal.signal}
                  </Badge>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">{signal.ticker}</span>
                      <span className="text-sm text-muted-foreground">
                        Confidence: {(signal.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {signal.reason}
                    </p>
                  </div>
                </div>
                <Link
                  href={`/stock/${signal.ticker}`}
                  className="text-sm text-neon-blue hover:text-neon-teal transition-colors"
                >
                  View →
                </Link>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
