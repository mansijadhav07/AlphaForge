'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SkeletonCard } from '@/components/ui/skeleton-loader';
import { AlertCircle, TrendingUp, Target, CheckCircle, XCircle } from 'lucide-react';
import { LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

interface CalibrationData {
  symbol: string;
  timestamp: string;
  calibration_curve: {
    bins: Array<{
      predicted_prob: number;
      actual_freq: number;
      count: number;
      confidence_lower: number;
      confidence_upper: number;
      gap?: number;
    }>;
    metrics: {
      ece: number;
      mce: number;
      brier_score: number;
      log_loss: number;
      reliability_score: number;
    };
  };
  reliability_diagram: {
    bins: Array<any>;
    perfect_line: Array<{ x: number; y: number }>;
    metrics: any;
    summary: {
      total_samples: number;
      n_bins: number;
      mean_predicted_prob: number;
      actual_positive_rate: number;
    };
  };
  interpretation: {
    ece: {
      quality: string;
      description: string;
      value: number;
    };
    brier: {
      quality: string;
      description: string;
      value: number;
    };
    overall: string;
  };
  summary: {
    total_samples: number;
    positive_rate: number;
    mean_predicted_prob: number;
  };
}

export default function CalibrationPage() {
  const [data, setData] = useState<CalibrationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');

  const symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT'];

  useEffect(() => {
    fetchCalibrationData();
  }, [selectedSymbol]);

  const fetchCalibrationData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/pgm/calibration/${selectedSymbol}`);
      if (!response.ok) throw new Error('Failed to fetch calibration data');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent': return 'bg-green-100 text-green-800 border-green-200';
      case 'good': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'fair': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'poor': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getQualityIcon = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
      case 'good':
        return <CheckCircle className="w-5 h-5" />;
      case 'fair':
        return <AlertCircle className="w-5 h-5" />;
      case 'poor':
        return <XCircle className="w-5 h-5" />;
      default:
        return <Target className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card className="p-6 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            <span className="font-semibold">Error loading calibration data</span>
          </div>
          <p className="mt-2 text-red-600">{error}</p>
        </Card>
      </div>
    );
  }

  if (!data) return null;

  // Prepare calibration curve data
  const calibrationData = data.calibration_curve.bins.map(bin => ({
    predicted: bin.predicted_prob,
    actual: bin.actual_freq,
    count: bin.count,
    lower: bin.confidence_lower,
    upper: bin.confidence_upper
  }));

  // Perfect calibration line
  const perfectLine = [
    { predicted: 0, actual: 0 },
    { predicted: 1, actual: 1 }
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Probability Calibration</h1>
          <p className="text-gray-600 mt-1">
            Analyze how well predicted probabilities match actual outcomes
          </p>
        </div>
        <select
          value={selectedSymbol}
          onChange={(e) => setSelectedSymbol(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {symbols.map(symbol => (
            <option key={symbol} value={symbol}>{symbol}</option>
          ))}
        </select>
      </div>

      {/* Overall Assessment */}
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-100 rounded-lg">
            <Target className="w-6 h-6 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Assessment</h3>
            <p className="text-gray-700 text-lg">{data.interpretation.overall}</p>
            <div className="mt-4 grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Samples</p>
                <p className="text-2xl font-bold text-gray-900">{data.summary.total_samples}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Positive Rate</p>
                <p className="text-2xl font-bold text-gray-900">{(data.summary.positive_rate * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Mean Predicted</p>
                <p className="text-2xl font-bold text-gray-900">{(data.summary.mean_predicted_prob * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Calibration Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* ECE Card */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Expected Calibration Error</h3>
              <p className="text-sm text-gray-600 mt-1">Lower is better (0 = perfect)</p>
            </div>
            <Badge className={getQualityColor(data.interpretation.ece.quality)}>
              <div className="flex items-center gap-1">
                {getQualityIcon(data.interpretation.ece.quality)}
                {data.interpretation.ece.quality}
              </div>
            </Badge>
          </div>
          <div className="space-y-3">
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-gray-900">
                {(data.calibration_curve.metrics.ece * 100).toFixed(2)}%
              </span>
              <span className="text-gray-600">ECE</span>
            </div>
            <p className="text-gray-700">{data.interpretation.ece.description}</p>
            <div className="pt-3 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Reliability Score</span>
                <span className="font-semibold text-gray-900">
                  {(data.calibration_curve.metrics.reliability_score * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </Card>

        {/* Brier Score Card */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Brier Score</h3>
              <p className="text-sm text-gray-600 mt-1">Measures prediction accuracy</p>
            </div>
            <Badge className={getQualityColor(data.interpretation.brier.quality)}>
              <div className="flex items-center gap-1">
                {getQualityIcon(data.interpretation.brier.quality)}
                {data.interpretation.brier.quality}
              </div>
            </Badge>
          </div>
          <div className="space-y-3">
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-gray-900">
                {data.calibration_curve.metrics.brier_score.toFixed(3)}
              </span>
              <span className="text-gray-600">Score</span>
            </div>
            <p className="text-gray-700">{data.interpretation.brier.description}</p>
            <div className="pt-3 border-t space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Log Loss</span>
                <span className="font-semibold text-gray-900">
                  {data.calibration_curve.metrics.log_loss.toFixed(3)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Max Calibration Error</span>
                <span className="font-semibold text-gray-900">
                  {(data.calibration_curve.metrics.mce * 100).toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Calibration Curve */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Calibration Curve</h3>
        <p className="text-sm text-gray-600 mb-6">
          Points closer to the diagonal line indicate better calibration
        </p>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="predicted"
              name="Predicted Probability"
              domain={[0, 1]}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              label={{ value: 'Predicted Probability', position: 'insideBottom', offset: -10 }}
            />
            <YAxis
              type="number"
              dataKey="actual"
              name="Actual Frequency"
              domain={[0, 1]}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              label={{ value: 'Actual Frequency', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              formatter={(value: any) => `${(value * 100).toFixed(1)}%`}
              labelFormatter={(label) => `Bin: ${label}`}
            />
            <Legend />
            
            {/* Perfect calibration line */}
            <Line
              data={perfectLine}
              type="monotone"
              dataKey="actual"
              stroke="#94a3b8"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Perfect Calibration"
            />
            
            {/* Actual calibration */}
            <Scatter
              data={calibrationData}
              fill="#3b82f6"
              name="Model Calibration"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </Card>

      {/* Reliability Diagram Details */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Calibration Bins</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Predicted Prob</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Actual Freq</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Gap</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Count</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Confidence Interval</th>
              </tr>
            </thead>
            <tbody>
              {data.calibration_curve.bins.map((bin, idx) => {
                const gap = Math.abs(bin.predicted_prob - bin.actual_freq);
                const gapColor = gap < 0.05 ? 'text-green-600' : gap < 0.10 ? 'text-yellow-600' : 'text-red-600';
                
                return (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm">{(bin.predicted_prob * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-sm">{(bin.actual_freq * 100).toFixed(1)}%</td>
                    <td className={`py-3 px-4 text-sm font-semibold ${gapColor}`}>
                      {(gap * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-sm">{bin.count}</td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      [{(bin.confidence_lower * 100).toFixed(1)}%, {(bin.confidence_upper * 100).toFixed(1)}%]
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Info Card */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Understanding Calibration</h3>
        <div className="space-y-2 text-sm text-gray-700">
          <p>
            <strong>Calibration</strong> measures how well predicted probabilities match actual outcomes.
            A well-calibrated model predicting 70% probability should be correct 70% of the time.
          </p>
          <p>
            <strong>Expected Calibration Error (ECE)</strong> is the average difference between predicted
            probabilities and actual frequencies across all bins. Lower is better.
          </p>
          <p>
            <strong>Brier Score</strong> measures the accuracy of probabilistic predictions.
            It ranges from 0 (perfect) to 1 (worst).
          </p>
        </div>
      </Card>
    </div>
  );
}
