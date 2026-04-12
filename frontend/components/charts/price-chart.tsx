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
} from 'recharts'
import { format } from 'date-fns'
import { StockFeatures } from '@/lib/api'

interface PriceChartProps {
  data: StockFeatures[]
  showIndicators?: {
    sma10?: boolean
    sma30?: boolean
    sma50?: boolean
    bb?: boolean
  }
  highlightLast?: boolean
}

export function PriceChart({ data, showIndicators = {}, highlightLast = false }: PriceChartProps) {
  const chartData = useMemo(() => {
    return data.map((item, index) => ({
      date: format(new Date(item.date), 'MMM dd'),
      price: item.close,
      sma10: item.sma_10,
      sma30: item.sma_30,
      sma50: item.sma_50,
      bb_upper: item.bb_upper,
      bb_lower: item.bb_lower,
      isLast: highlightLast && index === data.length - 1
    }))
  }, [data, highlightLast])

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <defs>
          <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.1} />
          </linearGradient>
        </defs>
        
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
        
        <XAxis
          dataKey="date"
          stroke="rgba(255,255,255,0.5)"
          style={{ fontSize: '12px' }}
        />
        
        <YAxis
          stroke="rgba(255,255,255,0.5)"
          style={{ fontSize: '12px' }}
          domain={['auto', 'auto']}
        />
        
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(10, 10, 10, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)',
          }}
          labelStyle={{ color: '#fff' }}
        />
        
        <Legend
          wrapperStyle={{ fontSize: '12px' }}
          iconType="line"
        />

        {/* Bollinger Bands */}
        {showIndicators.bb && (
          <>
            <Line
              type="monotone"
              dataKey="bb_upper"
              stroke="#f59e0b"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
              name="BB Upper"
            />
            <Line
              type="monotone"
              dataKey="bb_lower"
              stroke="#f59e0b"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
              name="BB Lower"
            />
          </>
        )}

        {/* Moving Averages */}
        {showIndicators.sma10 && (
          <Line
            type="monotone"
            dataKey="sma10"
            stroke="#10b981"
            strokeWidth={1.5}
            dot={false}
            name="SMA 10"
          />
        )}
        
        {showIndicators.sma30 && (
          <Line
            type="monotone"
            dataKey="sma30"
            stroke="#f59e0b"
            strokeWidth={1.5}
            dot={false}
            name="SMA 30"
          />
        )}
        
        {showIndicators.sma50 && (
          <Line
            type="monotone"
            dataKey="sma50"
            stroke="#ef4444"
            strokeWidth={1.5}
            dot={false}
            name="SMA 50"
          />
        )}

        {/* Price Line */}
        <Line
          type="monotone"
          dataKey="price"
          stroke="#06b6d4"
          strokeWidth={2}
          dot={(props: any) => {
            // Highlight last point in live mode
            if (props.payload?.isLast) {
              return (
                <circle
                  cx={props.cx}
                  cy={props.cy}
                  r={6}
                  fill="#06b6d4"
                  stroke="#fff"
                  strokeWidth={2}
                  className="animate-pulse"
                />
              )
            }
            return <></>
          }}
          name="Price"
          fill="url(#priceGradient)"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
