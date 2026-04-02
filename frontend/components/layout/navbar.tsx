'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, TrendingUp, Brain, BarChart3, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ModelDropdown } from './model-dropdown'

const mainNavigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Stocks', href: '/stock/AAPL' },
  { name: 'Insights', href: '/insights' },
  { name: 'Backtesting', href: '/backtesting' },
]

export function Navbar() {
  const pathname = usePathname()
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false)

  // Check if current path is in Model Intelligence section
  const isModelIntelligenceActive = pathname?.match(
    /\/(pgm-graph|structure-analysis|discretization|feature-impact|baseline-comparison|model-evaluation|calibration|model-failures)/
  )

  return (
    <motion.nav 
      className="fixed top-0 z-[100] w-full backdrop-blur-xl bg-gray-950/80 border-b border-white/10"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
    >
      <div className="px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-3 group">
            <motion.div 
              className="relative"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="relative bg-gradient-to-br from-cyan-500 via-teal-500 to-cyan-600 p-2 rounded-lg shadow-lg">
                <Activity className="h-5 w-5 text-white" />
              </div>
            </motion.div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
                AlphaForge
              </h1>
              <p className="text-[10px] text-gray-400 font-medium">Financial Intelligence</p>
            </div>
          </Link>

          {/* Main Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {mainNavigation.map((item) => {
              const isActive = pathname?.startsWith(item.href)
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className="relative"
                >
                  <motion.div
                    className={cn(
                      'px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 relative',
                      isActive
                        ? 'text-cyan-400'
                        : 'text-gray-300 hover:text-white'
                    )}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {isActive && (
                      <motion.div
                        className="absolute inset-0 bg-cyan-500/10 rounded-lg border border-cyan-500/20"
                        layoutId="activeTab"
                        transition={{ 
                          type: "spring", 
                          stiffness: 380, 
                          damping: 30 
                        }}
                      />
                    )}
                    <span className="relative z-10">{item.name}</span>
                    {isActive && (
                      <motion.div
                        className="absolute -bottom-[9px] left-1/2 -translate-x-1/2 w-12 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
                        layoutId="activeUnderline"
                        transition={{ 
                          type: "spring", 
                          stiffness: 380, 
                          damping: 30 
                        }}
                      />
                    )}
                  </motion.div>
                </Link>
              )
            })}

            {/* Model Intelligence Dropdown */}
            <div 
              className="relative z-[110]"
              onMouseEnter={() => setIsModelDropdownOpen(true)}
              onMouseLeave={() => setIsModelDropdownOpen(false)}
            >
              <motion.button
                className={cn(
                  'flex items-center space-x-1.5 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 relative',
                  isModelIntelligenceActive
                    ? 'text-cyan-400'
                    : 'text-gray-300 hover:text-white'
                )}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isModelIntelligenceActive && (
                  <motion.div
                    className="absolute inset-0 bg-cyan-500/10 rounded-lg border border-cyan-500/20"
                    layoutId="activeTab"
                    transition={{ 
                      type: "spring", 
                      stiffness: 380, 
                      damping: 30 
                    }}
                  />
                )}
                <span className="relative z-10">Model Intelligence</span>
                <ChevronDown 
                  className={cn(
                    "h-4 w-4 relative z-10 transition-transform duration-200",
                    isModelDropdownOpen && "rotate-180"
                  )} 
                />
                {isModelIntelligenceActive && (
                  <motion.div
                    className="absolute -bottom-[9px] left-1/2 -translate-x-1/2 w-12 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
                    layoutId="activeUnderline"
                    transition={{ 
                      type: "spring", 
                      stiffness: 380, 
                      damping: 30 
                    }}
                  />
                )}
              </motion.button>

              {/* Dropdown Menu */}
              <AnimatePresence>
                {isModelDropdownOpen && <ModelDropdown />}
              </AnimatePresence>
            </div>
          </div>

          {/* Status Indicator */}
          <motion.div 
            className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <motion.div 
              className="h-2 w-2 rounded-full bg-emerald-400"
              animate={{ 
                scale: [1, 1.2, 1],
                opacity: [1, 0.7, 1]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
            <span className="text-xs font-bold text-emerald-400 tracking-wide">LIVE</span>
          </motion.div>
        </div>
      </div>
    </motion.nav>
  )
}
