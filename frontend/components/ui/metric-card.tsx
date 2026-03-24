'use client'

import { LucideIcon } from 'lucide-react'
import { Card, CardContent } from './card'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: LucideIcon
  trend?: 'up' | 'down' | 'neutral'
  format?: 'currency' | 'percentage' | 'number'
  colorize?: boolean
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  format = 'number',
  colorize = false,
}: MetricCardProps) {
  const formatValue = (val: string | number): string => {
    if (typeof val === 'string') return val

    switch (format) {
      case 'currency':
        return `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
      case 'percentage':
        return `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`
      default:
        return typeof val === 'number' ? val.toFixed(2) : val
    }
  }

  const getValueColor = (): string => {
    if (!colorize) return 'text-foreground'

    if (trend === 'up') return 'text-bullish'
    if (trend === 'down') return 'text-bearish'

    if (typeof value === 'number') {
      if (value > 0) return 'text-bullish'
      if (value < 0) return 'text-bearish'
    }

    return 'text-muted-foreground'
  }

  return (
    <Card className="card-glow-hover">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {Icon && (
                <div className="p-2 rounded-lg bg-neon-blue/10">
                  <Icon className="h-4 w-4 text-neon-blue" />
                </div>
              )}
              <span className="text-sm font-medium text-muted-foreground">{title}</span>
            </div>
            <div className={cn('text-2xl font-bold', getValueColor())}>
              {formatValue(value)}
            </div>
            {subtitle && (
              <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
