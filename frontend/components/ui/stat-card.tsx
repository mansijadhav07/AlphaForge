'use client'

import { LucideIcon } from 'lucide-react'
import { Card, CardContent } from './card'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: LucideIcon
  iconColor?: string
  iconBgColor?: string
}

export function StatCard({
  title,
  value,
  change,
  icon: Icon,
  iconColor = 'text-neon-blue',
  iconBgColor = 'bg-neon-blue/10',
}: StatCardProps) {
  return (
    <Card className="card-glow-hover">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground font-medium">{title}</p>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-bold">{value}</span>
              {change !== undefined && (
                <span
                  className={cn(
                    'text-sm font-medium',
                    change >= 0 ? 'text-bullish' : 'text-bearish'
                  )}
                >
                  {change >= 0 ? '+' : ''}
                  {change.toFixed(1)}%
                </span>
              )}
            </div>
          </div>
          <div className={cn('p-4 rounded-xl', iconBgColor)}>
            <Icon className={cn('h-8 w-8', iconColor)} />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
