import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-3 py-1 text-xs font-bold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 shadow-lg hover:scale-105',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-gradient-to-r from-primary to-primary/80 text-primary-foreground hover:from-primary/90 hover:to-primary/70 shadow-primary/20',
        secondary:
          'border-transparent bg-gradient-to-r from-secondary to-secondary/80 text-secondary-foreground hover:from-secondary/90 hover:to-secondary/70',
        destructive:
          'border-transparent bg-gradient-to-r from-destructive to-destructive/80 text-destructive-foreground hover:from-destructive/90 hover:to-destructive/70 shadow-destructive/20',
        outline: 'text-foreground border-white/20 hover:bg-white/5',
        bullish:
          'border-transparent bg-gradient-to-r from-bullish to-bullish-light text-white hover:from-bullish-light hover:to-bullish shadow-bullish/30',
        bearish:
          'border-transparent bg-gradient-to-r from-bearish to-bearish-light text-white hover:from-bearish-light hover:to-bearish shadow-bearish/30',
        neutral:
          'border-transparent bg-gradient-to-r from-neutral to-neutral-light text-white hover:from-neutral-light hover:to-neutral shadow-neutral/30',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
