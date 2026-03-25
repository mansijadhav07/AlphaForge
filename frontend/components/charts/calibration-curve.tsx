'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

interface CalibrationData {
  bin: number
  predicted_prob: number
  actual_freq: number
  count: number
}

interface CalibrationCurveProps {
  data: Record<string, CalibrationData[]>
  title?: string
}

export function CalibrationCurve({ data, title = 'Calibration Curve' }: CalibrationCurveProps) {
  // Prepare data for chart - combine all classes
  const chartData = []
  const maxBins = Math.max(...Object.values(data).map(d => d.length))
  
  for (let i = 0; i < maxBins; i++) {
    const point: any = { bin: i }
    
    Object.entries(data).forEach(([className, bins]) => {
      if (bins[i]) {
        point[`${className}_predicted`] = bins[i].predicted_prob
        point[`${className}_actual`] = bins[i].actual_freq
      }
    })
    
    chartData.push(point)
  }

  // Perfect calibration line data
  const perfectLine = chartData.map((_, i) => ({
    bin: i,
    perfect: i / (maxBins - 1)
  }))

  return (
    <div className="w-full h-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold gradient-text">{title}</h3>
        <p className="text-sm text-muted-foreground">
          Predicted probability vs actual frequency (closer to diagonal = better calibrated)
        </p>
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis
            dataKey="bin"
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            label={{ value: 'Predicted Probability Bin', position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
            tickFormatter={(value) => `${(value / (maxBins - 1) * 100).toFixed(0)}%`}
          />
          <YAxis
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            label={{ value: 'Actual Frequency', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="glass border border-white/10 rounded-lg p-3 shadow-xl">
                    <p className="text-sm font-semibold mb-2">
                      Bin {payload[0].payload.bin}
                    </p>
                    {payload.map((entry: any, index: number) => {
                      if (entry.dataKey === 'perfect') return null
                      const [className, type] = entry.dataKey.split('_')
                      return (
                        <p key={index} className="text-xs" style={{ color: entry.color }}>
                          {className} {type}: {(entry.value * 100).toFixed(1)}%
                        </p>
                      )
                    })}
                  </div>
                )
              }
              return null
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            formatter={(value) => {
              if (value === 'perfect') return 'Perfect Calibration'
              const [className, type] = value.split('_')
              return `${className.charAt(0).toUpperCase() + className.slice(1)} ${type === 'predicted' ? 'Pred' : 'Actual'}`
            }}
          />
          
          {/* Perfect calibration line */}
          <Line
            data={perfectLine}
            type="monotone"
            dataKey="perfect"
            stroke="#6b7280"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
          />
          
          {/* Positive class */}
          {data.positive && (
            <>
              <Line
                type="monotone"
                dataKey="positive_predicted"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={{ fill: '#06b6d4', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="positive_actual"
                stroke="#06b6d4"
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={{ fill: '#06b6d4', r: 3 }}
              />
            </>
          )}
          
          {/* Neutral class */}
          {data.neutral && (
            <>
              <Line
                type="monotone"
                dataKey="neutral_predicted"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={{ fill: '#8b5cf6', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="neutral_actual"
                stroke="#8b5cf6"
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={{ fill: '#8b5cf6', r: 3 }}
              />
            </>
          )}
          
          {/* Negative class */}
          {data.negative && (
            <>
              <Line
                type="monotone"
                dataKey="negative_predicted"
                stroke="#f43f5e"
                strokeWidth={2}
                dot={{ fill: '#f43f5e', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="negative_actual"
                stroke="#f43f5e"
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={{ fill: '#f43f5e', r: 3 }}
              />
            </>
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
