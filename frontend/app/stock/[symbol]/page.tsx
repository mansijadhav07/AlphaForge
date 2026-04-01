'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams } from 'next/navigation'
import { ArrowLeft, TrendingUp, Activity, BarChart3, Target } from 'lucide-react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PriceChart } from '@/components/charts/price-chart'
import { IndicatorChart } from '@/components/charts/indicator-chart'
import { FeatureImpactChart } from '@/components/charts/feature-impact-chart'
import { FeatureBadge } from '@/components/ui/feature-badge'
import { RegimeIndicator } from '@/components/ui/regime-indicator'
import { LiveIndicator } from '@/components/ui/live-indicator'
import { api, type StockFeatures } from '@/lib/api'
import { formatCurrency, formatPercentage, getChangeColor } from '@/lib/utils'

export default function StockDetailPage() {
  const params = useParams()
  const symbol = params.symbol as string

  const [data, setData] = useState<StockFeatures[]>([])
  const [featureImpact, setFeatureImpact] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [isLiveMode, setIsLiveMode] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  
  const [showIndicators, setShowIndicators] = useState({
    sma10: true,
    sma30: true,
    sma50: false,
    bb: false,
  })

  // Load historical data once on mount
  const loadHistoricalData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log(`[${symbol}] Loading historical data...`)
      const response = await api.getHistoricalData(symbol, 30)
      
      console.log(`[${symbol}] Loaded ${response.data_points} data points (cache hit: ${response.cache_hit})`)
      setData(response.data)
      setLastUpdated(new Date())
      
      // Fetch feature impact data
      try {
        const impact = await api.getPGMFeatureImpact(symbol)
        setFeatureImpact(impact)
      } catch (error) {
        console.error('Error fetching feature impact:', error)
      }
      
      setLoading(false)
    } catch (err) {
      console.error(`[${symbol}] Error loading historical data:`, err)
      setError('Failed to load data')
      setLoading(false)
    }
  }, [symbol])

  // Update only the latest datapoint
  const updateLiveData = useCallback(async () => {
    if (!isLiveMode || data.length === 0) return
    
    try {
      setIsUpdating(true)
      setError(null)
      
      console.log(`[${symbol}] Fetching live update...`)
      const liveData = await api.getLivePrice(symbol)
      
      // Create updated datapoint
      const updatedPoint: StockFeatures = {
        ticker: symbol,
        date: liveData.timestamp.split('T')[0],
        close: liveData.price,
        open: liveData.indicators.open,
        high: liveData.indicators.high,
        low: liveData.indicators.low,
        volume: liveData.indicators.volume,
        return: liveData.change_pct,
        rsi: liveData.indicators.rsi,
        macd: liveData.indicators.macd,
        macd_signal: liveData.indicators.macd_signal,
        macd_diff: liveData.indicators.macd_diff,
        sma_10: liveData.indicators.sma_10,
        sma_30: liveData.indicators.sma_30,
        sma_50: liveData.indicators.sma_50,
        volatility_10: liveData.indicators.volatility_10,
        volatility_30: liveData.indicators.volatility_30,
        momentum_score: liveData.indicators.momentum_score,
        regime: liveData.indicators.regime,
        bb_upper: liveData.indicators.bb_upper,
        bb_middle: liveData.indicators.bb_middle,
        bb_lower: liveData.indicators.bb_lower,
        atr: liveData.indicators.atr
      }
      
      // Update only the last datapoint (no full re-render)
      setData(prevData => {
        const newData = [...prevData]
        newData[newData.length - 1] = updatedPoint
        return newData
      })
      
      setLastUpdated(new Date())
      console.log(`[${symbol}] Live update complete - Price: ${liveData.price}`)
      
    } catch (err) {
      console.error(`[${symbol}] Error updating live data:`, err)
      setError('Update failed')
    } finally {
      setIsUpdating(false)
    }
  }, [symbol, isLiveMode, data.length])

  // Toggle live mode
  const toggleLiveMode = useCallback(() => {
    setIsLiveMode(prev => !prev)
    setError(null)
  }, [])

  // Initial load
  useEffect(() => {
    loadHistoricalData()
  }, [loadHistoricalData])

  // Setup live polling
  useEffect(() => {
    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    if (isLiveMode && data.length > 0) {
      console.log(`[${symbol}] Starting live mode (30-second polling)`)
      
      // Immediate update
      updateLiveData()
      
      // Poll every 30 seconds
      intervalRef.current = setInterval(updateLiveData, 30000)
    } else {
      console.log(`[${symbol}] Live mode disabled`)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isLiveMode, data.length, updateLiveData, symbol])

  if (loading || data.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-white/10 rounded w-1/4" />
          <div className="h-96 bg-white/10 rounded" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="h-64 bg-white/10 rounded" />
            <div className="h-64 bg-white/10 rounded" />
            <div className="h-64 bg-white/10 rounded" />
          </div>
        </div>
      </div>
    )
  }

  const latestData = data[data.length - 1]
  const previousData = data[data.length - 2]
  const priceChange = latestData.close - previousData.close
  const priceChangePct = priceChange / previousData.close

  // Key features to display
  const keyFeatures = [
    { name: 'RSI', value: latestData.rsi, colorize: true },
    { name: 'MACD', value: latestData.macd, colorize: true },
    { name: 'SMA_10', value: latestData.sma_10, format: 'currency' as const },
    { name: 'SMA_30', value: latestData.sma_30, format: 'currency' as const },
    { name: 'SMA_50', value: latestData.sma_50, format: 'currency' as const },
    { name: 'Volatility_10', value: latestData.volatility_10, format: 'percentage' as const },
    { name: 'Volatility_30', value: latestData.volatility_30, format: 'percentage' as const },
    { name: 'ATR', value: latestData.atr },
    { name: 'Momentum_Score', value: latestData.momentum_score, colorize: true },
    { name: 'BB_Upper', value: latestData.bb_upper, format: 'currency' as const },
    { name: 'BB_Lower', value: latestData.bb_lower, format: 'currency' as const },
    { name: 'Return', value: latestData.return, format: 'percentage' as const, colorize: true },
  ]

  return (
    <div className="container mx-auto px-4 py-8 space-y-6 animate-slide-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            href="/dashboard"
            className="p-2 rounded-lg glass-hover transition-all"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-4xl font-bold gradient-text">{symbol}</h1>
            <p className="text-muted-foreground">Real-time feature analysis</p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-3xl font-bold">{formatCurrency(latestData.close)}</div>
          <div className={`text-sm font-medium ${getChangeColor(priceChange)}`}>
            {priceChange > 0 ? '+' : ''}{formatCurrency(priceChange)} ({priceChange > 0 ? '+' : ''}{formatPercentage(priceChangePct)})
          </div>
        </div>
      </div>

      {/* Live Mode Indicator */}
      <Card>
        <CardContent className="py-4">
          <LiveIndicator
            isLive={isLiveMode}
            lastUpdated={lastUpdated}
            onToggle={toggleLiveMode}
            isLoading={isUpdating}
            error={error}
          />
        </CardContent>
      </Card>

      {/* Price Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Price Chart</CardTitle>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowIndicators({ ...showIndicators, sma10: !showIndicators.sma10 })}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  showIndicators.sma10 ? 'bg-bullish/20 text-bullish' : 'bg-white/5 text-muted-foreground'
                }`}
              >
                SMA 10
              </button>
              <button
                onClick={() => setShowIndicators({ ...showIndicators, sma30: !showIndicators.sma30 })}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  showIndicators.sma30 ? 'bg-neutral/20 text-neutral' : 'bg-white/5 text-muted-foreground'
                }`}
              >
                SMA 30
              </button>
              <button
                onClick={() => setShowIndicators({ ...showIndicators, sma50: !showIndicators.sma50 })}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  showIndicators.sma50 ? 'bg-bearish/20 text-bearish' : 'bg-white/5 text-muted-foreground'
                }`}
              >
                SMA 50
              </button>
              <button
                onClick={() => setShowIndicators({ ...showIndicators, bb: !showIndicators.bb })}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  showIndicators.bb ? 'bg-neutral/20 text-neutral' : 'bg-white/5 text-muted-foreground'
                }`}
              >
                Bollinger Bands
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <PriceChart data={data} showIndicators={showIndicators} highlightLast={isLiveMode} />
        </CardContent>
      </Card>

      {/* Technical Indicators */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* RSI */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-neon-blue" />
              <span>RSI (Relative Strength Index)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <IndicatorChart data={data} type="rsi" />
            <div className="mt-4 flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Current RSI:</span>
              <span className={`font-semibold ${
                latestData.rsi > 70 ? 'text-bearish' : latestData.rsi < 30 ? 'text-bullish' : 'text-neutral'
              }`}>
                {latestData.rsi.toFixed(2)}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* MACD */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-neon-teal" />
              <span>MACD</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <IndicatorChart data={data} type="macd" />
            <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground block">MACD</span>
                <span className="font-semibold">{latestData.macd.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-muted-foreground block">Signal</span>
                <span className="font-semibold">{latestData.macd_signal.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-muted-foreground block">Histogram</span>
                <span className={`font-semibold ${getChangeColor(latestData.macd_diff)}`}>
                  {latestData.macd_diff.toFixed(2)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Volume */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-neon-blue" />
            <span>Volume</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <IndicatorChart data={data} type="volume" />
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Regime Indicator */}
        <RegimeIndicator regime={latestData.regime} />

        {/* Key Features */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>All Features</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {keyFeatures.map((feature) => (
                <FeatureBadge
                  key={feature.name}
                  name={feature.name}
                  value={feature.value}
                  format={feature.format}
                  colorize={feature.colorize}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Feature Contribution Analysis */}
      {featureImpact && featureImpact.impacts && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-neon-blue" />
              <span>Feature Contribution Analysis</span>
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              How each feature influences the probabilistic prediction
            </p>
          </CardHeader>
          <CardContent style={{ height: '400px' }}>
            <FeatureImpactChart data={featureImpact.impacts} title="" />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
