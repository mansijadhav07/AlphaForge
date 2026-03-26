'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SkeletonCard } from '@/components/ui/skeleton-loader';
import { AlertCircle, BarChart3, TrendingUp, Activity, Zap } from 'lucide-react';

interface BinInfo {
  bin: number;
  label: string;
  lower: number;
  upper: number;
  range: string;
}

interface Method {
  method: string;
  name: string;
  description: string;
  thresholds: number[];
  bins: BinInfo[];
  distribution: Record<string, number>;
  stats: Record<string, number>;
}

interface DiscretizationDemo {
  feature: string;
  unit: string;
  n_samples: number;
  data_stats: Record<string, number>;
  histogram: {
    counts: number[];
    edges: number[];
  };
  methods: Method[];
}

export default function DiscretizationPage() {
  const [data, setData] = useState<DiscretizationDemo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFeature, setSelectedFeature] = useState('volatility');
  const [selectedMethod, setSelectedMethod] = useState<Method | null>(null);

  const features = [
    { value: 'volatility', label: 'Volatility', icon: Activity },
    { value: 'rsi', label: 'RSI', icon: TrendingUp },
    { value: 'return', label: 'Return', icon: BarChart3 },
    { value: 'momentum', label: 'Momentum', icon: Zap },
  ];

  useEffect(() => {
    fetchDemo();
  }, [selectedFeature]);

  const fetchDemo = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/discretization/demo?feature=${selectedFeature}&n_samples=1000`);
      if (!response.ok) throw new Error('Failed to fetch discretization demo');
      const result = await response.json();
      setData(result);
      setSelectedMethod(result.methods[0]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'quantile': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'kmeans': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'equal_width': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'threshold': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
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
          Feature Discretization
        </h1>
        <p className="text-gray-400">
          Compare different discretization methods for converting continuous features to discrete states
        </p>
      </div>

      {/* Feature Selector */}
      <Card className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Select Feature</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <button
                key={feature.value}
                onClick={() => setSelectedFeature(feature.value)}
                className={`p-4 rounded-lg border transition-all ${
                  selectedFeature === feature.value
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-700 hover:border-gray-600'
                }`}
              >
                <Icon className="w-6 h-6 mb-2 mx-auto text-blue-400" />
                <p className="text-sm font-medium">{feature.label}</p>
              </button>
            );
          })}
        </div>
      </Card>

      {/* Data Statistics */}
      <Card className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Data Statistics ({data.n_samples} samples)</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {Object.entries(data.data_stats).map(([key, value]) => (
            <div key={key} className="text-center">
              <p className="text-xs text-gray-400 uppercase mb-1">{key}</p>
              <p className="text-lg font-semibold">{value.toFixed(4)}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Method Selector */}
      <Card className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Discretization Methods</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {data.methods.map((method) => (
            <button
              key={method.method}
              onClick={() => setSelectedMethod(method)}
              className={`p-4 rounded-lg border text-left transition-all ${
                selectedMethod?.method === method.method
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              <Badge className={`mb-2 ${getMethodColor(method.method)}`}>
                {method.method}
              </Badge>
              <p className="font-medium mb-1">{method.name}</p>
              <p className="text-xs text-gray-400">{method.description}</p>
            </button>
          ))}
        </div>
      </Card>

      {/* Selected Method Details */}
      {selectedMethod && (
        <>
          {/* Thresholds */}
          <Card className="glass-card p-6">
            <h2 className="text-lg font-semibold mb-4">
              Thresholds - {selectedMethod.name}
            </h2>
            <div className="flex items-center gap-2 flex-wrap">
              {selectedMethod.thresholds.map((threshold, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <Badge variant="outline" className="text-sm">
                    {threshold.toFixed(4)}
                  </Badge>
                  {idx < selectedMethod.thresholds.length - 1 && (
                    <span className="text-gray-500">→</span>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Bins */}
          <Card className="glass-card p-6">
            <h2 className="text-lg font-semibold mb-4">Bin Information</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="p-3 text-left">Bin</th>
                    <th className="p-3 text-left">Label</th>
                    <th className="p-3 text-right">Lower</th>
                    <th className="p-3 text-right">Upper</th>
                    <th className="p-3 text-left">Range</th>
                    <th className="p-3 text-right">Count</th>
                    <th className="p-3 text-right">%</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedMethod.bins.map((bin) => {
                    const count = selectedMethod.distribution[bin.label] || 0;
                    const percentage = (count / data.n_samples) * 100;
                    
                    return (
                      <tr key={bin.bin} className="border-b border-gray-800">
                        <td className="p-3">{bin.bin}</td>
                        <td className="p-3">
                          <Badge className={getMethodColor(selectedMethod.method)}>
                            {bin.label}
                          </Badge>
                        </td>
                        <td className="p-3 text-right font-mono">{bin.lower.toFixed(4)}</td>
                        <td className="p-3 text-right font-mono">{bin.upper.toFixed(4)}</td>
                        <td className="p-3 font-mono text-xs">{bin.range}</td>
                        <td className="p-3 text-right">{count}</td>
                        <td className="p-3 text-right">{percentage.toFixed(1)}%</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Distribution Visualization */}
          <Card className="glass-card p-6">
            <h2 className="text-lg font-semibold mb-4">Distribution</h2>
            <div className="space-y-3">
              {selectedMethod.bins.map((bin) => {
                const count = selectedMethod.distribution[bin.label] || 0;
                const percentage = (count / data.n_samples) * 100;
                
                return (
                  <div key={bin.bin}>
                    <div className="flex items-center justify-between mb-1">
                      <Badge className={getMethodColor(selectedMethod.method)}>
                        {bin.label}
                      </Badge>
                      <span className="text-sm text-gray-400">
                        {count} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </>
      )}

      {/* Method Comparison */}
      <Card className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Method Comparison</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="p-3 text-left">Method</th>
                <th className="p-3 text-left">Description</th>
                <th className="p-3 text-right">Bins</th>
                <th className="p-3 text-left">Best For</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="p-3">
                  <Badge className="bg-blue-500/20 text-blue-400">Quantile</Badge>
                </td>
                <td className="p-3 text-gray-300">Equal frequency bins</td>
                <td className="p-3 text-right">3</td>
                <td className="p-3 text-gray-400">Skewed distributions</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="p-3">
                  <Badge className="bg-purple-500/20 text-purple-400">K-means</Badge>
                </td>
                <td className="p-3 text-gray-300">Natural cluster detection</td>
                <td className="p-3 text-right">3</td>
                <td className="p-3 text-gray-400">Unknown distributions</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="p-3">
                  <Badge className="bg-green-500/20 text-green-400">Equal-width</Badge>
                </td>
                <td className="p-3 text-gray-300">Equal-sized intervals</td>
                <td className="p-3 text-right">3</td>
                <td className="p-3 text-gray-400">Uniform distributions</td>
              </tr>
              <tr>
                <td className="p-3">
                  <Badge className="bg-orange-500/20 text-orange-400">Threshold</Badge>
                </td>
                <td className="p-3 text-gray-300">Fixed or data-driven</td>
                <td className="p-3 text-right">3</td>
                <td className="p-3 text-gray-400">Domain knowledge</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
