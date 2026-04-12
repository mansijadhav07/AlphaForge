'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Database, 
  Sparkles, 
  TrendingUp, 
  Activity,
  ArrowRight,
  Zap,
  BarChart3,
  GitBranch
} from 'lucide-react'
import { api, type StockFeatures } from '@/lib/api'
import { FullScreenLoader } from '@/components/ui/fullscreen-loader'
import { PipelineFlow } from '@/components/feature-intelligence/pipeline-flow'
import { RawDataPreview } from '@/components/feature-intelligence/raw-data-preview'
import { FeaturePanel } from '@/components/feature-intelligence/feature-panel'
import { DiscretizationSection } from '@/components/feature-intelligence/discretization-section'
import { ModelConnection } from '@/components/feature-intelligence/model-connection'

const TICKERS = ['AAPL', 'TSLA', 'GOOGL', 'MSFT']

export default function FeatureIntelligencePage() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL')
  const [stockData, setStockData] = useState<StockFeatures[]>([])
  const [loading, setLoading] = useState(true)
  const [showDiscretized, setShowDiscretized] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      const data = await api.getFeatures(selectedTicker)
      setStockData(data)
      setLoading(false)
    }

    fetchData()
  }, [selectedTicker])

  if (loading) {
    return <FullScreenLoader message="Loading feature pipeline" />
  }

  const latestData = stockData[stockData.length - 1]

  return (
    <div className="page-container">
      {/* Header */}
      <motion.div 
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3 mb-3">
          <h1 className="page-title">Feature Intelligence</h1>
          <Sparkles className="w-7 h-7 text-cyan-400" />
        </div>
        <p className="page-description">
          From Raw Data to Model Input - Visualizing the Feature Engineering Pipeline
        </p>
      </motion.div>

      {/* Ticker Selector */}
      <motion.div
        className="flex gap-3 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {TICKERS.map((ticker) => (
          <button
            key={ticker}
            onClick={() => setSelectedTicker(ticker)}
            className={`px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
              selectedTicker === ticker
                ? 'bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-lg shadow-cyan-500/30'
                : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
            }`}
          >
            {ticker}
          </button>
        ))}
      </motion.div>

      {/* Pipeline Flow */}
      <PipelineFlow />

      {/* Raw Data Preview */}
      <RawDataPreview data={stockData.slice(-5)} />

      {/* Feature Engineering Panel */}
      <FeaturePanel 
        data={latestData} 
        showDiscretized={showDiscretized}
      />

      {/* Discretization Section */}
      <DiscretizationSection 
        data={latestData}
        showDiscretized={showDiscretized}
        onToggle={() => setShowDiscretized(!showDiscretized)}
      />

      {/* Model Connection */}
      <ModelConnection />
    </div>
  )
}
