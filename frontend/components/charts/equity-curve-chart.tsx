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
    return data.map((item, index) => ({
      date: format(new Date(item.date), 'MMM dd'),
      strategy: item.value,
      buyHold: buyHoldData?.[index]?.value || initialCapital,
      initial: initialCapital,
    }))
  }, [data, buyHoldData, initialCapital])

  const finalValue = data[data.length - 1]?.value || initialCapital
  const totalReturn = ((finalValue - initialCapital) / initialCapital) * 100

  return (
    <div className="space-y-4">
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

      <ResponsiveContainer width="100%" height={400}>
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
          <Area
            type="monotone"
            dataKey="strategy"
            stroke="#06b6d4"
            strokeWidth={3}
            fill="url(#equityGradient)"
            name="Strategy"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
