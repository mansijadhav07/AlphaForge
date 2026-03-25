'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Loader2, AlertTriangle, Info, XCircle, AlertCircle } from 'lucide-react'

export default function ModelFailuresPage() {
  const [symbol, setSymbol] = useState('AAPL')
  const [failures, setFailures] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN']

  const loadFailures = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getPGMFailures(symbol)
      setFailures(data)
    } catch (err) {
      setError('Failed to load failure data')
      console.error('Error loading failures:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFailures()
  }, [symbol])

  const getSeverityColor = (severity: string) => {
    if (severity === 'high') return 'text-red-500'
    if (severity === 'medium') return 'text-yellow-500'
    return 'text-gray-400'
  }

  const getSeverityIcon = (severity: string) => {
    if (severity === 'high') return <XCircle className="h-5 w-5" />
    if (severity === 'medium') return <AlertCircle className="h-5 w-5" />
    return <Info className="h-5 w-5" />
  }

  return (
    <div className="min-h-screen pt-16 pb-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="absolute inset-0 bg-red-500 blur-lg opacity-50" />
                <div className="relative bg-gradient-to-br from-red-500 to-orange-500 p-3 rounded-xl">
                  <AlertTriangle className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold gradient-text">Model Failures</h1>
                <p className="text-muted-foreground">When and why predictions fail</p>
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

          <div className="glass border border-red-500/20 rounded-xl p-4">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-red-400 mb-1">About Failure Analysis</h3>
                <p className="text-sm text-muted-foreground">
                  Identifies incorrect predictions and explains why failures occurred.
                </p>
              </div>
            </div>
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="h-12 w-12 animate-spin text-neon-blue mx-auto mb-4" />
              <p className="text-muted-foreground">Analyzing failures...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-muted-foreground mb-4">{error}</p>
              <button onClick={loadFailures} className="px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 text-neon-blue rounded-lg transition-colors">
                Retry
              </button>
            </div>
          </div>
        )}

        {failures && !loading && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="glass border border-white/10 rounded-xl p-4">
                <div className="text-sm text-muted-foreground mb-1">Total Failures</div>
                <div className="text-2xl font-bold text-red-400">{failures.summary.total_failures}</div>
              </div>

              <div className="glass border border-white/10 rounded-xl p-4">
                <div className="text-sm text-muted-foreground mb-1">High Severity</div>
                <div className="text-2xl font-bold text-red-500">{failures.summary.high_severity_count}</div>
              </div>

              <div className="glass border border-white/10 rounded-xl p-4">
                <div className="text-sm text-muted-foreground mb-1">Failure Rate</div>
                <div className="text-2xl font-bold text-yellow-400">
                  {(failures.summary.failure_rate * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {failures.insights.length > 0 && (
              <div className="glass border border-white/10 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold gradient-text mb-4">Insights</h3>
                <div className="space-y-3">
                  {failures.insights.map((insight: string, index: number) => (
                    <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-white/5">
                      <AlertTriangle className="h-5 w-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-foreground">{insight}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="glass border border-white/10 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-white/10">
                <h3 className="text-lg font-semibold gradient-text">Failure Cases</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Predicted</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Actual</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Severity</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Reason</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {failures.failure_cases.map((failure: any, index: number) => (
                      <tr key={index} className="hover:bg-white/5 transition-colors">
                        <td className="px-4 py-4 text-sm">{failure.date || 'N/A'}</td>
                        <td className="px-4 py-4">
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-neon-blue/20 text-neon-blue capitalize">
                            {failure.predicted}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-neon-teal/20 text-neon-teal capitalize">
                            {failure.actual}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <div className={`flex items-center space-x-2 ${getSeverityColor(failure.severity)}`}>
                            {getSeverityIcon(failure.severity)}
                            <span className="text-sm capitalize">{failure.severity}</span>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-sm text-muted-foreground max-w-md">{failure.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
