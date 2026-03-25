'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface FeatureImpact {
  feature: string
  impact: number
  current_state: string
}

interface FeatureImpactChartProps {
  data: FeatureImpact[]
  title?: string
}

export function FeatureImpactChart({ data, title = 'Feature Contribution Analysis' }: FeatureImpactChartProps) {
  // Sort by impact score (descending)
  const sortedData = [...data].sort((a, b) => b.impact - a.impact)

  // Prepare data for chart
  const chartData = sortedData.map(item => ({
    name: item.feature,
    impact: item.impact,
    impactPercent: (item.impact * 100).toFixed(1),
    state: item.current_state,
  }))

  // Color scale based on impact
  const getBarColor = (impact: number) => {
    if (impact >= 0.20) return '#06b6d4' // High impact - neon blue
    if (impact >= 0.15) return '#14b8a6' // Medium-high - neon teal
    if (impact >= 0.10) return '#8b5cf6' // Medium - purple
    return '#6b7280' // Low - gray
  }

  return (
    <div className="w-full h-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold gradient-text">{title}</h3>
        <p className="text-sm text-muted-foreground">
          How each feature contributes to the prediction
        </p>
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis
            type="number"
            domain={[0, 'auto']}
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            width={110}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload
                return (
                  <div className="glass border border-white/10 rounded-lg p-3 shadow-xl">
                    <p className="font-semibold text-neon-blue mb-1">{data.name}</p>
                    <p className="text-sm text-muted-foreground mb-1">
                      Impact: <span className="text-foreground font-medium">{data.impactPercent}%</span>
                    </p>
                    <p className="text-sm text-muted-foreground">
                      State: <span className="text-foreground font-medium">{data.state}</span>
                    </p>
                  </div>
                )
              }
              return null
            }}
          />
          <Bar dataKey="impact" radius={[0, 8, 8, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.impact)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: '#06b6d4' }} />
          <span className="text-muted-foreground">High Impact (&gt;20%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: '#14b8a6' }} />
          <span className="text-muted-foreground">Medium-High (15-20%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: '#8b5cf6' }} />
          <span className="text-muted-foreground">Medium (10-15%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: '#6b7280' }} />
          <span className="text-muted-foreground">Low (&lt;10%)</span>
        </div>
      </div>
    </div>
  )
}
