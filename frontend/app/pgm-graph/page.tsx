'use client'

import { useEffect, useState } from 'react'
import { NetworkGraph } from '@/components/pgm/network-graph'
import { api } from '@/lib/api'
import { Loader2, Network, Info } from 'lucide-react'

export default function PGMGraphPage() {
  const [graphData, setGraphData] = useState<{
    nodes: Array<{ id: string; label: string }>
    edges: Array<{ from: string; to: string; from_label: string; to_label: string }>
    num_nodes: number
    num_edges: number
    is_dag: boolean
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadGraphData()
  }, [])

  const loadGraphData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getPGMGraph()
      setGraphData(data)
    } catch (err) {
      setError('Failed to load graph structure')
      console.error('Error loading graph:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen pt-16 pb-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <div className="relative">
              <div className="absolute inset-0 bg-neon-blue blur-lg opacity-50" />
              <div className="relative bg-gradient-to-br from-neon-blue to-neon-teal p-3 rounded-xl">
                <Network className="h-6 w-6 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold gradient-text">Bayesian Network</h1>
              <p className="text-muted-foreground">
                Probabilistic Graphical Model Structure
              </p>
            </div>
          </div>

          {/* Info Banner */}
          <div className="glass border border-neon-blue/20 rounded-xl p-4 mt-4">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-neon-blue mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-neon-blue mb-1">
                  About This Graph
                </h3>
                <p className="text-sm text-muted-foreground">
                  This Bayesian Network models the probabilistic dependencies between financial features.
                  Arrows show causal relationships, where parent nodes influence child nodes. Click on any
                  node to see its dependencies and influences.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Graph Stats */}
        {graphData && !loading && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="glass border border-white/10 rounded-xl p-4">
              <div className="text-sm text-muted-foreground mb-1">Total Nodes</div>
              <div className="text-2xl font-bold gradient-text">{graphData.num_nodes}</div>
            </div>
            <div className="glass border border-white/10 rounded-xl p-4">
              <div className="text-sm text-muted-foreground mb-1">Total Edges</div>
              <div className="text-2xl font-bold gradient-text">{graphData.num_edges}</div>
            </div>
            <div className="glass border border-white/10 rounded-xl p-4">
              <div className="text-sm text-muted-foreground mb-1">Graph Type</div>
              <div className="text-2xl font-bold gradient-text">
                {graphData.is_dag ? 'DAG' : 'Cyclic'}
              </div>
            </div>
            <div className="glass border border-white/10 rounded-xl p-4">
              <div className="text-sm text-muted-foreground mb-1">Avg Connections</div>
              <div className="text-2xl font-bold gradient-text">
                {(graphData.num_edges / graphData.num_nodes).toFixed(1)}
              </div>
            </div>
          </div>
        )}

        {/* Graph Visualization */}
        <div className="glass border border-white/10 rounded-xl overflow-hidden" style={{ height: '700px' }}>
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin text-neon-blue mx-auto mb-4" />
                <p className="text-muted-foreground">Loading graph structure...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-red-500 mb-2">⚠️</div>
                <p className="text-muted-foreground">{error}</p>
                <button
                  onClick={loadGraphData}
                  className="mt-4 px-4 py-2 bg-neon-blue/20 hover:bg-neon-blue/30 text-neon-blue rounded-lg transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {graphData && !loading && !error && (
            <NetworkGraph nodes={graphData.nodes} edges={graphData.edges} />
          )}
        </div>

        {/* Feature Descriptions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="glass border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-neon-blue mb-2">Input Features</h3>
            <p className="text-xs text-muted-foreground">
              Raw market indicators like RSI, MACD, volatility, and volume that serve as
              the foundation for predictions.
            </p>
          </div>
          <div className="glass border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-purple-400 mb-2">Derived Features</h3>
            <p className="text-xs text-muted-foreground">
              Intermediate variables like market regime and risk that are computed from
              input features and influence the final prediction.
            </p>
          </div>
          <div className="glass border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-neon-teal mb-2">Target Variable</h3>
            <p className="text-xs text-muted-foreground">
              Future return prediction - the main output of the model that combines
              information from all features.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
