'use client'

import { useEffect, useState } from 'react'

interface FullScreenLoaderProps {
  message?: string
}

export function FullScreenLoader({ 
  message = "Loading market data"
}: FullScreenLoaderProps) {
  const [dots, setDots] = useState('.')

  // Animated dots
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '.' : prev + '.')
    }, 500)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="fixed top-16 left-0 right-0 bottom-0 z-40 flex items-center justify-center bg-[#0b0f17]">
      {/* Subtle radial glow in background */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          background: 'radial-gradient(circle at 50% 50%, rgba(0, 245, 212, 0.15) 0%, transparent 60%)'
        }}
      />

      {/* Loader content */}
      <div className="relative flex flex-col items-center space-y-8">
        {/* Concentric rotating rings */}
        <div className="relative w-32 h-32">
          {/* Outer ring - slow clockwise */}
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-cyan-400/60 border-r-cyan-400/40 animate-spin-slow" 
               style={{ animationDuration: '3s' }} />
          
          {/* Middle ring - medium counter-clockwise */}
          <div className="absolute inset-3 rounded-full border-2 border-transparent border-t-[#00f5d4] border-l-[#00f5d4]/60 animate-spin-reverse" 
               style={{ animationDuration: '2s' }} />
          
          {/* Inner ring - fast clockwise */}
          <div className="absolute inset-6 rounded-full border-2 border-transparent border-t-teal-400 border-r-teal-400/50 animate-spin" 
               style={{ animationDuration: '1.5s' }} />
          
          {/* Center pulsing dot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-[#00f5d4] animate-pulse shadow-lg shadow-cyan-400/50" 
                 style={{ animationDuration: '2s' }} />
          </div>

          {/* Glow effect */}
          <div className="absolute inset-0 rounded-full bg-cyan-400/20 blur-2xl animate-pulse" 
               style={{ animationDuration: '3s' }} />
        </div>

        {/* Loading text */}
        <div className="text-center space-y-2">
          <p className="text-lg font-medium text-cyan-400/90 tracking-wide">
            {message}<span className="inline-block w-4 text-left">{dots}</span>
          </p>
          <p className="text-xs text-cyan-400/50 font-mono">
            Powered by AlphaForge
          </p>
        </div>
      </div>

      {/* Global animation styles */}
      <style jsx global>{`
        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes spin-reverse {
          from {
            transform: rotate(360deg);
          }
          to {
            transform: rotate(0deg);
          }
        }

        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }

        .animate-spin-reverse {
          animation: spin-reverse 2s linear infinite;
        }
      `}</style>
    </div>
  )
}
