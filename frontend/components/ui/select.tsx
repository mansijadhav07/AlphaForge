'use client'

import * as React from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SelectProps {
  value: string
  onValueChange: (value: string) => void
  options: Array<{ value: string; label: string }>
  placeholder?: string
  className?: string
}

export function Select({
  value,
  onValueChange,
  options,
  placeholder = 'Select...',
  className,
}: SelectProps) {
  const [isOpen, setIsOpen] = React.useState(false)
  const selectedOption = options.find((opt) => opt.value === value)

  return (
    <div className={cn('relative', className)}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-2 rounded-lg glass-hover border border-white/10 text-sm"
      >
        <span>{selectedOption?.label || placeholder}</span>
        <ChevronDown className={cn('h-4 w-4 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute z-50 w-full mt-2 glass border border-white/10 rounded-lg overflow-hidden animate-slide-in">
            {options.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => {
                  onValueChange(option.value)
                  setIsOpen(false)
                }}
                className={cn(
                  'w-full px-4 py-2 text-left text-sm hover:bg-white/10 transition-colors',
                  value === option.value && 'bg-neon-blue/20 text-neon-blue'
                )}
              >
                {option.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
