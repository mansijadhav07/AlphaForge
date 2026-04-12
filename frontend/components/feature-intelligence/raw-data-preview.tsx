'use client'

import { motion } from 'framer-motion'
import { Database } from 'lucide-react'
import { StockFeatures } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'

interface RawDataPreviewProps {
  data: StockFeatures[]
}

export function RawDataPreview({ data }: RawDataPreviewProps) {
  return (
    <motion.div
      className="section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <div className="glass-card">
        <div className="card-header">
          <h2 className="card-title flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Raw Market Data
          </h2>
          <p className="card-subtitle">Latest 5 trading days</p>
        </div>
        <div className="card-body">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Date</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Open</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">High</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Low</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Close</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Volume</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row, index) => (
                  <motion.tr
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.05 }}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >
                    <td className="py-3 px-4 text-sm text-white font-medium">{row.date}</td>
                    <td className="py-3 px-4 text-sm text-gray-300 text-right">{formatCurrency(row.open)}</td>
                    <td className="py-3 px-4 text-sm text-green-400 text-right">{formatCurrency(row.high)}</td>
                    <td className="py-3 px-4 text-sm text-red-400 text-right">{formatCurrency(row.low)}</td>
                    <td className="py-3 px-4 text-sm text-white font-semibold text-right">{formatCurrency(row.close)}</td>
                    <td className="py-3 px-4 text-sm text-gray-400 text-right">
                      {(row.volume / 1000000).toFixed(2)}M
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
