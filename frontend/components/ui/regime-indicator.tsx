'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from './badge'

interface RegimeIndicatorProps {
  regime: number
  className?: string
}

export function RegimeIndicator({ regime, className }: RegimeIndicatorProps) {
  const getRegimeData = () => {
    if (regime > 0) {
      return {
        label: 'Bull Market',
        icon: TrendingUp,
        color: 'text-bullish',
        bgColor: 'bg-bullish/10',
        borderColor: 'border-bullish/20',
        variant: 'bullish' as const,
      }
    }
    if (regime < 0) {
      return {
        label: 'Bear Market',
        icon: TrendingDown,
        color: 'text-bearish',
        bgColor: 'bg-bearish/10',
        borderColor: 'border-bearish/20',
        variant: 'bearish' as const,
      }
    }
    return {
      label: 'Sideways Market',
      icon: Minus,
      color: 'text-neutral',
      bgColor: 'bg-neutral/10',
      borderColor: 'border-neutral/20',
      variant: 'neutral' as const,
    }
  }

  const regimeData = getRegimeData()
  const Icon = regimeData.icon

  return (
    <div className={cn('glass rounded-lg p-6', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">Market Regime</h3>
        <Badge variant={regimeData.variant}>{regimeData.label}</Badge>
      </div>

      <div className={cn('flex items-center space-x-4 p-4 rounded-lg', regimeData.bgColor, regimeData.borderColor, 'border')}>
        <div className={cn('p-3 rounded-full', regimeData.bgColor)}>
          <Icon className={cn('h-6 w-6', regimeData.color)} />
        </div>
        <div className="flex-1">
          <div className={cn('text-2xl font-bold', regimeData.color)}>
            {regime > 0 ? 'Bullish' : regime < 0 ? 'Bearish' : 'Neutral'}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            {regime > 0 && 'Upward trend detected. Momentum is positive.'}
            {regime < 0 && 'Downward trend detected. Momentum is negative.'}
            {regime === 0 && 'No clear trend. Market is consolidating.'}
          </p>
        </div>
      </div>

      {/* Regime Strength Indicator */}
      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
          <span>Strength</span>
          <span>{Math.abs(regime * 100).toFixed(0)}%</span>
        </div>
        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
          <div
            className={cn('h-full transition-all duration-500', regimeData.color.replace('text-', 'bg-'))}
            style={{ width: `${Math.abs(regime * 100)}%` }}
          />
        </div>
      </div>
    </div>
  )
}
