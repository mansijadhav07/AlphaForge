'use client'

import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
  Bar,
} from 'recharts'
import { format } from 'date-fns'
import { StockFeatures } from '@/lib/api'

interface IndicatorChartProps {
  data: StockFeatures[]
  type: 'rsi' | 'macd' | 'volume'
}

export function IndicatorChart({ data, type }: IndicatorChartProps) {
  const chartData = useMemo(() => {
    return data.map((item) => ({
      date: format(new Date(item.date), 'MMM dd'),
      rsi: item.rsi,
      macd: item.macd,
      macd_signal: item.macd_signal,
      macd_diff: item.macd_diff,
      volume: item.volume,
    }))
  }, [data])

  if (type === 'rsi') {
    return (
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          
          <XAxis
            dataKey="date"
            stroke="rgba(255,255,255,0.5)"
            style={{ fontSize: '12px' }}
          />
          
          <YAxis
            stroke="rgba(255,255,255,0.5)"
            style={{ fontSize: '12px' }}
            domain={[0, 100]}
          />
          
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(10, 10, 10, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
            }}
          />
          
          <Legend wrapperStyle={{ fontSize: '12px' }} />

          {/* Overbought/Oversold Lines */}
          <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label="Overbought" />
          <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label="Oversold" />
          <ReferenceLine y={50} stroke="rgba(255,255,255,0.3)" strokeDasharray="3 3" />

          <Line
            type="monotone"
            dataKey="rsi"
            stroke="#a855f7"
            strokeWidth={2}
            dot={false}
            name="RSI"
          />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  if (type === 'macd') {
    return (
      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          
          <XAxis
            dataKey="date"
            stroke="rgba(255,255,255,0.5)"
            style={{ fontSize: '12px' }}
          />
          
          <YAxis
            stroke="rgba(255,255,255,0.5)"
            style={{ fontSize: '12px' }}
          />
          
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(10, 10, 10, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
            }}
          />
          
          <Legend wrapperStyle={{ fontSize: '12px' }} />

          <ReferenceLine y={0} stroke="rgba(255,255,255,0.3)" />

          <Bar
            dataKey="macd_diff"
            fill="#06b6d4"
            opacity={0.6}
            name="MACD Histogram"
          />

          <Line
            type="monotone"
            dataKey="macd"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="MACD"
          />
          
          <Line
            type="monotone"
            dataKey="macd_signal"
            stroke="#ef4444"
            strokeWidth={2}
            dot={false}
            name="Signal"
          />
        </ComposedChart>
      </ResponsiveContainer>
    )
  }

  // Volume chart
  return (
    <ResponsiveContainer width="100%" height={150}>
      <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
        
        <XAxis
          dataKey="date"
          stroke="rgba(255,255,255,0.5)"
          style={{ fontSize: '12px' }}
        />
        
        <YAxis
          stroke="rgba(255,255,255,0.5)"
          style={{ fontSize: '12px' }}
        />
        
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(10, 10, 10, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '8px',
          }}
          formatter={(value: number) => value.toLocaleString()}
        />

        <Bar
          dataKey="volume"
          fill="#06b6d4"
          opacity={0.6}
          name="Volume"
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
