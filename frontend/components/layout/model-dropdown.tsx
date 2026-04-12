'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { Network, GitBranch, Layers, Target, Scale, CheckCircle2, Gauge, AlertTriangle, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

const modelSections = [
  {
    title: 'Model',
    items: [
      { name: 'Graph', href: '/pgm-graph', icon: Network, description: 'Bayesian network structure' },
      { name: 'Structure', href: '/structure-analysis', icon: GitBranch, description: 'Dependency analysis' },
    ]
  },
  {
    title: 'Data',
    items: [
      { name: 'Feature Pipeline', href: '/feature-intelligence', icon: Sparkles, description: 'Data transformation flow' },
      { name: 'Discretization', href: '/discretization', icon: Layers, description: 'Feature binning' },
    ]
  },
  {
    title: 'Analysis',
    items: [
      { name: 'Feature Impact', href: '/feature-impact', icon: Target, description: 'Feature importance' },
      { name: 'Baselines', href: '/baseline-comparison', icon: Scale, description: 'Model comparison' },
    ]
  },
  {
    title: 'Evaluation',
    items: [
      { name: 'Model Eval', href: '/model-evaluation', icon: CheckCircle2, description: 'Performance metrics' },
      { name: 'Calibration', href: '/calibration', icon: Gauge, description: 'Probability calibration' },
      { name: 'Failures', href: '/model-failures', icon: AlertTriangle, description: 'Error analysis' },
    ]
  },
]

export function ModelDropdown() {
  const pathname = usePathname()

  return (
    <motion.div
      className="absolute top-full right-0 mt-2 w-[480px] origin-top-right"
      initial={{ opacity: 0, y: -10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ duration: 0.15, ease: "easeOut" }}
    >
      <div className="backdrop-blur-xl bg-gray-900/95 border border-white/10 rounded-xl shadow-2xl overflow-hidden">
        <div className="p-3">
          <div className="grid grid-cols-2 gap-3">
            {modelSections.map((section, sectionIdx) => (
              <div key={section.title}>
                {/* Section Header */}
                <div className="px-3 py-2 mb-1">
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                    {section.title}
                  </h3>
                </div>

                {/* Section Items */}
                <div className="space-y-0.5">
                  {section.items.map((item) => {
                    const isActive = pathname === item.href
                    const Icon = item.icon

                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className="block"
                      >
                        <motion.div
                          className={cn(
                            'flex items-start space-x-3 px-3 py-2.5 rounded-lg transition-all duration-150 relative group',
                            isActive
                              ? 'bg-cyan-500/10 border border-cyan-500/20'
                              : 'hover:bg-white/5 border border-transparent'
                          )}
                          whileHover={{ x: 2 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <div className={cn(
                            'mt-0.5 p-1.5 rounded-md transition-colors',
                            isActive 
                              ? 'bg-cyan-500/20 text-cyan-400' 
                              : 'bg-gray-800 text-gray-400 group-hover:bg-gray-700 group-hover:text-gray-300'
                          )}>
                            <Icon className="h-3.5 w-3.5" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className={cn(
                              'text-sm font-semibold transition-colors',
                              isActive 
                                ? 'text-cyan-400' 
                                : 'text-gray-200 group-hover:text-white'
                            )}>
                              {item.name}
                            </div>
                            <div className="text-xs text-gray-500 mt-0.5">
                              {item.description}
                            </div>
                          </div>
                          {isActive && (
                            <motion.div
                              className="absolute right-2 top-1/2 -translate-y-1/2 w-1 h-6 bg-cyan-400 rounded-full"
                              layoutId="activeDropdownItem"
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
                </div>

                {/* Divider between sections (except last) */}
                {sectionIdx < modelSections.length - 1 && sectionIdx % 2 === 1 && (
                  <div className="col-span-2 my-2 border-t border-white/5" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Footer hint */}
        <div className="px-4 py-2 bg-gray-950/50 border-t border-white/5">
          <p className="text-xs text-gray-500 text-center">
            Comprehensive model analysis and evaluation tools
          </p>
        </div>
      </div>
    </motion.div>
  )
}
