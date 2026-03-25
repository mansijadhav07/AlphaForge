'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Activity, BarChart3, Brain, TrendingUp, Network, Target, CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Activity },
  { name: 'Stocks', href: '/stock/AAPL', icon: TrendingUp },
  { name: 'Backtesting', href: '/backtesting', icon: BarChart3 },
  { name: 'Insights', href: '/insights', icon: Brain },
  { name: 'PGM Graph', href: '/pgm-graph', icon: Network },
  { name: 'Feature Impact', href: '/feature-impact', icon: Target },
  { name: 'Model Eval', href: '/model-evaluation', icon: CheckCircle2 },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <nav className="fixed top-0 z-50 w-full glass border-b border-white/10">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-neon-blue blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative bg-gradient-to-br from-neon-blue to-neon-teal p-2 rounded-lg">
                <Activity className="h-6 w-6 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">AlphaForge</h1>
              <p className="text-xs text-muted-foreground">Financial Intelligence</p>
            </div>
          </Link>

          {/* Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const isActive = pathname?.startsWith(item.href)
              const Icon = item.icon
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-neon-blue/20 text-neon-blue'
                      : 'text-muted-foreground hover:text-foreground hover:bg-white/5'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </div>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-bullish/10 border border-bullish/20">
              <div className="h-2 w-2 rounded-full bg-bullish animate-pulse-glow" />
              <span className="text-xs font-medium text-bullish">Live</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
