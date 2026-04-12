'use client'

import { motion } from 'framer-motion'
import { Zap, TrendingUp, Activity, BarChart3, Info } from 'lucide-react'
import { StockFeatures } from '@/lib/api'
import { Tooltip } from '@/components/ui/tooltip'

interface FeaturePanelProps {
  data: StockFeatures
  showDiscretized: boolean
}

const features = [
  {
    key: 'rsi',
    label: 'RSI',
    icon: Activity,
    description: 'Relative Strength Index - measures momentum',
    getState: (val: number, _close?: number) => val < 30 ? 'OVERSOLD' : val > 70 ? 'OVERBOUGHT' : 'NEUTRAL',
    getColor: (val: number, _close?: number) => val < 30 ? 'text-green-400' : val > 70 ? 'text-red-400' : 'text-yellow-400',
    format: (val: number) => val.toFixed(2)
  },
  {
    key: 'momentum_score',
    label: 'Momentum',
    icon: TrendingUp,
    description: 'Price momentum indicator',
    getState: (val: number, _close?: number) => val > 0.5 ? 'STRONG' : val < -0.5 ? 'WEAK' : 'MODERATE',
    getColor: (val: number, _close?: number) => val > 0.5 ? 'text-green-400' : val < -0.5 ? 'text-red-400' : 'text-yellow-400',
    format: (val: number) => val.toFixed(3)
  },
  {
    key: 'volatility_10',
    label: 'Volatility (10d)',
    icon: BarChart3,
    description: '10-day rolling volatility',
    getState: (val: number, _close?: number) => val > 0.03 ? 'HIGH' : val < 0.01 ? 'LOW' : 'MEDIUM',
    getColor: (val: number, _close?: number) => val > 0.03 ? 'text-red-400' : val < 0.01 ? 'text-green-400' : 'text-yellow-400',
    format: (val: number) => (val * 100).toFixed(2) + '%'
  },
  {
    key: 'macd_diff',
    label: 'MACD Diff',
    icon: Activity,
    description: 'MACD histogram - trend strength',
    getState: (val: number, _close?: number) => val > 1 ? 'BULLISH' : val < -1 ? 'BEARISH' : 'NEUTRAL',
    getColor: (val: number, _close?: number) => val > 1 ? 'text-green-400' : val < -1 ? 'text-red-400' : 'text-yellow-400',
    format: (val: number) => val.toFixed(3)
  },
  {
    key: 'sma_10',
    label: 'SMA 10',
    icon: TrendingUp,
    description: '10-day simple moving average',
    getState: (val: number, close: number) => close > val ? 'ABOVE' : 'BELOW',
    getColor: (val: number, close: number) => close > val ? 'text-green-400' : 'text-red-400',
    format: (val: number) => val.toFixed(2)
  },
  {
    key: 'atr',
    label: 'ATR',
    icon: BarChart3,
    description: 'Average True Range - volatility measure',
    getState: (val: number, _close?: number) => val > 5 ? 'HIGH' : val < 2 ? 'LOW' : 'MEDIUM',
    getColor: (val: number, _close?: number) => val > 5 ? 'text-red-400' : val < 2 ? 'text-green-400' : 'text-yellow-400',
    format: (val: number) => val.toFixed(2)
  }
]

export function FeaturePanel({ data, showDiscretized }: FeaturePanelProps) {
  return (
    <motion.div
      className="section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
    >
      <div className="glass-card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="card-title flex items-center gap-2">
                <Zap className="w-5 h-5 text-teal-400" />
                Engineered Features
              </h2>
              <p className="card-subtitle">Computed technical indicators</p>
            </div>
          </div>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((feature, index) => {
              const value = data[feature.key as keyof StockFeatures] as number
              const state = feature.getState(value, data.close)
              const color = feature.getColor(value, data.close)

              return (
                <motion.div
                  key={feature.key}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.7 + index * 0.05 }}
                  className="relative group"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-teal-500/10 rounded-xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                  <div className="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-5 hover:border-cyan-500/30 transition-all duration-300">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-teal-500/20 flex items-center justify-center">
                          <feature.icon className="w-5 h-5 text-cyan-400" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-white text-sm">{feature.label}</h3>
                        </div>
                      </div>
                      <Tooltip content={feature.description}>
                        <Info className="w-4 h-4 text-gray-500 hover:text-gray-300 cursor-help" />
                      </Tooltip>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-baseline justify-between">
                        <span className="text-xs text-gray-400">Value:</span>
                        <span className="text-lg font-bold text-white">
                          {feature.format(value)}
                        </span>
                      </div>
                      
                      {showDiscretized && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="pt-2 border-t border-white/10"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-400">State:</span>
                            <span className={`text-sm font-bold ${color} px-2 py-1 rounded bg-white/5`}>
                              {state}
                            </span>
                          </div>
                        </motion.div>
                      )}
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
