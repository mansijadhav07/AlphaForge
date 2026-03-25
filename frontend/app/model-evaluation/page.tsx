'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Loader2, CheckCircle2, AlertCircle, Info, BarChart3 } from 'lucide-react'

export default function ModelEvaluationPage() {
  const [symbol, setSymbol] = useState('AAPL')
  const [evaluation, setEvaluation] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN']

  const loadEvaluation = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getPGMEvaluation(symbol)
      setEvaluation(data)
    } catch (err) {
      setError('Failed to load evaluation data')
      console.error('Error loading evaluation:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadEvaluation()
  }, [symbol])

  return (
    <div className="min-h-screen pt-16 pb-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="absolute inset-0 bg-neon-blue blur-lg opacity-50" />
                <div className="relative bg-gradient-to-br from-neon-blue to-neon-teal p-3 rounded-xl">
                  <BarChart3 className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold gradient-text">Model Evaluation Dashboard</h1>
                <p className="text-muted-foreground">Comprehensive performance metrics</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">Symbol:</span>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="glass border border-white/10 rounded-lg px-4 py-2 text-sm font-medium bg-transparent focus:outline-none focus:ring-2 focus:ring-neon-blue"
              >
                {symbols.map((sym) => (
                  <option key={sym} value={sym} className="bg-gray-900">{sym}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="glass border border-neon-blue/20 rounded-xl p-4">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-neon-blue mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-neon-blue mb-1">About Model Evaluation</h3>
                <p className="text-sm text-muted-foreground">
                  This dashboard evaluates the probabilistic model performance using historical data.
                </p>
              </div>
            </div>
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="h-12 w-12 animate-spin text-neon-blue mx-auto mb-4" />
              <p className="text-muted-foreground">Loading evaluation data...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-muted-foreground mb-4">{error}</p>
              <button onClick={loadEvaluation} className="px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 text-neon-blue rounded-lg transition-colors">
                Retry
              </button>
            </div>
          </div>
        )}

        {evaluation && !loading && (
          <div className="glass border border-white/10 rounded-xl p-6">
            <h3 className="text-lg font-semibold gradient-text mb-4">Evaluation Results</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">Accuracy</div>
                <div className="text-2xl font-bold text-neon-blue">{(evaluation.accuracy * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Brier Score</div>
                <div className="text-2xl font-bold text-neon-teal">{evaluation.brier_score.overall.toFixed(3)}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">F1-Score</div>
                <div className="text-2xl font-bold text-purple-400">{(evaluation.classification_report.macro_avg.f1_score * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Samples</div>
                <div className="text-2xl font-bold text-foreground">{evaluation.n_samples}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
