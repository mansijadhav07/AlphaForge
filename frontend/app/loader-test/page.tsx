'use client'

import { useState } from 'react'
import { PremiumChartLoader } from '@/components/ui/premium-chart-loader'
import { GhostChartLoader } from '@/components/ui/ghost-chart-loader'

export default function LoaderTestPage() {
  const [variant, setVariant] = useState<'line' | 'candlestick' | 'area'>('line')
  const [showVolume, setShowVolume] = useState(false)
  const [height, setHeight] = useState(400)

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold gradient-text">Premium Loader Test</h1>
        <p className="text-muted-foreground">
          Test and preview the premium chart loaders
        </p>
      </div>

      {/* Controls */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold">Controls</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm text-muted-foreground mb-2 block">Variant</label>
            <select
              value={variant}
              onChange={(e) => setVariant(e.target.value as any)}
              className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
            >
              <option value="line">Line Chart</option>
              <option value="area">Area Chart</option>
              <option value="candlestick">Candlestick</option>
            </select>
          </div>

          <div>
            <label className="text-sm text-muted-foreground mb-2 block">Height</label>
            <input
              type="number"
              value={height}
              onChange={(e) => setHeight(Number(e.target.value))}
              className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
              min="200"
              max="600"
              step="50"
            />
          </div>

          <div>
            <label className="text-sm text-muted-foreground mb-2 block">Show Volume</label>
            <button
              onClick={() => setShowVolume(!showVolume)}
              className={`w-full px-4 py-2 rounded-lg transition-all ${
                showVolume
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'bg-white/5 text-gray-400 border border-white/10'
              }`}
            >
              {showVolume ? 'Enabled' : 'Disabled'}
            </button>
          </div>
        </div>
      </div>

      {/* Premium Loader Demo */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">PremiumChartLoader</h2>
        <PremiumChartLoader
          height={height}
          message="Loading market data"
          variant={variant}
          showVolume={showVolume}
        />
      </div>

      {/* Ghost Loader Demo */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">GhostChartLoader (Simple)</h2>
        <GhostChartLoader
          height={height}
          message="Fetching live market data"
          showStats={true}
        />
      </div>

      {/* Multiple Sizes Demo */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">Different Sizes</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PremiumChartLoader height={280} message="Small Chart" variant="line" />
          <PremiumChartLoader height={280} message="Small Chart" variant="area" />
        </div>
        <PremiumChartLoader height={200} message="Compact Chart" variant="candlestick" showVolume={true} />
      </div>

      {/* Animation Features */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold">Animation Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <h3 className="font-semibold text-cyan-400">Visual Effects</h3>
            <ul className="space-y-1 text-gray-400">
              <li>✓ Neon glow on chart lines</li>
              <li>✓ Shimmer sweep overlay</li>
              <li>✓ Pulsing endpoint indicator</li>
              <li>✓ Expanding rings animation</li>
              <li>✓ Gradient color transitions</li>
              <li>✓ Trading grid background</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h3 className="font-semibold text-cyan-400">Technical Details</h3>
            <ul className="space-y-1 text-gray-400">
              <li>✓ SVG-based animations</li>
              <li>✓ CSS keyframe animations</li>
              <li>✓ Smooth quadratic curves</li>
              <li>✓ Memoized data generation</li>
              <li>✓ 60fps performance</li>
              <li>✓ No layout shift</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
