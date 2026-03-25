'use client'

import { useCallback, useEffect, useState } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position,
} from 'reactflow'
import 'reactflow/dist/style.css'

interface NetworkGraphProps {
  nodes: Array<{ id: string; label: string }>
  edges: Array<{ from: string; to: string; from_label: string; to_label: string }>
}

const nodeDescriptions: Record<string, string> = {
  rsi_state: 'Relative Strength Index - Momentum oscillator measuring overbought/oversold conditions',
  momentum_score_state: 'Rate of price change - Indicates strength and direction of price movement',
  volatility_10_state: 'Price volatility over 10 periods - Measures market uncertainty',
  trend_slope_30_state: '30-period trend direction - Identifies long-term price trajectory',
  regime_state: 'Market regime classification - Bull, Bear, or Sideways market conditions',
  macd_diff_state: 'MACD histogram - Difference between MACD line and signal line',
  bb_position_state: 'Bollinger Band position - Price location relative to bands',
  volume_to_sma_state: 'Volume ratio - Current volume compared to moving average',
  atr_pct_state: 'Average True Range percentage - Normalized volatility measure',
  risk_state: 'Risk assessment - Overall market risk level',
  future_return_state: 'Predicted future return - Target variable for predictions',
}

const getNodeCategory = (nodeId: string): 'target' | 'derived' | 'feature' => {
  if (nodeId === 'future_return_state') return 'target'
  if (nodeId === 'risk_state' || nodeId === 'regime_state') return 'derived'
  return 'feature'
}

export function NetworkGraph({ nodes, edges }: NetworkGraphProps) {
  const [reactFlowNodes, setReactFlowNodes, onNodesChange] = useNodesState([])
  const [reactFlowEdges, setReactFlowEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  useEffect(() => {
    // Calculate layout positions
    const nodePositions = calculateLayout(nodes, edges)

    // Create React Flow nodes
    const flowNodes: Node[] = nodes.map((node) => {
      const category = getNodeCategory(node.id)
      
      return {
        id: node.id,
        type: 'default',
        data: { 
          label: node.label,
          description: nodeDescriptions[node.id] || 'No description available',
        },
        position: nodePositions[node.id] || { x: 0, y: 0 },
        style: {
          background: category === 'target' 
            ? 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)'
            : category === 'derived'
            ? 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)'
            : 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
          color: '#fff',
          border: '2px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '12px',
          padding: '12px 20px',
          fontSize: '13px',
          fontWeight: '600',
          boxShadow: category === 'target'
            ? '0 0 30px rgba(6, 182, 212, 0.5)'
            : category === 'derived'
            ? '0 0 20px rgba(139, 92, 246, 0.4)'
            : '0 0 15px rgba(16, 185, 129, 0.3)',
          width: 'auto',
          minWidth: '120px',
        },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      }
    })

    // Create React Flow edges
    const flowEdges: Edge[] = edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.from,
      target: edge.to,
      type: 'smoothstep',
      animated: true,
      style: {
        stroke: 'rgba(6, 182, 212, 0.6)',
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: 'rgba(6, 182, 212, 0.8)',
        width: 20,
        height: 20,
      },
    }))

    setReactFlowNodes(flowNodes)
    setReactFlowEdges(flowEdges)
  }, [nodes, edges, setReactFlowNodes, setReactFlowEdges])

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.id)
  }, [])

  const onPaneClick = useCallback(() => {
    setSelectedNode(null)
  }, [])

  return (
    <div className="relative w-full h-full">
      <ReactFlow
        nodes={reactFlowNodes}
        edges={reactFlowEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        fitView
        attributionPosition="bottom-left"
        className="bg-transparent"
      >
        <Background color="rgba(255, 255, 255, 0.05)" gap={16} />
        <Controls className="glass border border-white/10 rounded-lg" />
      </ReactFlow>

      {/* Node Info Panel */}
      {selectedNode && (
        <div className="absolute top-4 right-4 w-80 glass border border-white/10 rounded-xl p-4 shadow-xl">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold gradient-text">
              {nodes.find(n => n.id === selectedNode)?.label}
            </h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              ✕
            </button>
          </div>
          
          <p className="text-sm text-muted-foreground mb-4">
            {nodeDescriptions[selectedNode]}
          </p>

          <div className="space-y-2">
            <div>
              <h4 className="text-xs font-semibold text-neon-blue mb-1">Dependencies</h4>
              <div className="flex flex-wrap gap-1">
                {edges
                  .filter(e => e.to === selectedNode)
                  .map((e, i) => (
                    <span
                      key={i}
                      className="text-xs px-2 py-1 rounded-full bg-white/5 border border-white/10"
                    >
                      {e.from_label}
                    </span>
                  ))}
                {edges.filter(e => e.to === selectedNode).length === 0 && (
                  <span className="text-xs text-muted-foreground">No dependencies</span>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-semibold text-neon-teal mb-1">Influences</h4>
              <div className="flex flex-wrap gap-1">
                {edges
                  .filter(e => e.from === selectedNode)
                  .map((e, i) => (
                    <span
                      key={i}
                      className="text-xs px-2 py-1 rounded-full bg-white/5 border border-white/10"
                    >
                      {e.to_label}
                    </span>
                  ))}
                {edges.filter(e => e.from === selectedNode).length === 0 && (
                  <span className="text-xs text-muted-foreground">No influences</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 glass border border-white/10 rounded-xl p-4 shadow-xl">
        <h4 className="text-sm font-semibold mb-3">Node Types</h4>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded bg-gradient-to-r from-neon-blue to-blue-500 shadow-glow-blue" />
            <span className="text-xs text-muted-foreground">Target (Prediction)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded bg-gradient-to-r from-purple-500 to-pink-500" />
            <span className="text-xs text-muted-foreground">Derived (Intermediate)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded bg-gradient-to-r from-green-500 to-neon-blue" />
            <span className="text-xs text-muted-foreground">Feature (Input)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Simple hierarchical layout algorithm
function calculateLayout(
  nodes: Array<{ id: string; label: string }>,
  edges: Array<{ from: string; to: string }>
): Record<string, { x: number; y: number }> {
  const positions: Record<string, { x: number; y: number }> = {}
  
  // Build adjacency list
  const adjacency: Record<string, string[]> = {}
  const inDegree: Record<string, number> = {}
  
  nodes.forEach(node => {
    adjacency[node.id] = []
    inDegree[node.id] = 0
  })
  
  edges.forEach(edge => {
    adjacency[edge.from].push(edge.to)
    inDegree[edge.to] = (inDegree[edge.to] || 0) + 1
  })
  
  // Topological sort to determine layers
  const layers: string[][] = []
  const queue: string[] = []
  const visited = new Set<string>()
  
  // Start with nodes that have no dependencies
  nodes.forEach(node => {
    if (inDegree[node.id] === 0) {
      queue.push(node.id)
    }
  })
  
  while (queue.length > 0) {
    const currentLayer: string[] = []
    const layerSize = queue.length
    
    for (let i = 0; i < layerSize; i++) {
      const nodeId = queue.shift()!
      currentLayer.push(nodeId)
      visited.add(nodeId)
      
      adjacency[nodeId].forEach(neighbor => {
        inDegree[neighbor]--
        if (inDegree[neighbor] === 0 && !visited.has(neighbor)) {
          queue.push(neighbor)
        }
      })
    }
    
    if (currentLayer.length > 0) {
      layers.push(currentLayer)
    }
  }
  
  // Position nodes
  const horizontalSpacing = 250
  const verticalSpacing = 120
  
  layers.forEach((layer, layerIndex) => {
    const layerHeight = (layer.length - 1) * verticalSpacing
    const startY = -layerHeight / 2
    
    layer.forEach((nodeId, nodeIndex) => {
      positions[nodeId] = {
        x: layerIndex * horizontalSpacing,
        y: startY + nodeIndex * verticalSpacing,
      }
    })
  })
  
  return positions
}
