import { Card } from "@/components/ui/card"
import { ArrowUpRight } from "lucide-react"
import type React from "react"

interface MetricsCardProps {
  title: string
  value: string
  change: {
    value: string
    percentage: string
    isPositive: boolean
  }
  chart?: React.ReactNode
  mode?: 'fun' | 'serious'
  onModeChange?: (mode: 'fun' | 'serious') => void
}

export function MetricsCard({ title, value, change, chart, mode = 'serious', onModeChange }: MetricsCardProps) {
  const handleModeToggle = () => {
    if (onModeChange) {
      onModeChange(mode === 'fun' ? 'serious' : 'fun');
    }
  };

  return (
    <Card
      className={`p-4 ${
        mode === 'fun' 
          ? 'bg-white/80 backdrop-blur border-pink-200' 
          : 'bg-gray-800/50 backdrop-blur border-gray-700'
      }`}
      onClick={onModeChange ? handleModeToggle : undefined}
      style={onModeChange ? { cursor: 'pointer' } : undefined}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-sm ${
          mode === 'fun' ? 'text-gray-600' : 'text-gray-400'
        }`}>{title}</h3>
        {chart ? (
          <ArrowUpRight className={`h-4 w-4 ${
            mode === 'fun' ? 'text-gray-600' : 'text-gray-400'
          }`} />
        ) : null}
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className={`text-2xl font-bold ${
            mode === 'fun' ? 'text-gray-900' : 'text-gray-100'
          }`}>{value}</p>
          <div className="flex items-center gap-1 mt-1">
            <span className={`text-sm ${
              mode === 'fun' ? 'text-gray-600' : 'text-gray-400'
            }`}>+{change.value}</span>
            <span className={`text-sm ${
              change.isPositive 
                ? 'text-green-500' 
                : mode === 'fun' ? 'text-red-400' : 'text-red-500'
            }`}>
              {change.percentage}
            </span>
          </div>
        </div>
        {chart}
      </div>
    </Card>
  )
}

