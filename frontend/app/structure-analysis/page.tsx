'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SkeletonCard } from '@/components/ui/skeleton-loader';
import { AlertCircle, CheckCircle2, Network, GitBranch, TrendingUp } from 'lucide-react';

interface CorrelationMatrix {
  features: string[];
  matrix: number[][];
  method: string;
}

interface EdgeExplanation {
  parent: string;
  child: string;
  edge_type: string;
  strength: string;
  reasoning: string;
  financial_theory: string;
  empirical_support: string;
  causal_mechanism: string;
}

interface StructureAnalysis {
  timestamp: string;
  correlation_matrix: CorrelationMatrix;
  edge_explanations: EdgeExplanation[];
  structure_validation: {
    is_valid_dag: boolean;
    has_cycles: boolean;
    validation_summary: string;
  };
  network_summary: {
    total_nodes: number;
    total_edges: number;
    is_dag: boolean;
    description: string;
  };
}

export default function StructureAnalysisPage() {
  const [data, setData] = useState<StructureAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<EdgeExplanation | null>(null);

  useEffect(() => {
    fetchStructureAnalysis();
  }, []);

  const fetchStructureAnalysis = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/pgm/structure-analysis?symbol=AAPL');
      if (!response.ok) throw new Error('Failed to fetch structure analysis');
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getStrengthColor = (strength: string) => {
    switch (strength.toLowerCase()) {
      case 'strong': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'weak': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getCorrelationColor = (value: number) => {
    const abs = Math.abs(value);
    if (abs > 0.7) return 'bg-green-500';
    if (abs > 0.4) return 'bg-yellow-500';
    if (abs > 0.2) return 'bg-orange-500';
    return 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container mx-auto p-6">
        <Card className="p-6 border-red-500/30 bg-red-500/5">
          <div className="flex items-center gap-3 text-red-400">
            <AlertCircle className="w-5 h-5" />
            <p>Error: {error || 'No data available'}</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Bayesian Network Structure Analysis
        </h1>
        <p className="text-gray-400">
          Comprehensive analysis of the probabilistic graphical model structure
        </p>
      </div>

      {/* Network Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="glass-card p-6">
          <div className="flex items-center gap-3">
            <Network className="w-8 h-8 text-blue-400" />
            <div>
              <p className="text-sm text-gray-400">Total Nodes</p>
              <p className="text-2xl font-bold">{data.network_summary.total_nodes}</p>
            </div>
          </div>
        </Card>
        
        <Card className="glass-card p-6">
          <div className="flex items-center gap-3">
            <GitBranch className="w-8 h-8 text-purple-400" />
            <div>
              <p className="text-sm text-gray-400">Total Edges</p>
              <p className="text-2xl font-bold">{data.network_summary.total_edges}</p>
            </div>
          </div>
        </Card>
        
        <Card className="glass-card p-6">
          <div className="flex items-center gap-3">
            {data.structure_validation.is_valid_dag ? (
              <CheckCircle2 className="w-8 h-8 text-green-400" />
            ) : (
              <AlertCircle className="w-8 h-8 text-red-400" />
            )}
            <div>
              <p className="text-sm text-gray-400">DAG Status</p>
              <p className="text-2xl font-bold">
                {data.structure_validation.is_valid_dag ? 'Valid' : 'Invalid'}
              </p>
            </div>
          </div>
        </Card>
        
        <Card className="glass-card p-6">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-green-400" />
            <div>
              <p className="text-sm text-gray-400">Cycles</p>
              <p className="text-2xl font-bold">
                {data.structure_validation.has_cycles ? 'Yes' : 'None'}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Validation Summary */}
      <Card className="glass-card p-6">
        <h2 className="text-xl font-semibold mb-4">Structure Validation</h2>
        <p className="text-gray-300">{data.structure_validation.validation_summary}</p>
      </Card>

      {/* Correlation Heatmap */}
      <Card className="glass-card p-6">
        <h2 className="text-xl font-semibold mb-4">Correlation Matrix ({data.correlation_matrix.method})</h2>
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="p-2 text-left sticky left-0 bg-gray-900/90"></th>
                  {data.correlation_matrix.features.map((feature) => (
                    <th key={feature} className="p-2 text-center text-xs text-gray-400 min-w-[60px]">
                      {feature}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.correlation_matrix.features.map((rowFeature, i) => (
                  <tr key={rowFeature}>
                    <td className="p-2 text-xs text-gray-400 font-medium sticky left-0 bg-gray-900/90">
                      {rowFeature}
                    </td>
                    {data.correlation_matrix.matrix[i].map((value, j) => (
                      <td key={j} className="p-1">
                        <div
                          className={`w-full h-8 flex items-center justify-center rounded text-xs font-medium ${
                            i === j ? 'bg-blue-500/30 text-blue-300' : ''
                          }`}
                          style={{
                            backgroundColor: i !== j ? `rgba(${value > 0 ? '34, 197, 94' : '239, 68, 68'}, ${Math.abs(value) * 0.5})` : undefined
                          }}
                          title={`${rowFeature} vs ${data.correlation_matrix.features[j]}: ${value.toFixed(3)}`}
                        >
                          {value.toFixed(2)}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="mt-4 flex items-center gap-4 text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500/50 rounded"></div>
            <span>Positive Correlation</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500/50 rounded"></div>
            <span>Negative Correlation</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-blue-500/30 rounded"></div>
            <span>Self (1.0)</span>
          </div>
        </div>
      </Card>

      {/* Edge Explanations */}
      <Card className="glass-card p-6">
        <h2 className="text-xl font-semibold mb-4">Edge Explanations ({data.edge_explanations.length} edges)</h2>
        <div className="space-y-3">
          {data.edge_explanations.map((edge, idx) => (
            <div
              key={idx}
              className="border border-gray-700/50 rounded-lg p-4 hover:border-blue-500/50 transition-all cursor-pointer"
              onClick={() => setSelectedEdge(selectedEdge?.parent === edge.parent && selectedEdge?.child === edge.child ? null : edge)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm">
                    <span className="text-blue-400">{edge.parent}</span>
                    <span className="text-gray-500 mx-2">→</span>
                    <span className="text-purple-400">{edge.child}</span>
                  </span>
                  <Badge className={getStrengthColor(edge.strength)}>
                    {edge.strength}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {edge.edge_type}
                  </Badge>
                </div>
              </div>
              
              <p className="text-sm text-gray-300 mb-2">{edge.reasoning}</p>
              
              {selectedEdge?.parent === edge.parent && selectedEdge?.child === edge.child && (
                <div className="mt-4 space-y-3 pt-3 border-t border-gray-700/50">
                  <div>
                    <p className="text-xs font-semibold text-blue-400 mb-1">Financial Theory</p>
                    <p className="text-sm text-gray-300">{edge.financial_theory}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-green-400 mb-1">Empirical Support</p>
                    <p className="text-sm text-gray-300">{edge.empirical_support}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-purple-400 mb-1">Causal Mechanism</p>
                    <p className="text-sm text-gray-300">{edge.causal_mechanism}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
