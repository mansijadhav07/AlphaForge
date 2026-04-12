'use client'

import { motion } from 'framer-motion'
import { GitBranch, ArrowRight, Sparkles } from 'lucide-react'
import Link from 'next/link'

export function ModelConnection() {
  return (
    <motion.div
      className="section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.8 }}
    >
      <div className="glass-card">
        <div className="card-header">
          <h2 className="card-title flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-lime-400" />
            Connection to Bayesian Network
          </h2>
          <p className="card-subtitle">How features feed into the probabilistic model</p>
        </div>
        <div className="card-body">
          <div className="space-y-6">
            {/* Visual Connection */}
            <div className="flex items-center justify-center gap-8 p-8 rounded-xl bg-gradient-to-r from-lime-500/5 to-green-500/5 border border-lime-500/20">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.9 }}
                className="text-center"
              >
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center mb-3 border border-emerald-500/30">
                  <Sparkles className="w-12 h-12 text-emerald-400" />
                </div>
                <div className="text-sm font-semibold text-white">Discretized Features</div>
                <div className="text-xs text-gray-400 mt-1">RSI, Momentum, Volatility...</div>
              </motion.div>

              <motion.div
                animate={{ x: [0, 10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <ArrowRight className="w-12 h-12 text-lime-400" />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.0 }}
                className="text-center"
              >
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-lime-500/20 to-green-500/20 flex items-center justify-center mb-3 border border-lime-500/30">
                  <GitBranch className="w-12 h-12 text-lime-400" />
                </div>
                <div className="text-sm font-semibold text-white">Bayesian Network</div>
                <div className="text-xs text-gray-400 mt-1">Probabilistic inference</div>
              </motion.div>

              <motion.div
                animate={{ x: [0, 10, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
              >
                <ArrowRight className="w-12 h-12 text-lime-400" />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.1 }}
                className="text-center"
              >
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-green-500/20 to-lime-500/20 flex items-center justify-center mb-3 border border-green-500/30">
                  <Sparkles className="w-12 h-12 text-green-400" />
                </div>
                <div className="text-sm font-semibold text-white">Predictions</div>
                <div className="text-xs text-gray-400 mt-1">Future return probabilities</div>
              </motion.div>
            </div>

            {/* Feature List */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                'RSI State',
                'Momentum State',
                'Volatility State',
                'MACD State',
                'Trend Slope',
                'BB Position',
                'Volume Ratio',
                'Market Regime'
              ].map((feature, index) => (
                <motion.div
                  key={feature}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.0 + index * 0.05 }}
                  className="px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-center"
                >
                  <div className="text-sm font-medium text-gray-300">{feature}</div>
                </motion.div>
              ))}
            </div>

            {/* CTA Buttons */}
            <div className="flex gap-4 justify-center pt-4">
              <Link href="/pgm-graph">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-lime-500 to-green-500 text-white font-semibold shadow-lg shadow-lime-500/30 hover:shadow-lime-500/50 transition-all duration-200 flex items-center gap-2"
                >
                  <GitBranch className="w-5 h-5" />
                  View Model Structure
                  <ArrowRight className="w-4 h-4" />
                </motion.button>
              </Link>

              <Link href="/discretization">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:border-lime-500/30 text-white font-semibold transition-all duration-200 flex items-center gap-2"
                >
                  Learn More About Discretization
                  <ArrowRight className="w-4 h-4" />
                </motion.button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
