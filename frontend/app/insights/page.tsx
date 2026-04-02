'use client'

import { useEffect, useState } from 'react'
import {
  Brain,
  TrendingUp,
  AlertTriangle,
  Activity,
  Zap,
  Target,
  Eye,
  BarChart3,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { InsightCard } from '@/components/ui/insight-card'
import { StatCard } from '@/components/ui/stat-card'
import { FullScreenLoader } from '@/components/ui/fullscreen-loader'
import { api, type Insight, type MarketOverview } from '@/lib/api'

export default function InsightsPage() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [marketData, setMarketData] = useState<MarketOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'warning' | 'info' | 'success'>('all')

  useEffect(() => {
    const fetchData = async () => {
      const [insightsData, marketOverview] = await Promise.all([
        api.getInsights(),
        api.getMarketOverview(),
      ])
      setInsights(insightsData)
      setMarketData(marketOverview)
      setLoading(false)
    }

    fetchData()

    // Reduced refresh to 60 seconds (data is cached for 60s on backend)
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  const filteredInsights = filter === 'all' 
    ? insights 
    : insights.filter((insight) => insight.type === filter)

  const insightCounts = {
    total: insights.length,
    warnings: insights.filter((i) => i.type === 'warning').length,
    opportunities: insights.filter((i) => i.type === 'success').length,
    info: insights.filter((i) => i.type === 'info').length,
  }

  if (loading) {
    return <FullScreenLoader message="Loading market insights" />
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div className="flex items-center space-x-3 mb-3">
          <div className="p-2.5 rounded-lg bg-gradient-to-br from-cyan-500/20 to-teal-500/20 border border-cyan-500/20">
            <Brain className="h-6 w-6 text-cyan-400" />
          </div>
          <h1 className="page-title">Market Insights</h1>
        </div>
        <p className="page-description">
          AI-powered analysis and opportunity detection
        </p>
      </div>

      {/* Stats Overview */}
      <div className="card-grid-4 mb-8">
        <StatCard
          title="Total Insights"
          value={insightCounts.total}
          icon={Brain}
          trend="neutral"
        />
        <StatCard
          title="Warnings"
          value={insightCounts.warnings}
          icon={AlertTriangle}
          trend="down"
        />
        <StatCard
          title="Opportunities"
          value={insightCounts.opportunities}
          icon={Target}
          trend="up"
        />
        <StatCard
          title="Market Updates"
          value={insightCounts.info}
          icon={Activity}
          trend="neutral"
        />
      </div>

      {/* Market Pulse */}
      {marketData && (
        <div className="section">
          <div className="glass-card glass-hover">
            <div className="card-header">
              <h2 className="card-title flex items-center gap-2">
                <Zap className="h-5 w-5 text-cyan-400" />
                Market Pulse
              </h2>
              <p className="card-subtitle">Real-time market conditions</p>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Market Regime */}
                <div className="space-y-2">
                  <div className="text-sm text-gray-400">Market Regime</div>
                  <div className="flex items-center space-x-2">
                    <Badge
                      variant={
                        marketData.market_regime === 'Bull'
                          ? 'bullish'
                          : marketData.market_regime === 'Bear'
                          ? 'bearish'
                          : 'neutral'
                      }
                    >
                      {marketData.market_regime}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-500">
                    {marketData.market_regime === 'Bull' && 'Upward momentum detected'}
                    {marketData.market_regime === 'Bear' && 'Downward pressure observed'}
                    {marketData.market_regime === 'Sideways' && 'Consolidation phase'}
                  </p>
                </div>

                {/* Volatility */}
                <div className="space-y-2">
                  <div className="text-sm text-gray-400">Volatility Index</div>
                  <div className="text-2xl font-bold text-white">{marketData.volatility_index.toFixed(2)}</div>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          marketData.volatility_index > 25
                            ? 'bg-bearish'
                            : marketData.volatility_index > 15
                            ? 'bg-neutral'
                            : 'bg-bullish'
                        }`}
                        style={{ width: `${Math.min(marketData.volatility_index * 2, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">
                      {marketData.volatility_index > 25
                        ? 'High'
                        : marketData.volatility_index > 15
                        ? 'Moderate'
                        : 'Low'}
                    </span>
                  </div>
                </div>

                {/* Active Signals */}
                <div className="space-y-2">
                  <div className="text-sm text-gray-400">Active Signals</div>
                  <div className="text-2xl font-bold text-white">{marketData.signals.length}</div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-bullish" />
                    <span className="text-xs text-gray-500">
                      {marketData.signals.filter((s) => s.signal === 'BUY').length} Buy signals
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            filter === 'all'
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
              : 'bg-white/5 text-gray-400 hover:bg-white/10 border border-transparent'
          }`}
        >
          All ({insightCounts.total})
        </button>
        <button
          onClick={() => setFilter('warning')}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            filter === 'warning'
              ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
              : 'bg-white/5 text-gray-400 hover:bg-white/10 border border-transparent'
          }`}
        >
          Warnings ({insightCounts.warnings})
        </button>
        <button
          onClick={() => setFilter('success')}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            filter === 'success'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'bg-white/5 text-gray-400 hover:bg-white/10 border border-transparent'
          }`}
        >
          Opportunities ({insightCounts.opportunities})
        </button>
        <button
          onClick={() => setFilter('info')}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            filter === 'info'
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
              : 'bg-white/5 text-gray-400 hover:bg-white/10 border border-transparent'
          }`}
        >
          Updates ({insightCounts.info})
        </button>
      </div>

      {/* Insights List */}
      <div className="section">
        {filteredInsights.length === 0 ? (
          <div className="glass-card text-center py-12">
            <Eye className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">No insights found</h3>
            <p className="text-sm text-gray-400">
              {filter === 'all'
                ? 'No insights available at the moment'
                : `No ${filter} insights found`}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredInsights.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="section">
        <div className="glass-card glass-hover">
          <div className="card-header">
            <h2 className="card-title flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-teal-400" />
              Quick Actions
            </h2>
            <p className="card-subtitle">Common tasks and shortcuts</p>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="p-4 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-emerald-500/30 transition-all text-left group">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-emerald-500/10 group-hover:bg-emerald-500/20 transition-colors">
                    <TrendingUp className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <div className="font-semibold text-white">View Top Opportunities</div>
                    <div className="text-xs text-gray-400">
                      {insightCounts.opportunities} available
                    </div>
                  </div>
                </div>
              </button>

              <button className="p-4 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-yellow-500/30 transition-all text-left group">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-yellow-500/10 group-hover:bg-yellow-500/20 transition-colors">
                    <AlertTriangle className="h-5 w-5 text-yellow-400" />
                  </div>
                  <div>
                    <div className="font-semibold text-white">Review Warnings</div>
                    <div className="text-xs text-gray-400">
                      {insightCounts.warnings} alerts
                    </div>
                  </div>
                </div>
              </button>

              <button className="p-4 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-cyan-500/30 transition-all text-left group">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-cyan-500/10 group-hover:bg-cyan-500/20 transition-colors">
                    <Activity className="h-5 w-5 text-cyan-400" />
                  </div>
                  <div>
                    <div className="font-semibold text-white">Market Analysis</div>
                    <div className="text-xs text-gray-400">Full report</div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
