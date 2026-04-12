'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { BarChart3, ArrowRight, ToggleLeft, ToggleRight } from 'lucide-react'
import { StockFeatures } from '@/lib/api'

interface DiscretizationSectionProps {
  data: StockFeatures
  showDiscretized: boolean
  onToggle: () => void
}

const transformations = [
  {
    feature: 'RSI',
    continuous: (data: StockFeatures) => data.rsi.toFixed(2),
    discretized: (data: StockFeatures) => 
      data.rsi < 30 ? 'OVERSOLD' : data.rsi > 70 ? 'OVERBOUGHT' : 'NEUTRAL',
    getColor: (data: StockFeatures) => 
      data.rsi < 30 ? 'text-green-400' : data.rsi > 70 ? 'text-red-400' : 'text-yellow-400'
  },
  {
    feature: 'Volatility',
    continuous: (data: StockFeatures) => (data.volatility_10 * 100).toFixed(2) + '%',
    discretized: (data: StockFeatures) => 
      data.volatility_10 > 0.03 ? 'HIGH' : data.volatility_10 < 0.01 ? 'LOW' : 'MEDIUM',
    getColor: (data: StockFeatures) => 
      data.volatility_10 > 0.03 ? 'text-red-400' : data.volatility_10 < 0.01 ? 'text-green-400' : 'text-yellow-400'
  },
  {
    feature: 'Momentum',
    continuous: (data: StockFeatures) => data.momentum_score.toFixed(3),
    discretized: (data: StockFeatures) => 
      data.momentum_score > 0.5 ? 'STRONG' : data.momentum_score < -0.5 ? 'WEAK' : 'MODERATE',
    getColor: (data: StockFeatures) => 
      data.momentum_score > 0.5 ? 'text-green-400' : data.momentum_score < -0.5 ? 'text-red-400' : 'text-yellow-400'
  },
  {
    feature: 'MACD Diff',
    continuous: (data: StockFeatures) => data.macd_diff.toFixed(3),
    discretized: (data: StockFeatures) => 
      data.macd_diff > 1 ? 'BULLISH' : data.macd_diff < -1 ? 'BEARISH' : 'NEUTRAL',
    getColor: (data: StockFeatures) => 
      data.macd_diff > 1 ? 'text-green-400' : data.macd_diff < -1 ? 'text-red-400' : 'text-yellow-400'
  }
]

export function DiscretizationSection({ data, showDiscretized, onToggle }: DiscretizationSectionProps) {
  return (
    <motion.div
      className="section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7 }}
    >
      <div className="glass-card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="card-title flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-emerald-400" />
                Feature Discretization
              </h2>
              <p className="card-subtitle">Converting continuous values to categorical states</p>
            </div>
            <button
              onClick={onToggle}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-cyan-500/30 transition-all duration-200"
            >
              {showDiscretized ? (
                <>
                  <ToggleRight className="w-5 h-5 text-cyan-400" />
                  <span className="text-sm font-medium text-white">Discretized</span>
                </>
              ) : (
                <>
                  <ToggleLeft className="w-5 h-5 text-gray-400" />
                  <span className="text-sm font-medium text-gray-400">Continuous</span>
                </>
              )}
            </button>
          </div>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {transformations.map((transform, index) => (
              <motion.div
                key={transform.feature}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 + index * 0.05 }}
                className="flex items-center gap-6 p-5 rounded-xl bg-white/5 border border-white/10 hover:border-emerald-500/30 transition-all duration-300"
              >
                {/* Feature Name */}
                <div className="w-32 flex-shrink-0">
                  <span className="text-sm font-semibold text-gray-300">{transform.feature}</span>
                </div>

                {/* Continuous Value */}
                <div className="flex-1 flex items-center gap-4">
                  <div className="flex-1 bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">Continuous</div>
                    <div className="text-lg font-bold text-white">
                      {transform.continuous(data)}
                    </div>
                  </div>

                  {/* Arrow */}
                  <motion.div
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <ArrowRight className="w-6 h-6 text-emerald-400" />
                  </motion.div>

                  {/* Discretized Value */}
                  <div className="flex-1 bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">Discretized</div>
                    <div className={`text-lg font-bold ${transform.getColor(data)}`}>
                      {transform.discretized(data)}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Info Box */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="mt-6 p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20"
          >
            <p className="text-sm text-gray-300 leading-relaxed">
              <span className="font-semibold text-emerald-400">Why Discretization?</span> Bayesian Networks work with categorical states. 
              Converting continuous features into discrete bins (LOW, MEDIUM, HIGH) makes probabilistic inference more efficient 
              and interpretable while preserving the essential information.
            </p>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
