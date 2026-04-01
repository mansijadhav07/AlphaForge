'use client'

import { useState, useEffect } from 'react'
import { Activity, Pause, RefreshCw, Clock } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface LiveIndicatorProps {
  isLive: boolean
  lastUpdated: Date | null
  onToggle: () => void
  isLoading?: boolean
  error?: string | null
}

export function LiveIndicator({
  isLive,
  lastUpdated,
  onToggle,
  isLoading = false,
  error = null
}: LiveIndicatorProps) {
  const [timeAgo, setTimeAgo] = useState<string>('')

  // Update time ago every second
  useEffect(() => {
    if (!lastUpdated) return

    const updateTimeAgo = () => {
      setTimeAgo(formatDistanceToNow(lastUpdated, { addSuffix: true }))
    }

    updateTimeAgo()
    const interval = setInterval(updateTimeAgo, 1000)

    return () => clearInterval(interval)
  }, [lastUpdated])

  return (
    <div className="flex items-center space-x-4">
      {/* Status Indicator */}
      <div className="flex items-center space-x-2">
        {isLive ? (
          <>
            <div className="relative">
              <Activity className="h-5 w-5 text-bullish" />
              {!isLoading && (
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-bullish opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-bullish"></span>
                </span>
              )}
            </div>
            <span className="text-sm font-medium text-bullish">LIVE</span>
          </>
        ) : (
          <>
            <Pause className="h-5 w-5 text-neutral" />
            <span className="text-sm font-medium text-neutral">STATIC</span>
          </>
        )}
      </div>

      {/* Last Updated */}
      {lastUpdated && (
        <div className="flex items-center space-x-1 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span>Updated {timeAgo}</span>
        </div>
      )}

      {/* Loading Indicator */}
      {isLoading && (
        <RefreshCw className="h-4 w-4 text-neon-blue animate-spin" />
      )}

      {/* Error Indicator */}
      {error && (
        <div className="text-xs text-bearish">
          ⚠️ {error}
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className={`
          px-4 py-2 rounded-lg text-sm font-medium transition-all
          ${isLive 
            ? 'bg-bullish/20 text-bullish hover:bg-bullish/30' 
            : 'bg-neutral/20 text-neutral hover:bg-neutral/30'
          }
        `}
      >
        {isLive ? 'Pause Updates' : 'Enable Live Mode'}
      </button>
    </div>
  )
}
