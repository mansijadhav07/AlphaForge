'use client'

import { motion } from 'framer-motion'
import { Database, Filter, Zap, BarChart3, GitBranch, ArrowRight } from 'lucide-react'

const steps = [
  {
    icon: Database,
    title: 'Raw Market Data',
    description: 'Price, volume, timestamps',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    icon: Filter,
    title: 'Data Cleaning',
    description: 'Handle missing values, outliers',
    color: 'from-cyan-500 to-teal-500'
  },
  {
    icon: Zap,
    title: 'Feature Engineering',
    description: 'RSI, MACD, volatility, momentum',
    color: 'from-teal-500 to-emerald-500'
  },
  {
    icon: BarChart3,
    title: 'Discretization',
    description: 'Convert to categorical states',
    color: 'from-emerald-500 to-green-500'
  },
  {
    icon: GitBranch,
    title: 'Model Input',
    description: 'Feed to Bayesian Network',
    color: 'from-green-500 to-lime-500'
  }
]

export function PipelineFlow() {
  return (
    <motion.div
      className="section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="glass-card">
        <div className="card-header">
          <h2 className="card-title">Data Pipeline Flow</h2>
          <p className="card-subtitle">End-to-end transformation process</p>
        </div>
        <div className="card-body">
          <div className="flex items-center justify-between gap-4 overflow-x-auto pb-4">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center gap-4">
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="flex-shrink-0"
                >
                  <div className="relative group">
                    <div className={`absolute inset-0 bg-gradient-to-br ${step.color} rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity`} />
                    <div className="relative bg-gray-900/90 backdrop-blur-sm border border-white/10 rounded-2xl p-6 min-w-[200px] hover:border-cyan-500/30 transition-all duration-300">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${step.color} flex items-center justify-center mb-4`}>
                        <step.icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="font-semibold text-white mb-2">{step.title}</h3>
                      <p className="text-sm text-gray-400">{step.description}</p>
                    </div>
                  </div>
                </motion.div>
                
                {index < steps.length - 1 && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                    className="flex-shrink-0"
                  >
                    <ArrowRight className="w-8 h-8 text-cyan-400" />
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
