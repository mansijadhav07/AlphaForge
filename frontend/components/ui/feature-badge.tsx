'use client'

import { useState } from 'react'
import { Info } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FeatureBadgeProps {
  name: string
  value: number | string
  description?: string
  format?: 'number' | 'percentage' | 'currency'
  colorize?: boolean
}

const featureDescriptions: Record<string, string> = {
  rsi: 'Relative Strength Index: Momentum oscillator measuring speed and magnitude of price changes. Values above 70 indicate overbought, below 30 indicate oversold.',
  macd: 'Moving Average Convergence Divergence: Trend-following momentum indicator showing relationship between two moving averages.',
  sma_10: '10-day Simple Moving Average: Average closing price over the last 10 days.',
  sma_30: '30-day Simple Moving Average: Average closing price over the last 30 days.',
  sma_50: '50-day Simple Moving Average: Average closing price over the last 50 days.',
  volatility_10: '10-day Volatility: Standard deviation of returns over 10 days, measuring price fluctuation.',
  momentum_score: 'Composite Momentum Score: Combined indicator from RSI, MACD, and price momentum.',
  atr: 'Average True Range: Measures market volatility by decomposing the entire range of price movement.',
  regime: 'Market Regime: Classification of current market state (Bull/Bear/Sideways).',
}

export function FeatureBadge({
  name,
  value,
  description,
  format = 'number',
  colorize = false,
}: FeatureBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false)

  const formatValue = (val: number | string): string => {
    if (typeof val === 'string') return val

    switch (format) {
      case 'percentage':
        return `${(val * 100).toFixed(2)}%`
      case 'currency':
        return `$${val.toFixed(2)}`
      default:
        return val.toFixed(2)
    }
  }

  const getValueColor = (val: number | string): string => {
    if (!colorize || typeof val === 'string') return 'text-foreground'
    
    if (name.toLowerCase().includes('rsi')) {
      if (val > 70) return 'text-bearish'
      if (val < 30) return 'text-bullish'
      return 'text-neutral'
    }
    
    if (name.toLowerCase().includes('regime')) {
      if (val > 0) return 'text-bullish'
      if (val < 0) return 'text-bearish'
      return 'text-neutral'
    }
    
    if (val > 0) return 'text-bullish'
    if (val < 0) return 'text-bearish'
    return 'text-muted-foreground'
  }

  const tooltipText = description || featureDescriptions[name.toLowerCase()] || 'No description available'

  return (
    <div className="relative group">
      <div className="flex items-center justify-between p-3 rounded-lg glass-hover">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground font-medium">
            {name.toUpperCase().replace(/_/g, ' ')}
          </span>
          <button
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            className="text-muted-foreground hover:text-neon-blue transition-colors"
          >
            <Info className="h-3 w-3" />
          </button>
        </div>
        <span className={cn('text-sm font-semibold', getValueColor(value))}>
          {formatValue(value)}
        </span>
      </div>

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute z-50 left-0 right-0 top-full mt-2 p-3 rounded-lg glass border border-white/20 text-xs text-muted-foreground animate-slide-in">
          {tooltipText}
        </div>
      )}
    </div>
  )
}
