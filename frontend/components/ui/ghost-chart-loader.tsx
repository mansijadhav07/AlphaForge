'use client'

import { useEffect, useState } from 'react'
import { Activity, TrendingUp } from 'lucide-react'

interface GhostChartLoaderProps {
  height?: number
  message?: string
  showStats?: boolean
}

export function GhostChartLoader({ 
  height = 400, 
  message = "Fetching live market data",
  showStats = false 
}: GhostChartLoaderProps) {
  const [dots, setDots] = useState('.')

  // Animated dots for loading text
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '.' : prev + '.')
    }, 500)
    return () => clearInterval(interval)
  }, [])

  // Generate ghost chart path (smooth wave-like market movement)
  const generateGhostPath = () => {
    const points = 50
    const width = 100
    const baseHeight = 50
    
    let path = `M 0 ${baseHeight}`
    
    for (let i = 1; i <= points; i++) {
      const x = (i / points) * width
      // Create smooth wave with multiple frequencies for realistic market movement
      const wave1 = Math.sin(i * 0.15) * 8
      const wave2 = Math.sin(i * 0.08) * 12
      const wave3 = Math.sin(i * 0.25) * 4
      const trend = (i / points) * 10 // Slight upward trend
      const y = baseHeight - wave1 - wave2 - wave3 - trend
      
      path += ` L ${x} ${y}`
    }
    
    return path
  }

  return (
    <div 
      className="relative w-full rounded-xl overflow-hidden"
      style={{ height: `${height}px` }}
    >
      {/* Dark gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900" />
      
      {/* Grid lines (like trading charts) */}
      <svg className="absolute inset-0 w-full h-full opacity-20">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(6, 182, 212, 0.1)" strokeWidth="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        
        {/* Horizontal reference lines */}
        {[25, 50, 75].map(y => (
          <line
            key={y}
            x1="0"
            y1={`${y}%`}
            x2="100%"
            y2={`${y}%`}
            stroke="rgba(6, 182, 212, 0.15)"
            strokeWidth="1"
            strokeDasharray="4 4"
          />
        ))}
      </svg>

      {/* Animated ghost chart line */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
          {/* Glow effect */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          
          {/* Gradient for line */}
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#00f5d4" stopOpacity="1" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.3" />
          </linearGradient>
          
          {/* Gradient for area fill */}
          <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#00f5d4" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#00f5d4" stopOpacity="0" />
          </linearGradient>
        </defs>
        
        {/* Area under the line */}
        <path
          d={`${generateGhostPath()} L 100 100 L 0 100 Z`}
          fill="url(#areaGradient)"
          className="animate-pulse"
          style={{ animationDuration: '3s' }}
        />
        
        {/* Main ghost line */}
        <path
          d={generateGhostPath()}
          fill="none"
          stroke="url(#lineGradient)"
          strokeWidth="0.5"
          filter="url(#glow)"
          className="ghost-line"
        />
        
        {/* Pulsing dot at the end */}
        <circle
          cx="100"
          cy="35"
          r="1"
          fill="#00f5d4"
          className="animate-pulse"
          style={{ animationDuration: '1.5s' }}
        >
          <animate
            attributeName="r"
            values="1;1.5;1"
            dur="1.5s"
            repeatCount="indefinite"
          />
        </circle>
      </svg>

      {/* Shimmer overlay effect */}
      <div className="absolute inset-0 shimmer-overlay" />

      {/* Loading indicator */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="flex items-center space-x-3 px-6 py-3 rounded-full bg-slate-900/80 backdrop-blur-sm border border-cyan-500/20">
          <Activity className="h-4 w-4 text-cyan-400 animate-pulse" />
          <span className="text-sm font-medium text-cyan-400">
            📡 {message}{dots}
          </span>
        </div>
      </div>

      {/* Optional: Ghost stats */}
      {showStats && (
        <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-cyan-400/50 animate-pulse" 
                     style={{ animationDelay: `${i * 0.2}s` }} />
                <div className="h-3 w-16 bg-white/10 rounded animate-pulse" 
                     style={{ animationDelay: `${i * 0.2}s` }} />
              </div>
            ))}
          </div>
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4 text-cyan-400/50" />
            <div className="h-3 w-12 bg-white/10 rounded animate-pulse" />
          </div>
        </div>
      )}

      {/* CSS animations */}
      <style jsx>{`
        .ghost-line {
          animation: ghostWave 4s ease-in-out infinite;
        }

        @keyframes ghostWave {
          0%, 100% {
            transform: translateX(0) scaleY(1);
            opacity: 0.6;
          }
          50% {
            transform: translateX(-2px) scaleY(1.02);
            opacity: 0.8;
          }
        }

        .shimmer-overlay {
          background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(0, 245, 212, 0.1) 50%,
            transparent 100%
          );
          animation: shimmer 3s infinite;
        }

        @keyframes shimmer {
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
