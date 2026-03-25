'use client'

import { motion, HTMLMotionProps } from 'framer-motion'
import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode
  delay?: number
  hover?: boolean
  glow?: boolean
  className?: string
}

export function AnimatedCard({ 
  children, 
  delay = 0, 
  hover = true,
  glow = false,
  className,
  ...props 
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay,
        ease: [0.25, 0.1, 0.25, 1]
      }}
      whileHover={hover ? { 
        y: -4,
        transition: { duration: 0.2 }
      } : undefined}
      className={cn(
        'glass-card p-6',
        hover && 'cursor-pointer',
        glow && 'glow-blue-hover',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  )
}

export function AnimatedCardGrid({ 
  children, 
  className 
}: { 
  children: ReactNode
  className?: string 
}) {
  return (
    <div className={cn('grid gap-6', className)}>
      {children}
    </div>
  )
}
