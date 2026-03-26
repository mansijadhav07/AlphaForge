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
import { formatCurrency } from '@/lib/utils'

interface EquityCurveChartProps {
  data: Array<{
    date: string
    value: number
  }>
  initialCapital: number
  showBuyHold?: boolean
  buyHoldData?: Array<{
    date: string
    value: number
  }>
}

export function EquityCurveChart({
  data,
  initialCapital,
  showBuyHold = false,
  buyHoldData,
}: EquityCurveChartProps) {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      console.warn('EquityCurveChart: No data provided')
      return []
    }
    
    console.log('EquityCurveChart: Processing data', { 
      dataLength: data.length, 
      firstItem: data[0], 
      lastItem: data[data.length - 1] 
    })
    
    // Sample data if too many points (keep every 3rd point for better performance)
    const sampledData = data.length > 300 
      ? data.filter((_, index) => index % 3 === 0 || index === data.length - 1)
      : data
    
    const processed = sampledData.map((item, index) => ({
      date: format(new Date(item.date), 'MMM dd'),
      strategy: item.value,
      buyHold: buyHoldData?.[index]?.value || initialCapital,
      initial: initialCapital,
    }))
    
    console.log('EquityCurveChart: Processed data sample', {
      processedLength: processed.length,
      first: processed[0],
      last: processed[processed.length - 1],
      sample: processed.slice(0, 5)
    })
    
    return processed
  }, [data, buyHoldData, initialCapital])

  const finalValue = data && data.length > 0 ? data[data.length - 1]?.value || initialCapital : initialCapital
  const totalReturn = ((finalValue - initialCapital) / initialCapital) * 100
  
  // Calculate Y-axis domain
  const yDomain = useMemo(() => {
    if (!chartData || chartData.length === 0) return [0, 100000]
    
    const values = chartData.map(d => d.strategy)
    const minValue = Math.min(...values)
    const maxValue = Math.max(...values)
    const padding = (maxValue - minValue) * 0.1 || 1000 // 10% padding or $1000 minimum
    
    return [
      Math.floor((minValue - padding) / 1000) * 1000,
      Math.ceil((maxValue + padding) / 1000) * 1000
    ]
  }, [chartData])
  
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[400px] text-gray-400">
        No equity curve data available
      </div>
    )
  }

  return (
    <div className="space-y-4 w-full">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-muted-foreground">Final Portfolio Value</div>
          <div className="text-2xl font-bold">{formatCurrency(finalValue)}</div>
        </div>
        <div className="text-right">
          <div className="text-sm text-muted-foreground">Total Return</div>
          <div className={`text-2xl font-bold ${totalReturn >= 0 ? 'text-bullish' : 'text-bearish'}`}>
            {totalReturn >= 0 ? '+' : ''}{totalReturn.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="w-full h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
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
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
              domain={yDomain}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(10, 10, 10, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                backdropFilter: 'blur(10px)',
              }}
              formatter={(value: number) => formatCurrency(value)}
              labelStyle={{ color: '#fff' }}
            />

            <Legend wrapperStyle={{ fontSize: '12px' }} />

            {/* Initial Capital Reference Line */}
            <ReferenceLine
              y={initialCapital}
              stroke="rgba(255,255,255,0.3)"
              strokeDasharray="3 3"
              label={{ value: 'Initial', position: 'right', fill: 'rgba(255,255,255,0.5)' }}
            />

            {/* Buy & Hold Line */}
            {showBuyHold && buyHoldData && (
              <Line
                type="monotone"
                dataKey="buyHold"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
                name="Buy & Hold"
                strokeDasharray="5 5"
              />
            )}

            {/* Strategy Equity Curve */}
            <Line
              type="monotone"
              dataKey="strategy"
              stroke="#06b6d4"
              strokeWidth={3}
              dot={false}
              name="Strategy"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
