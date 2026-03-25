'use client'

import { LucideIcon, AlertTriangle, Info, CheckCircle, TrendingUp, Zap } from 'lucide-react'
import { Card, CardContent } from './card'
import { Badge } from './badge'
import { cn } from '@/lib/utils'
import { Insight } from '@/lib/api'

interface InsightCardProps {
  insight: Insight
  className?: string
}

const typeConfig = {
  warning: {
    icon: AlertTriangle,
    color: 'text-neutral',
    bgColor: 'bg-neutral/10',
    borderColor: 'border-neutral/30',
    badge: 'Warning',
    badgeVariant: 'neutral' as const,
  },
  info: {
    icon: Info,
    color: 'text-neon-blue',
    bgColor: 'bg-neon-blue/10',
    borderColor: 'border-neon-blue/30',
    badge: 'Info',
    badgeVariant: 'default' as const,
  },
  success: {
    icon: CheckCircle,
    color: 'text-bullish',
    bgColor: 'bg-bullish/10',
    borderColor: 'border-bullish/30',
    badge: 'Opportunity',
    badgeVariant: 'bullish' as const,
  },
}

export function InsightCard({ insight, className }: InsightCardProps) {
  const config = typeConfig[insight.type]
  const Icon = config.icon

  return (
    <Card className={cn('border-l-4 card-glow-hover', config.borderColor, className)}>
      <CardContent className="pt-6">
        <div className="flex items-start space-x-4">
          {/* Icon */}
          <div className={cn('p-3 rounded-lg', config.bgColor)}>
            <Icon className={cn('h-6 w-6', config.color)} />
          </div>

          {/* Content */}
          <div className="flex-1 space-y-2">
            <div className="flex items-start justify-between">
              <h3 className="font-semibold text-lg">{insight.title}</h3>
              <Badge variant={config.badgeVariant} className="ml-2">
                {config.badge}
              </Badge>
            </div>

            <p className="text-sm text-muted-foreground leading-relaxed">
              {insight.description}
            </p>

            <div className="flex items-center justify-between pt-2">
              {insight.ticker && (
                <Badge variant="outline" className="text-xs">
                  {insight.ticker}
                </Badge>
              )}
              <span className="text-xs text-muted-foreground">
                {new Date(insight.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
