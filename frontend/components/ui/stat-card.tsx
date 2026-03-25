'use client'

import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon?: LucideIcon
  trend?: 'up' | 'down' | 'neutral'
  delay?: number
  className?: string
}

export function StatCard({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  trend = 'neutral',
  delay = 0,
  className 
}: StatCardProps) {
  const trendColor = {
    up: 'text-bullish',
    down: 'text-bearish',
    neutral: 'text-neutral'
  }[trend]

  const trendBg = {
    up: 'bg-bullish/10',
    down: 'bg-bearish/10',
    neutral: 'bg-neutral/10'
  }[trend]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ 
        duration: 0.4, 
        delay,
        ease: [0.25, 0.1, 0.25, 1]
      }}
      whileHover={{ 
        y: -4,
        transition: { duration: 0.2 }
      }}
      className={cn(
        'glass-card p-6 glow-blue-hover transition-all duration-300',
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground mb-2">{title}</p>
          <motion.p 
            className="text-3xl font-bold text-premium"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: delay + 0.1 }}
          >
            {value}
          </motion.p>
          {change !== undefined && (
            <motion.div 
              className={cn('flex items-center gap-1 mt-2', trendColor)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: delay + 0.2 }}
            >
              <span className={cn('text-xs px-2 py-1 rounded-full', trendBg)}>
                {change > 0 ? '+' : ''}{change.toFixed(2)}%
              </span>
            </motion.div>
          )}
        </div>
        {Icon && (
          <motion.div
            initial={{ opacity: 0, rotate: -10 }}
            animate={{ opacity: 1, rotate: 0 }}
            transition={{ delay: delay + 0.15 }}
            className={cn(
              'p-3 rounded-xl',
              trendBg
            )}
          >
            <Icon className={cn('w-6 h-6', trendColor)} />
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
