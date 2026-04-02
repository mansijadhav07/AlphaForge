'use client'

import { useEffect, useState } from 'react'
import {
  TrendingUp,
  Activity,
  Target,
  BarChart3,
  DollarSign,
  TrendingDown,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select } from '@/components/ui/select'
import { MetricCard } from '@/components/ui/metric-card'
import { EquityCurveChart } from '@/components/charts/equity-curve-chart'
import { FullScreenLoader } from '@/components/ui/fullscreen-loader'
import { api, type BacktestResult } from '@/lib/api'
import { formatCurrency, formatPercentage } from '@/lib/utils'

const strategies = [
  { value: 'rsi', label: 'RSI Mean Reversion' },
  { value: 'macd', label: 'MACD Crossover' },
  { value: 'trend', label: 'Trend Following' },
  { value: 'bb', label: 'Bollinger Bands' },
]

const tickers = [
  { value: 'AAPL', label: 'Apple (AAPL)' },
  { value: 'TSLA', label: 'Tesla (TSLA)' },
  { value: 'GOOGL', label: 'Google (GOOGL)' },
  { value: 'MSFT', label: 'Microsoft (MSFT)' },
]

export default function BacktestingPage() {
  const [selectedStrategy, setSelectedStrategy] = useState('rsi')
  const [selectedTicker, setSelectedTicker] = useState('AAPL')
  const [results, setResults] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [compareMode, setCompareMode] = useState(false)
  const [compareResults, setCompareResults] = useState<BacktestResult[]>([])

  useEffect(() => {
    runBacktest()
  }, [selectedStrategy, selectedTicker])

  const runBacktest = async () => {
    setLoading(true)
    try {
      const data = await api.getBacktestResults(selectedStrategy, selectedTicker)
      console.log('Backtest data received:', data)
      setResults(data)
    } catch (error) {
      console.error('Error fetching backtest:', error)
    } finally {
      setLoading(false)
    }
  }

  const runComparison = async () => {
    setLoading(true)
    const allResults = await Promise.all(
      strategies.map((strategy) =>
        api.getBacktestResults(strategy.value, selectedTicker)
      )
    )
    setCompareResults(allResults)
    setCompareMode(true)
    setLoading(false)
  }

  if (loading && !results) {
    return <FullScreenLoader message="Running backtest simulation" />
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8 animate-slide-in">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold gradient-text">Backtesting</h1>
        <p className="text-muted-foreground">
          Evaluate trading strategies with historical data
        </p>
      </div>

      {/* Strategy Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-muted-foreground mb-2 block">
                Strategy
              </label>
              <Select
                value={selectedStrategy}
                onValueChange={setSelectedStrategy}
                options={strategies}
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground mb-2 block">
                Ticker
              </label>
              <Select
                value={selectedTicker}
                onValueChange={setSelectedTicker}
                options={tickers}
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={runComparison}
                className="w-full px-4 py-2 rounded-lg bg-neon-blue/20 text-neon-blue hover:bg-neon-blue/30 transition-all font-medium"
              >
                Compare All Strategies
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {!compareMode && results && (
        <>
          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Return"
              value={results.total_return * 100}
              format="percentage"
              icon={TrendingUp}
              colorize
              trend={results.total_return >= 0 ? 'up' : 'down'}
            />
            <MetricCard
              title="Sharpe Ratio"
              value={results.sharpe_ratio}
              subtitle="Risk-adjusted return"
              icon={Activity}
              colorize
              trend={results.sharpe_ratio >= 1 ? 'up' : results.sharpe_ratio >= 0 ? 'neutral' : 'down'}
            />
            <MetricCard
              title="Max Drawdown"
              value={results.max_drawdown * 100}
              format="percentage"
              icon={TrendingDown}
              colorize
              trend="down"
            />
            <MetricCard
              title="Win Rate"
              value={results.win_rate * 100}
              format="percentage"
              icon={Target}
              subtitle={`${results.num_trades} trades`}
            />
          </div>

          {/* Additional Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="card-glow">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <div className="p-3 rounded-lg bg-neon-blue/10">
                    <DollarSign className="h-6 w-6 text-neon-blue" />
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Initial Capital</div>
                    <div className="text-xl font-bold">
                      {formatCurrency(results.initial_capital)}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-glow">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <div className="p-3 rounded-lg bg-bullish/10">
                    <DollarSign className="h-6 w-6 text-bullish" />
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Final Value</div>
                    <div className="text-xl font-bold text-bullish">
                      {formatCurrency(results.final_value)}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-glow">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <div className="p-3 rounded-lg bg-neon-teal/10">
                    <BarChart3 className="h-6 w-6 text-neon-teal" />
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Number of Trades</div>
                    <div className="text-xl font-bold">{results.num_trades}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Equity Curve */}
          <Card>
            <CardHeader>
              <CardTitle>Equity Curve</CardTitle>
            </CardHeader>
            <CardContent>
              {results.equity_curve && results.equity_curve.length > 0 ? (
                <>
                  <div className="text-xs text-gray-500 mb-2">
                    Data points: {results.equity_curve.length} | 
                    Range: ${Math.min(...results.equity_curve.map(p => p.value)).toFixed(2)} - 
                    ${Math.max(...results.equity_curve.map(p => p.value)).toFixed(2)}
                  </div>
                  <EquityCurveChart
                    data={results.equity_curve}
                    initialCapital={results.initial_capital}
                    showBuyHold={true}
                  />
                </>
              ) : (
                <div className="text-gray-400 text-center py-8">
                  No equity curve data available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Strategy Info */}
          <Card>
            <CardHeader>
              <CardTitle>Strategy Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg glass">
                  <span className="text-sm text-muted-foreground">Strategy Name</span>
                  <Badge variant="default">{results.strategy}</Badge>
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg glass">
                  <span className="text-sm text-muted-foreground">Ticker</span>
                  <span className="font-semibold">{results.ticker}</span>
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg glass">
                  <span className="text-sm text-muted-foreground">Performance vs Buy & Hold</span>
                  <span className={`font-semibold ${
                    results.total_return >= 0 ? 'text-bullish' : 'text-bearish'
                  }`}>
                    {results.total_return >= 0 ? 'Outperformed' : 'Underperformed'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Comparison Mode */}
      {compareMode && compareResults.length > 0 && (
        <>
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Strategy Comparison</h2>
            <button
              onClick={() => setCompareMode(false)}
              className="px-4 py-2 rounded-lg glass-hover text-sm"
            >
              Back to Single View
            </button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Performance Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                        Strategy
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Total Return
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Sharpe Ratio
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Max Drawdown
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Win Rate
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                        Trades
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {compareResults.map((result, index) => (
                      <tr
                        key={index}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        <td className="py-3 px-4">
                          <Badge variant="default">{result.strategy}</Badge>
                        </td>
                        <td className={`text-right py-3 px-4 font-semibold ${
                          result.total_return >= 0 ? 'text-bullish' : 'text-bearish'
                        }`}>
                          {formatPercentage(result.total_return)}
                        </td>
                        <td className="text-right py-3 px-4 font-semibold">
                          {result.sharpe_ratio.toFixed(2)}
                        </td>
                        <td className="text-right py-3 px-4 font-semibold text-bearish">
                          {formatPercentage(result.max_drawdown)}
                        </td>
                        <td className="text-right py-3 px-4 font-semibold">
                          {formatPercentage(result.win_rate)}
                        </td>
                        <td className="text-right py-3 px-4">
                          {result.num_trades}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Best Strategy Highlight */}
          <Card className="border-neon-blue/50 card-glow">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-neon-blue" />
                <span>Best Performing Strategy</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {(() => {
                const bestStrategy = compareResults.reduce((best, current) =>
                  current.total_return > best.total_return ? current : best
                )
                return (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Strategy</div>
                      <div className="text-lg font-bold gradient-text">
                        {bestStrategy.strategy}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Total Return</div>
                      <div className="text-lg font-bold text-bullish">
                        {formatPercentage(bestStrategy.total_return)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Sharpe Ratio</div>
                      <div className="text-lg font-bold">
                        {bestStrategy.sharpe_ratio.toFixed(2)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Win Rate</div>
                      <div className="text-lg font-bold">
                        {formatPercentage(bestStrategy.win_rate)}
                      </div>
                    </div>
                  </div>
                )
              })()}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
