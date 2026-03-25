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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { InsightCard } from '@/components/ui/insight-card'
import { StatCard } from '@/components/ui/stat-card'
import { api, type Insight, type MarketOverview } from '@/lib/api'

export default function InsightsPage() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [marketData, setMarketData] = useState<MarketOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'warning' | 'info' | 'success'>('all')

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      const [insightsData, marketOverview] = await Promise.all([
        api.getInsights(),
        api.getMarketOverview(),
      ])
      setInsights(insightsData)
      setMarketData(marketOverview)
      setLoading(false)
    }

    fetchData()

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
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
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-white/10 rounded w-1/4" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-white/10 rounded" />
            ))}
          </div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-40 bg-white/10 rounded" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8 animate-slide-in">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-gradient-to-br from-neon-blue/20 to-neon-teal/20">
            <Brain className="h-8 w-8 text-neon-blue" />
          </div>
          <div>
            <h1 className="text-4xl font-bold gradient-text">Market Insights</h1>
            <p className="text-muted-foreground">
              AI-powered analysis and opportunity detection
            </p>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Insights"
          value={insightCounts.total}
          icon={Brain}
          iconColor="text-neon-blue"
          iconBgColor="bg-neon-blue/10"
        />
        <StatCard
          title="Warnings"
          value={insightCounts.warnings}
          icon={AlertTriangle}
          iconColor="text-neutral"
          iconBgColor="bg-neutral/10"
        />
        <StatCard
          title="Opportunities"
          value={insightCounts.opportunities}
          icon={Target}
          iconColor="text-bullish"
          iconBgColor="bg-bullish/10"
        />
        <StatCard
          title="Market Updates"
          value={insightCounts.info}
          icon={Activity}
          iconColor="text-neon-teal"
          iconBgColor="bg-neon-teal/10"
        />
      </div>

      {/* Market Pulse */}
      {marketData && (
        <Card className="border-neon-blue/30 card-glow">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-neon-blue" />
              <span>Market Pulse</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Market Regime */}
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Market Regime</div>
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
                  <span className="text-2xl font-bold">{marketData.market_regime}</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  {marketData.market_regime === 'Bull' && 'Upward momentum detected'}
                  {marketData.market_regime === 'Bear' && 'Downward pressure observed'}
                  {marketData.market_regime === 'Sideways' && 'Consolidation phase'}
                </p>
              </div>

              {/* Volatility */}
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Volatility Index</div>
                <div className="text-2xl font-bold">{marketData.volatility_index.toFixed(2)}</div>
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
                  <span className="text-xs text-muted-foreground">
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
                <div className="text-sm text-muted-foreground">Active Signals</div>
                <div className="text-2xl font-bold">{marketData.signals.length}</div>
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4 text-bullish" />
                  <span className="text-xs text-muted-foreground">
                    {marketData.signals.filter((s) => s.signal === 'BUY').length} Buy signals
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filter === 'all'
              ? 'bg-neon-blue/20 text-neon-blue'
              : 'bg-white/5 text-muted-foreground hover:bg-white/10'
          }`}
        >
          All ({insightCounts.total})
        </button>
        <button
          onClick={() => setFilter('warning')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filter === 'warning'
              ? 'bg-neutral/20 text-neutral'
              : 'bg-white/5 text-muted-foreground hover:bg-white/10'
          }`}
        >
          Warnings ({insightCounts.warnings})
        </button>
        <button
          onClick={() => setFilter('success')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filter === 'success'
              ? 'bg-bullish/20 text-bullish'
              : 'bg-white/5 text-muted-foreground hover:bg-white/10'
          }`}
        >
          Opportunities ({insightCounts.opportunities})
        </button>
        <button
          onClick={() => setFilter('info')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filter === 'info'
              ? 'bg-neon-blue/20 text-neon-blue'
              : 'bg-white/5 text-muted-foreground hover:bg-white/10'
          }`}
        >
          Updates ({insightCounts.info})
        </button>
      </div>

      {/* Insights List */}
      <div className="space-y-4">
        {filteredInsights.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Eye className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No insights found</h3>
                <p className="text-sm text-muted-foreground">
                  {filter === 'all'
                    ? 'No insights available at the moment'
                    : `No ${filter} insights found`}
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredInsights.map((insight) => (
            <InsightCard key={insight.id} insight={insight} />
          ))
        )}
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-neon-teal" />
            <span>Quick Actions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 rounded-lg glass-hover text-left group">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-bullish/10 group-hover:bg-bullish/20 transition-colors">
                  <TrendingUp className="h-5 w-5 text-bullish" />
                </div>
                <div>
                  <div className="font-semibold">View Top Opportunities</div>
                  <div className="text-xs text-muted-foreground">
                    {insightCounts.opportunities} available
                  </div>
                </div>
              </div>
            </button>

            <button className="p-4 rounded-lg glass-hover text-left group">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-neutral/10 group-hover:bg-neutral/20 transition-colors">
                  <AlertTriangle className="h-5 w-5 text-neutral" />
                </div>
                <div>
                  <div className="font-semibold">Review Warnings</div>
                  <div className="text-xs text-muted-foreground">
                    {insightCounts.warnings} alerts
                  </div>
                </div>
              </div>
            </button>

            <button className="p-4 rounded-lg glass-hover text-left group">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-neon-blue/10 group-hover:bg-neon-blue/20 transition-colors">
                  <Activity className="h-5 w-5 text-neon-blue" />
                </div>
                <div>
                  <div className="font-semibold">Market Analysis</div>
                  <div className="text-xs text-muted-foreground">Full report</div>
                </div>
              </div>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
