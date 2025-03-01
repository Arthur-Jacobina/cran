'use client'

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { MetricsCard } from "@/components/metrics-card"
import { StatsChart } from "@/components/stats-chart"
import { VaultTable } from "@/components/vault-table"
import { BarChart3, Briefcase, ChevronDown, Flower, Globe, Home, LayoutDashboard, LifeBuoy, Settings, Wallet } from "lucide-react"
import { useState } from "react"
import { motion } from "framer-motion"
import dynamic from "next/dynamic"

const HeartParticles = dynamic(
    () => import('@/components/ui/heart-particles'),
    { ssr: false }
  );
const HyperText = dynamic(
    () => import('@/components/ui/hyper-text'),
    { ssr: false }
  );
  
export default function Page() {
  const [mode, setMode] = useState<'fun' | 'serious'>('fun')
  const [baseAmount] = useState(1000) // Example base amount
  const [yieldRate] = useState(0.425) // 42.5% yield rate
  
  // Calculate accrued yield
  const accruedYield = baseAmount * yieldRate
  const totalAmount = baseAmount + accruedYield
  const formattedYield = `$${totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  
  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      mode === 'fun' ? 'bg-gradient-to-b from-blue-50/10 to-pink-50/10 text-gray-900' : 'bg-gray-900 text-gray-100'
    }`}>
     {mode === 'fun' && <HeartParticles />}
      <main className="p-6 z-10">
        <div className="mb-6 flex items-center justify-between">
          <div className="space-y-1">
            <HyperText className="text-2xl text-blue-500 font-bold" text={mode === 'fun' ? 'Love Levels' : 'Overview'} />
          </div>
          <div className="flex items-center gap-4">
          <motion.button
  onClick={() => setMode(mode === 'fun' ? 'serious' : 'fun')}
  className={`relative rounded-full p-1 w-20 h-10 ${
    mode === 'fun' ? 'bg-pink-200 border border-pink-300' : 'bg-gray-700 border border-gray-600'
  }`}
  whileTap={{ scale: 0.95 }}
>
  <div className="relative w-full h-full">
    <motion.div
      className={`absolute w-8 h-8 rounded-full flex items-center justify-center ${
        mode === 'fun' ? 'bg-white' : 'bg-gray-800'
      }`}
      initial={false}
      animate={{
        left: mode === 'fun' ? 'calc(100% - 32px)' : '0px',
      }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      {mode === 'fun' ? 
        <Flower className="h-5 w-5 text-pink-500" /> : 
        <Briefcase className="h-5 w-5 text-gray-300" />
      }
    </motion.div>
  </div>
  <span className="sr-only">{mode === 'fun' ? 'Switch to serious mode' : 'Switch to fun mode'}</span>
</motion.button>
            <Button variant="outline" className={`gap-2 ${mode === 'serious' ? 'bg-gray-800 text-white border-gray-700 hover:bg-gray-700' : ''}`}>
              Ethereum Network
              <ChevronDown className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <MetricsCard
            title={mode === 'fun' ? 'Love Credits' : 'Your Balance'}
            value="$1,425.00"
            change={{ value: "$303.53", percentage: "21.3%", isPositive: true }}
            mode={mode}
            onModeChange={setMode}
          />
          <MetricsCard
            title={mode === 'fun' ? 'GF Sweetness' : 'Accrued Yield'}
            value={formattedYield}
            change={{ value: `$${accruedYield.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, percentage: "42.5%", isPositive: true }}
            mode={mode}
            onModeChange={setMode}
          />
        </div>
        <Card className={`mt-6 p-6 ${mode === 'serious' ? 'bg-gray-800 border-gray-700' : ''}`}>
          <div className="mb-4 flex items-center justify-between">
            <h2 className={`${mode === 'fun' ? 'text-gray-900' : 'text-gray-100'} text-lg font-semibold`}>
              {mode === 'fun' ? 'Love Statistics' : 'General Statistics'}
            </h2>
            <div className="flex gap-2">
              <Button size="sm" variant="ghost" className={mode === 'serious' ? 'text-gray-200 hover:bg-gray-700' : ''}>
                Today
              </Button>
              <Button size="sm" variant="ghost" className={mode === 'serious' ? 'text-gray-200 hover:bg-gray-700' : ''}>
                Last week
              </Button>
              <Button size="sm" variant="ghost" className={mode === 'serious' ? 'text-gray-200 hover:bg-gray-700' : ''}>
                Last month
              </Button>
              <Button size="sm" variant="ghost" className={mode === 'serious' ? 'text-gray-200 hover:bg-gray-700' : ''}>
                Last 6 month
              </Button>
              <Button size="sm" variant="ghost" className={mode === 'serious' ? 'text-gray-200 hover:bg-gray-700' : ''}>
                Year
              </Button>
            </div>
          </div>
          <StatsChart />
        </Card>
        <div className="mt-6">
          <VaultTable />
        </div>
      </main>
    </div>
  )
}