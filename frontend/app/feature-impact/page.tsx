'use client'

import { useEffect, useState } from 'react'
import { FeatureImpactChart } from '@/components/charts/feature-impact-chart'
import { api } from '@/lib/api'
import { Loader2, TrendingUp, Info, BarChart3 } from 'lucide-react'

interface FeatureImpact {
  feature: string
  impact: number
  current_state: string
}

export default function FeatureImpactPage() {
  const [symbol, setSymbol] = useState('AAPL')
  const [impactData, setImpactData] = useState<FeatureImpact[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN']

  useEffect(() => {
    loadFeatureImpact()
  }, [symbol])

  const loadFeatureImpact = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getPGMFeatureImpact(symbol)
      setImpactData(data.impacts)
    } catch (err) {
      setError('Failed to load feature impact data')
      console.error('Error loading feature impact:', err)
    } finally {
      setLoading(false)
    }
  }

  // Calculate statistics
  const totalImpact = impactData?.reduce((sum, item) => sum + item.impact, 0) || 0
  const avgImpact = impactData ? totalImpact / impactData.length : 0
  const topFeature = impactData?.[0]
  const normalizedData = impactData?.map(item => ({
    ...item,
    impact: item.impact / totalImpact // Normalize to sum to 1
  }))

  return (
    <div className="min-h-screen pt-16 pb-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="absolute inset-0 bg-neon-blue blur-lg opacity-50" />
                <div className="relative bg-gradient-to-br from-neon-blue to-neon-teal p-3 rounded-xl">
                  <BarChart3 className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold gradient-text">Feature Contribution Analysis</h1>
                <p className="text-muted-foreground">
                  Understand how each feature influences predictions
                </p>
              </div>
            </div>

            {/* Symbol Selector */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">Symbol:</span>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="glass border border-white/10 rounded-lg px-4 py-2 text-sm font-medium bg-transparent focus:outline-none focus:ring-2 focus:ring-neon-blue"
              >
                {symbols.map((sym) => (
                  <option key={sym} value={sym} className="bg-gray-900">
                    {sym}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Info Banner */}
          <div className="glass border border-neon-blue/20 rounded-xl p-4">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-neon-blue mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-neon-blue mb-1">
                  About Feature Contribution
                </h3>
                <p className="text-sm text-muted-foreground">
                  This analysis shows how much each feature contributes to the probabilistic prediction.
                  Impact scores are calculated using sensitivity analysis - measuring how the prediction
                  changes when each feature is removed. Higher scores indicate stronger influence.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        {impactData && !loading && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="glass border border-white/10 rounded-xl p-4">
              <div className="text-sm text-muted-foreground mb-1">Total Features</div>
              <div className="text-2xl font-bold gradient-text">{impactData.length}</div>
            </div>
            <div className="glass border border-white/10 rounded-xl p-4">
              <div className="text-sm text-muted-foreground mb-1">Avg Impact</div>
              <div className="text-2xl font-bold gradient-text">
                {(avgImpact * 100).toFixed(1)}%
              </div>
            </div>
            <div className="glass border border-white/10 rounded-xl p-4">
              <div className="text-sm text-muted-foreground mb-1">Top Feature</div>
              <div className="text-lg font-bold gradient-text">{topFeature?.feature}</div>
              <div className="text-xs text-muted-foreground">{topFeature?.current_state}</div>
            </div>
            <div className="glass border border-white/10 rounded-xl p-4">
              <div className="text-sm text-muted-foreground mb-1">Top Impact</div>
              <div className="text-2xl font-bold gradient-text">
                {topFeature ? (topFeature.impact * 100).toFixed(1) : '0'}%
              </div>
            </div>
          </div>
        )}

        {/* Main Chart */}
        <div className="glass border border-white/10 rounded-xl p-6 mb-6" style={{ height: '500px' }}>
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin text-neon-blue mx-auto mb-4" />
                <p className="text-muted-foreground">Loading feature impact data...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-red-500 mb-2">⚠️</div>
                <p className="text-muted-foreground">{error}</p>
                <button
                  onClick={loadFeatureImpact}
                  className="mt-4 px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 text-neon-blue rounded-lg transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {normalizedData && !loading && !error && (
            <FeatureImpactChart data={normalizedData} />
          )}
        </div>

        {/* Feature Details Table */}
        {impactData && !loading && (
          <div className="glass border border-white/10 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-white/10">
              <h3 className="text-lg font-semibold gradient-text">Detailed Feature Analysis</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-white/5">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Feature
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Current State
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Impact Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Normalized %
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Influence
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {impactData.map((item, index) => {
                    const normalizedPercent = (item.impact / totalImpact) * 100
                    const influence = 
                      item.impact >= 0.20 ? 'Very High' :
                      item.impact >= 0.15 ? 'High' :
                      item.impact >= 0.10 ? 'Medium' : 'Low'
                    
                    return (
                      <tr key={index} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-neon-blue">
                          #{index + 1}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          {item.feature}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className="px-2 py-1 rounded-full bg-white/10 text-xs">
                            {item.current_state}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">
                          {item.impact.toFixed(3)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex items-center space-x-2">
                            <div className="flex-1 bg-white/10 rounded-full h-2 max-w-[100px]">
                              <div
                                className="bg-gradient-to-r from-neon-blue to-neon-teal h-2 rounded-full"
                                style={{ width: `${normalizedPercent}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium">{normalizedPercent.toFixed(1)}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            influence === 'Very High' ? 'bg-neon-blue/20 text-neon-blue' :
                            influence === 'High' ? 'bg-neon-teal/20 text-neon-teal' :
                            influence === 'Medium' ? 'bg-purple-500/20 text-purple-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {influence}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Insights */}
        {impactData && !loading && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="glass border border-white/10 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-neon-blue mb-2">Key Insights</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start space-x-2">
                  <TrendingUp className="h-4 w-4 text-neon-blue mt-0.5 flex-shrink-0" />
                  <span>
                    <span className="font-medium text-foreground">{topFeature?.feature}</span> has the
                    strongest influence on predictions ({((topFeature?.impact || 0) * 100).toFixed(1)}%)
                  </span>
                </li>
                <li className="flex items-start space-x-2">
                  <TrendingUp className="h-4 w-4 text-neon-blue mt-0.5 flex-shrink-0" />
                  <span>
                    Top 3 features account for{' '}
                    <span className="font-medium text-foreground">
                      {((impactData.slice(0, 3).reduce((sum, item) => sum + item.impact, 0) / totalImpact) * 100).toFixed(1)}%
                    </span>{' '}
                    of total influence
                  </span>
                </li>
                <li className="flex items-start space-x-2">
                  <TrendingUp className="h-4 w-4 text-neon-blue mt-0.5 flex-shrink-0" />
                  <span>
                    Current state of {topFeature?.feature} is{' '}
                    <span className="font-medium text-foreground">{topFeature?.current_state}</span>
                  </span>
                </li>
              </ul>
            </div>

            <div className="glass border border-white/10 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-purple-400 mb-2">Methodology</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Impact scores calculated using sensitivity analysis</li>
                <li>• Measures prediction change when each feature is removed</li>
                <li>• Uses Total Variation Distance between distributions</li>
                <li>• Normalized scores show relative contribution percentages</li>
                <li>• Higher scores indicate stronger causal influence</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
