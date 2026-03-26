'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { Activity, BarChart3, Brain, TrendingUp, Network, Target, CheckCircle2, AlertTriangle, GitBranch, Layers, Scale } from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Activity },
  { name: 'Stocks', href: '/stock/AAPL', icon: TrendingUp },
  { name: 'Backtesting', href: '/backtesting', icon: BarChart3 },
  { name: 'Insights', href: '/insights', icon: Brain },
  { name: 'PGM Graph', href: '/pgm-graph', icon: Network },
  { name: 'Structure', href: '/structure-analysis', icon: GitBranch },
  { name: 'Discretization', href: '/discretization', icon: Layers },
  { name: 'Baselines', href: '/baseline-comparison', icon: Scale },
  { name: 'Feature Impact', href: '/feature-impact', icon: Target },
  { name: 'Model Eval', href: '/model-evaluation', icon: CheckCircle2 },
  { name: 'Failures', href: '/model-failures', icon: AlertTriangle },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <motion.nav 
      className="fixed top-0 z-50 w-full glass-card border-b border-white/10"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
    >
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Premium Logo */}
          <Link href="/dashboard" className="flex items-center space-x-3 group">
            <motion.div 
              className="relative"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <motion.div 
                className="absolute inset-0 bg-neon-blue blur-xl opacity-50 group-hover:opacity-100 transition-opacity duration-500"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 0.8, 0.5]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              <div className="relative bg-gradient-to-br from-neon-blue via-neon-teal to-neon-purple p-2.5 rounded-xl shadow-lg">
                <Activity className="h-6 w-6 text-white" />
              </div>
            </motion.div>
            <div>
              <motion.h1 
                className="text-xl font-bold gradient-text"
                whileHover={{ scale: 1.02 }}
              >
                AlphaForge
              </motion.h1>
              <p className="text-xs text-muted-foreground font-medium">Financial Intelligence</p>
            </div>
          </Link>

          {/* Premium Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item, index) => {
              const isActive = pathname?.startsWith(item.href)
              const Icon = item.icon
              
              return (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link
                    href={item.href}
                    className="relative block"
                  >
                    <motion.div
                      className={cn(
                        'flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300 relative overflow-hidden',
                        isActive
                          ? 'text-neon-blue'
                          : 'text-muted-foreground hover:text-foreground'
                      )}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {/* Active indicator background */}
                      {isActive && (
                        <motion.div
                          className="absolute inset-0 bg-gradient-to-r from-neon-blue/20 via-neon-teal/20 to-neon-blue/20 rounded-xl"
                          layoutId="activeNav"
                          transition={{ 
                            type: "spring", 
                            stiffness: 380, 
                            damping: 30 
                          }}
                        />
                      )}
                      
                      {/* Hover effect */}
                      <motion.div
                        className="absolute inset-0 bg-white/5 rounded-xl opacity-0"
                        whileHover={{ opacity: 1 }}
                        transition={{ duration: 0.2 }}
                      />
                      
                      <Icon className={cn(
                        "h-4 w-4 relative z-10 transition-transform duration-300",
                        isActive && "animate-pulse"
                      )} />
                      <span className="relative z-10">{item.name}</span>
                    </motion.div>
                  </Link>
                </motion.div>
              )
            })}
          </div>

          {/* Premium Status Indicator */}
          <motion.div 
            className="flex items-center space-x-2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <motion.div 
              className="flex items-center space-x-2 px-4 py-2 rounded-full bg-gradient-to-r from-bullish/10 to-bullish/5 border border-bullish/30 shadow-lg"
              whileHover={{ scale: 1.05 }}
            >
              <motion.div 
                className="h-2.5 w-2.5 rounded-full bg-bullish shadow-lg shadow-bullish/50"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.8, 1]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              <span className="text-xs font-bold text-bullish tracking-wide">LIVE</span>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </motion.nav>
  )
}
