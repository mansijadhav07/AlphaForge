'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SkeletonCard } from '@/components/ui/skeleton-loader';
import { AlertCircle, Trophy, TrendingUp, Zap, Target, Award } from 'lucide-react';

interface ModelMetrics {
  model_name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  log_loss: number | null;
  confusion_matrix: number[][];
  training_time: number;
  prediction_time: number;
}

interface BaselineComparison {
  symbol: string;
  timestamp: string;
  models: Record<string, ModelMetrics>;
  summary: Array<{
    Model: string;
    Accuracy: number;
    Precision: number;
    Recall: number;
    'F1 Score': number;
    'Log Loss': number | null;
    'Training Time (s)': number;
    'Prediction Time (s)': number;
  }>;
  best_model: {
    name: string;
    accuracy: number;
    f1_score: number;
  };
  winner: string;
  improvement_over_random: number;
  improvement_over_majority: number;
}

export default function BaselineComparisonPage() {
  const [data, setData] = useState<BaselineComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [selectedModel, setSelectedModel] = useState<string | null>(null);

  const symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT'];

  useEffect(() => {
    fetchComparison();
  }, [selectedSymbol]);

  const fetchComparison = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/pgm/baseline-comparison/${selectedSymbol}`);
      if (!response.ok) throw new Error('Failed to fetch baseline comparison');
      const result = await response.json();
      setData(result);
      setSelectedModel(result.winner);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getModelColor = (modelName: string) => {
    if (modelName.includes('PGM') || modelName.includes('Bayesian')) {
      return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
    } else if (modelName.includes('Logistic')) {
      return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    } else if (modelName.includes('Majority')) {
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    } else {
      return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getModelIcon = (modelName: string) => {
    if (modelName.includes('PGM')) return Trophy;
    if (modelName.includes('Logistic')) return Target;
    if (modelName.includes('Majority')) return TrendingUp;
    return Zap;
  };

  const formatMetric = (value: number | null) => {
    if (value === null) return 'N/A';
    return value.toFixed(4);
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
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
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          Baseline Model Comparison
        </h1>
        <p className="text-gray-400">
          Compare PGM performance against simple baseline models
        </p>
      </div>

      {/* Symbol Selector */}
      <Card className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Select Symbol</h2>
        <div className="flex gap-3">
          {symbols.map((symbol) => (
            <button
              key={symbol}
              onClick={() => setSelectedSymbol(symbol)}
              className={`px-6 py-3 rounded-lg border transition-all ${
                selectedSymbol === symbol
                  ? 'border-purple-500 bg-purple-500/10'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              <p className="font-semibold">{symbol}</p>
            </button>
          ))}
        </div>
      </Card>

      {/* Winner Card */}
      <Card className="glass-card p-6 border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-blue-500/10">
        <div className="flex items-center gap-4">
          <div className="p-4 bg-purple-500/20 rounded-full">
            <Trophy className="w-8 h-8 text-purple-400" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-400 mb-1">Best Performing Model</p>
            <h2 className="text-2xl font-bold text-purple-400">{data.winner}</h2>
            <p className="text-sm text-gray-300 mt-2">
              Accuracy: {formatPercent(data.best_model.accuracy)} | 
              F1 Score: {formatPercent(data.best_model.f1_score)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400">Improvement</p>
            <p className="text-xl font-bold text-green-400">
              +{formatPercent(data.improvement_over_random)}
            </p>
            <p className="text-xs text-gray-500">over random</p>
          </div>
        </div>
      </Card>

      {/* Performance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="glass-card p-6">
          <div className="flex items-center gap-3 mb-2">
            <Award className="w-5 h-5 text-purple-400" />
            <p className="text-sm text-gray-400">vs Random Baseline</p>
          </div>
          <p className="text-3xl font-bold text-green-400">
            +{formatPercent(data.improvement_over_random)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Random: {formatPercent(data.models['Random'].accuracy)}
          </p>
        </Card>

        <Card className="glass-card p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-yellow-400" />
            <p className="text-sm text-gray-400">vs Majority Baseline</p>
          </div>
          <p className="text-3xl font-bold text-green-400">
            +{formatPercent(data.improvement_over_majority)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Majority: {formatPercent(data.models['Majority Class'].accuracy)}
          </p>
        </Card>

        <Card className="glass-card p-6">
          <div className="flex items-center gap-3 mb-2">
            <Target className="w-5 h-5 text-blue-400" />
            <p className="text-sm text-gray-400">vs Logistic Regression</p>
          </div>
          <p className="text-3xl font-bold text-green-400">
            +{formatPercent(data.best_model.accuracy - data.models['Logistic Regression'].accuracy)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            LR: {formatPercent(data.models['Logistic Regression'].accuracy)}
          </p>
        </Card>
      </div>

      {/* Model Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(data.models).map(([name, metrics]) => {
          const Icon = getModelIcon(name);
          const isWinner = name === data.winner;
          
          return (
            <Card
              key={name}
              className={`glass-card p-6 cursor-pointer transition-all ${
                selectedModel === name ? 'border-purple-500 bg-purple-500/5' : ''
              } ${isWinner ? 'border-purple-500/50' : ''}`}
              onClick={() => setSelectedModel(name)}
            >
              {isWinner && (
                <div className="flex items-center gap-2 mb-3">
                  <Trophy className="w-4 h-4 text-purple-400" />
                  <Badge className="bg-purple-500/20 text-purple-400 text-xs">Winner</Badge>
                </div>
              )}
              
              <div className="flex items-center gap-3 mb-4">
                <Icon className="w-6 h-6 text-purple-400" />
                <Badge className={getModelColor(name)}>
                  {name}
                </Badge>
              </div>

              <div className="space-y-2">
                <div>
                  <p className="text-xs text-gray-400">Accuracy</p>
                  <p className="text-2xl font-bold">{formatPercent(metrics.accuracy)}</p>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <p className="text-gray-400">Precision</p>
                    <p className="font-semibold">{formatPercent(metrics.precision)}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Recall</p>
                    <p className="font-semibold">{formatPercent(metrics.recall)}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">F1 Score</p>
                    <p className="font-semibold">{formatPercent(metrics.f1_score)}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Log Loss</p>
                    <p className="font-semibold">{formatMetric(metrics.log_loss)}</p>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Detailed Comparison Table */}
      <Card className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Detailed Metrics</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="p-3 text-left">Model</th>
                <th className="p-3 text-right">Accuracy</th>
                <th className="p-3 text-right">Precision</th>
                <th className="p-3 text-right">Recall</th>
                <th className="p-3 text-right">F1 Score</th>
                <th className="p-3 text-right">Log Loss</th>
                <th className="p-3 text-right">Train Time</th>
                <th className="p-3 text-right">Predict Time</th>
              </tr>
            </thead>
            <tbody>
              {data.summary.map((row, idx) => (
                <tr
                  key={idx}
                  className={`border-b border-gray-800 ${
                    row.Model === data.winner ? 'bg-purple-500/5' : ''
                  }`}
                >
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <Badge className={getModelColor(row.Model)}>
                        {row.Model}
                      </Badge>
                      {row.Model === data.winner && (
                        <Trophy className="w-4 h-4 text-purple-400" />
                      )}
                    </div>
                  </td>
                  <td className="p-3 text-right font-semibold">{formatPercent(row.Accuracy)}</td>
                  <td className="p-3 text-right">{formatPercent(row.Precision)}</td>
                  <td className="p-3 text-right">{formatPercent(row.Recall)}</td>
                  <td className="p-3 text-right">{formatPercent(row['F1 Score'])}</td>
                  <td className="p-3 text-right">{formatMetric(row['Log Loss'])}</td>
                  <td className="p-3 text-right text-xs">{row['Training Time (s)'].toFixed(3)}s</td>
                  <td className="p-3 text-right text-xs">{row['Prediction Time (s)'].toFixed(3)}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Selected Model Details */}
      {selectedModel && data.models[selectedModel] && (
        <Card className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4">
            Confusion Matrix - {selectedModel}
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="p-3"></th>
                  <th className="p-3 text-center" colSpan={3}>Predicted</th>
                </tr>
                <tr className="border-b border-gray-700">
                  <th className="p-3 text-left">Actual</th>
                  <th className="p-3 text-center">Negative</th>
                  <th className="p-3 text-center">Neutral</th>
                  <th className="p-3 text-center">Positive</th>
                </tr>
              </thead>
              <tbody>
                {data.models[selectedModel].confusion_matrix.map((row, i) => (
                  <tr key={i} className="border-b border-gray-800">
                    <td className="p-3 font-semibold">
                      {['Negative', 'Neutral', 'Positive'][i]}
                    </td>
                    {row.map((value, j) => (
                      <td
                        key={j}
                        className={`p-3 text-center ${
                          i === j ? 'bg-green-500/20 font-bold' : 'bg-red-500/10'
                        }`}
                      >
                        {value}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-gray-400 mt-4">
            Diagonal values (green) are correct predictions. Off-diagonal values (red) are errors.
          </p>
        </Card>
      )}

      {/* Interpretation Guide */}
      <Card className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Interpretation Guide</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-purple-400 mb-2">Model Descriptions</h3>
            <div className="space-y-2 text-sm">
              <div>
                <p className="font-medium">Random Baseline</p>
                <p className="text-gray-400">Predicts classes randomly. Absolute minimum performance.</p>
              </div>
              <div>
                <p className="font-medium">Majority Class</p>
                <p className="text-gray-400">Always predicts most common class. Simple but often effective.</p>
              </div>
              <div>
                <p className="font-medium">Logistic Regression</p>
                <p className="text-gray-400">Linear classifier. Standard ML baseline.</p>
              </div>
              <div>
                <p className="font-medium">PGM (Bayesian Network)</p>
                <p className="text-gray-400">Probabilistic model with feature dependencies. Most sophisticated.</p>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-blue-400 mb-2">Performance Ranges</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>&lt; 40%</span>
                <span className="text-red-400">Worse than random</span>
              </div>
              <div className="flex justify-between">
                <span>40-55%</span>
                <span className="text-orange-400">Weak signal</span>
              </div>
              <div className="flex justify-between">
                <span>55-70%</span>
                <span className="text-yellow-400">Moderate</span>
              </div>
              <div className="flex justify-between">
                <span>70-85%</span>
                <span className="text-green-400">Good</span>
              </div>
              <div className="flex justify-between">
                <span>&gt; 85%</span>
                <span className="text-purple-400">Excellent</span>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
