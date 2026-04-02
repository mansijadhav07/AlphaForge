'use client'

import { useEffect, useState, useMemo } from 'react'
import { Activity, TrendingUp, BarChart3 } from 'lucide-react'

interface PremiumChartLoaderProps {
  height?: number
  message?: string
  variant?: 'line' | 'candlestick' | 'area'
  showVolume?: boolean
}

export function PremiumChartLoader({ 
  height = 400, 
  message = "Fetching live market data",
  variant = 'line',
  showVolume = false
}: PremiumChartLoaderProps) {
  const [dots, setDots] = useState('.')
  const [animationPhase, setAnimationPhase] = useState(0)

  // Animated dots
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '.' : prev + '.')
    }, 500)
    return () => clearInterval(interval)
  }, [])

  // Animation phase for wave movement
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimationPhase(prev => (prev + 1) % 100)
    }, 50)
    return () => clearInterval(interval)
  }, [])

  // Generate realistic market data points
  const ghostData = useMemo(() => {
    const points = 60
    const data = []
    let price = 180
    
    for (let i = 0; i < points; i++) {
      // Simulate realistic price movement
      const trend = Math.sin(i * 0.1) * 2
      const noise = (Math.random() - 0.5) * 1.5
      const momentum = Math.sin(i * 0.05) * 3
      
      price += trend + noise + momentum * 0.1
      
      data.push({
        x: (i / points) * 100,
        y: 50 - ((price - 180) / 10) * 20, // Normalize to 0-100 range
        volume: 30 + Math.random() * 40
      })
    }
    
    return data
  }, [])

  // Generate SVG path for line chart
  const linePath = useMemo(() => {
    if (ghostData.length === 0) return ''
    
    let path = `M ${ghostData[0].x} ${ghostData[0].y}`
    for (let i = 1; i < ghostData.length; i++) {
      // Use smooth curves instead of straight lines
      const curr = ghostData[i]
      const prev = ghostData[i - 1]
      const cpx = (prev.x + curr.x) / 2
      
      path += ` Q ${cpx} ${prev.y}, ${curr.x} ${curr.y}`
    }
    
    return path
  }, [ghostData])

  // Generate area path (for fill under line)
  const areaPath = useMemo(() => {
    if (ghostData.length === 0) return ''
    return `${linePath} L 100 100 L 0 100 Z`
  }, [linePath, ghostData])

  return (
    <div 
      className="relative w-full rounded-xl overflow-hidden border border-white/5"
      style={{ height: `${height}px` }}
    >
      {/* Premium dark background with subtle gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
      
      {/* Subtle radial glow */}
      <div className="absolute inset-0 bg-radial-gradient opacity-30" 
           style={{
             background: 'radial-gradient(circle at 50% 50%, rgba(0, 245, 212, 0.1) 0%, transparent 70%)'
           }} />

      {/* Trading chart grid */}
      <svg className="absolute inset-0 w-full h-full">
        <defs>
          {/* Grid pattern */}
          <pattern id="trading-grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path 
              d="M 50 0 L 0 0 0 50" 
              fill="none" 
              stroke="rgba(6, 182, 212, 0.08)" 
              strokeWidth="0.5"
            />
          </pattern>
          
          {/* Glow filter for line */}
          <filter id="neon-glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          
          {/* Line gradient */}
          <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.4">
              <animate attributeName="stop-opacity" values="0.4;0.8;0.4" dur="2s" repeatCount="indefinite" />
            </stop>
            <stop offset="50%" stopColor="#00f5d4" stopOpacity="1">
              <animate attributeName="stop-opacity" values="1;0.6;1" dur="2s" repeatCount="indefinite" />
            </stop>
            <stop offset="100%" stopColor="#14b8a6" stopOpacity="0.4">
              <animate attributeName="stop-opacity" values="0.4;0.8;0.4" dur="2s" repeatCount="indefinite" />
            </stop>
          </linearGradient>
          
          {/* Area gradient */}
          <linearGradient id="area-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#00f5d4" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#00f5d4" stopOpacity="0" />
          </linearGradient>
        </defs>
        
        {/* Grid background */}
        <rect width="100%" height="100%" fill="url(#trading-grid)" />
        
        {/* Horizontal reference lines */}
        {[20, 40, 60, 80].map(y => (
          <line
            key={y}
            x1="0"
            y1={`${y}%`}
            x2="100%"
            y2={`${y}%`}
            stroke="rgba(6, 182, 212, 0.12)"
            strokeWidth="1"
            strokeDasharray="6 4"
          />
        ))}
        
        {/* Y-axis labels (ghost) */}
        {[20, 40, 60, 80].map((y, i) => (
          <g key={y}>
            <rect
              x="2"
              y={`${y - 2}%`}
              width="30"
              height="8"
              fill="rgba(255, 255, 255, 0.05)"
              rx="2"
              className="animate-pulse"
              style={{ animationDelay: `${i * 0.1}s` }}
            />
          </g>
        ))}
      </svg>

      {/* Main chart SVG */}
      <svg 
        className="absolute inset-0 w-full h-full" 
        viewBox="0 0 100 100" 
        preserveAspectRatio="none"
      >
        {/* Area fill under line */}
        <path
          d={areaPath}
          fill="url(#area-gradient)"
          className="animate-pulse"
          style={{ animationDuration: '3s' }}
        />
        
        {/* Main ghost line with glow */}
        <path
          d={linePath}
          fill="none"
          stroke="url(#line-gradient)"
          strokeWidth="0.8"
          filter="url(#neon-glow)"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {/* Animate the line drawing */}
          <animate
            attributeName="stroke-dasharray"
            values="0 200;200 0;0 200"
            dur="4s"
            repeatCount="indefinite"
          />
        </path>
        
        {/* Pulsing endpoint */}
        <circle
          cx={ghostData[ghostData.length - 1]?.x || 100}
          cy={ghostData[ghostData.length - 1]?.y || 50}
          r="1.5"
          fill="#00f5d4"
          filter="url(#neon-glow)"
        >
          <animate
            attributeName="r"
            values="1;2;1"
            dur="1.5s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="1;0.5;1"
            dur="1.5s"
            repeatCount="indefinite"
          />
        </circle>
        
        {/* Pulse rings around endpoint */}
        <circle
          cx={ghostData[ghostData.length - 1]?.x || 100}
          cy={ghostData[ghostData.length - 1]?.y || 50}
          r="1"
          fill="none"
          stroke="#00f5d4"
          strokeWidth="0.3"
          opacity="0"
        >
          <animate
            attributeName="r"
            values="1;4;6"
            dur="2s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="0.8;0.3;0"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
      </svg>

      {/* Shimmer sweep effect */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(0, 245, 212, 0.15) 50%, transparent 100%)',
          animation: 'shimmer-sweep 3s infinite',
          animationTimingFunction: 'ease-in-out'
        }}
      />

      {/* Volume bars (if enabled) */}
      {showVolume && (
        <svg className="absolute bottom-0 left-0 right-0 h-20" viewBox="0 0 100 20" preserveAspectRatio="none">
          {ghostData.map((point, i) => (
            <rect
              key={i}
              x={point.x - 0.5}
              y={20 - (point.volume / 100) * 20}
              width="1"
              height={(point.volume / 100) * 20}
              fill="rgba(6, 182, 212, 0.2)"
              className="animate-pulse"
              style={{ animationDelay: `${i * 0.02}s`, animationDuration: '2s' }}
            />
          ))}
        </svg>
      )}

      {/* Loading message */}
      <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2">
        <div className="flex items-center space-x-3 px-5 py-2.5 rounded-full bg-slate-900/90 backdrop-blur-md border border-cyan-500/30 shadow-lg shadow-cyan-500/10">
          <div className="relative">
            <Activity className="h-4 w-4 text-cyan-400" />
            <span className="absolute -top-1 -right-1 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400"></span>
            </span>
          </div>
          <span className="text-sm font-medium text-cyan-400 tracking-wide">
            {message}<span className="inline-block w-4 text-left">{dots}</span>
          </span>
        </div>
      </div>

      {/* Corner indicators (like professional trading platforms) */}
      <div className="absolute top-4 left-4 flex items-center space-x-2">
        <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
        <span className="text-xs font-mono text-cyan-400/70">LOADING</span>
      </div>

      <div className="absolute top-4 right-4">
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900/60 border border-cyan-500/20">
          <BarChart3 className="h-3 w-3 text-cyan-400/70" />
          <span className="text-xs font-mono text-cyan-400/70">REAL-TIME</span>
        </div>
      </div>

      {/* Global styles */}
      <style jsx global>{`
        @keyframes shimmer-sweep {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  )
}
