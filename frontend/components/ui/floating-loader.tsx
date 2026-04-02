'use client'

import { useEffect, useState } from 'react'
import { Activity } from 'lucide-react'

interface FloatingLoaderProps {
  isLoading: boolean
  message?: string
  position?: 'top-center' | 'top-right'
}

export function FloatingLoader({ 
  isLoading, 
  message = "Updating market data",
  position = 'top-center'
}: FloatingLoaderProps) {
  const [dots, setDots] = useState('.')
  const [isVisible, setIsVisible] = useState(false)

  // Animated dots
  useEffect(() => {
    if (!isLoading) return
    
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '.' : prev + '.')
    }, 500)
    return () => clearInterval(interval)
  }, [isLoading])

  // Smooth fade in/out
  useEffect(() => {
    if (isLoading) {
      setIsVisible(true)
    } else {
      const timeout = setTimeout(() => setIsVisible(false), 300)
      return () => clearTimeout(timeout)
    }
  }, [isLoading])

  if (!isVisible) return null

  const positionClasses = position === 'top-center' 
    ? 'left-1/2 -translate-x-1/2' 
    : 'right-6'

  return (
    <div
      className={`fixed top-20 ${positionClasses} z-50 transition-all duration-300 ${
        isLoading ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2'
      }`}
    >
      <div className="flex items-center space-x-3 px-4 py-2.5 rounded-full bg-slate-900/95 backdrop-blur-md border border-cyan-500/30 shadow-lg shadow-cyan-500/20">
        {/* Animated spinner ring */}
        <div className="relative w-5 h-5">
          {/* Outer glow ring */}
          <div className="absolute inset-0 rounded-full border-2 border-cyan-400/20 animate-ping" 
               style={{ animationDuration: '2s' }} />
          
          {/* Main spinning ring */}
          <svg className="w-5 h-5 animate-spin" style={{ animationDuration: '1.2s' }} viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
              style={{ color: '#06b6d4' }}
            />
            <path
              className="opacity-75"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              d="M12 2 A10 10 0 0 1 22 12"
              style={{ color: '#00f5d4' }}
            >
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0 12 12"
                to="360 12 12"
                dur="1.2s"
                repeatCount="indefinite"
              />
            </path>
          </svg>
          
          {/* Inner pulse dot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" 
                 style={{ animationDuration: '1.5s' }} />
          </div>
        </div>

        {/* Loading text */}
        {message && (
          <span className="text-xs font-medium text-cyan-400/90 tracking-wide">
            {message}<span className="inline-block w-3 text-left">{dots}</span>
          </span>
        )}
      </div>

      {/* Subtle glow effect underneath */}
      <div className="absolute inset-0 -z-10 blur-xl bg-cyan-500/20 rounded-full" />
    </div>
  )
}
