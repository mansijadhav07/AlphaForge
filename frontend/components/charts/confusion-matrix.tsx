'use client'

interface ConfusionMatrixProps {
  classes: string[]
  matrix: number[][]
  title?: string
}

export function ConfusionMatrix({ classes, matrix, title = 'Confusion Matrix' }: ConfusionMatrixProps) {
  // Calculate max value for color scaling
  const maxValue = Math.max(...matrix.flat())

  // Get color intensity based on value
  const getColor = (value: number) => {
    const intensity = value / maxValue
    if (intensity > 0.7) return 'bg-neon-blue/80'
    if (intensity > 0.5) return 'bg-neon-blue/60'
    if (intensity > 0.3) return 'bg-neon-blue/40'
    if (intensity > 0.1) return 'bg-neon-blue/20'
    return 'bg-white/5'
  }

  // Get text color based on background intensity
  const getTextColor = (value: number) => {
    const intensity = value / maxValue
    return intensity > 0.5 ? 'text-white' : 'text-foreground'
  }

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold gradient-text mb-4">{title}</h3>
      
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Header row */}
          <div className="flex items-center mb-2">
            <div className="w-32" />
            <div className="flex-1 flex justify-center">
              <span className="text-sm font-semibold text-muted-foreground">Predicted</span>
            </div>
          </div>

          {/* Column labels */}
          <div className="flex items-center mb-1">
            <div className="w-32" />
            {classes.map((cls) => (
              <div key={cls} className="flex-1 text-center">
                <span className="text-xs font-medium text-muted-foreground capitalize">
                  {cls}
                </span>
              </div>
            ))}
          </div>

          {/* Matrix rows */}
          <div className="flex">
            {/* Row label container */}
            <div className="flex flex-col justify-center mr-2">
              <div className="flex items-center h-full">
                <span className="text-sm font-semibold text-muted-foreground -rotate-90 whitespace-nowrap">
                  Actual
                </span>
              </div>
            </div>

            {/* Row labels and cells */}
            <div className="flex-1">
              {matrix.map((row, i) => (
                <div key={i} className="flex items-center mb-1">
                  <div className="w-24 text-right pr-3">
                    <span className="text-xs font-medium text-muted-foreground capitalize">
                      {classes[i]}
                    </span>
                  </div>
                  {row.map((value, j) => (
                    <div
                      key={j}
                      className={`flex-1 aspect-square flex items-center justify-center rounded-lg border border-white/10 mx-0.5 transition-all hover:scale-105 ${getColor(value)}`}
                    >
                      <span className={`text-sm font-bold ${getTextColor(value)}`}>
                        {value}
                      </span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div className="mt-4 flex items-center justify-center space-x-4 text-xs">
            <span className="text-muted-foreground">Intensity:</span>
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 rounded bg-white/5" />
              <span className="text-muted-foreground">Low</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 rounded bg-neon-blue/40" />
              <span className="text-muted-foreground">Medium</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 rounded bg-neon-blue/80" />
              <span className="text-muted-foreground">High</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
