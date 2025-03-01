'use client'

import AnimatedShinyText from "@/components/ui/animated-shiny-text"
import { Button } from "@/components/ui/button"
import HeartParticles from "@/components/ui/heart-particles"
import { Input } from "@/components/ui/input"
import { ChevronDown, Smile } from "lucide-react"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"

interface FloatingToken {
  width: number
  height: number
  left: number
  top: number
  duration: number
  delay: number
}

export default function Home() {
  const [floatingTokens, setFloatingTokens] = useState<FloatingToken[]>([])
  const [selectedFlowers, setSelectedFlowers] = useState(0)

  useEffect(() => {
    // Generate random values after component mounts
    const tokens = Array(8).fill(null).map(() => ({
      width: Math.random() * 100 + 80,
      height: Math.random() * 100 + 80,
      left: Math.random() * 100,
      top: Math.random() * 100,
      duration: Math.random() * 10 + 15,
      delay: Math.random() * 5
    }))
    setFloatingTokens(tokens)
  }, [])
  const router = useRouter()
  
  return (
    <div className="min-h-screen bg-white text-gray-800 relative overflow-hidden">
      <HeartParticles />
      {/* Background floating tokens */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {floatingTokens.map((token, i) => (
          <div
            key={i}
            className="absolute rounded-full opacity-30"
            style={{
              width: `${token.width}px`,
              height: `${token.height}px`,
              left: `${token.left}%`,
              top: `${token.top}%`,
              transform: `translate(-50%, -50%)`,
              animation: `float ${token.duration}s ease-in-out infinite`,
              animationDelay: `${token.delay}s`,
              backgroundImage: `url(/api/waifu)`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
          />
        ))}
      </div>

      {/* Updated main content with two-column layout */}
      <div className="flex items-center justify-center h-screen">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-12">
            {/* Left column with image */}
            <div className="w-full md:w-1/2">
              <div className="relative max-w-[500px] mx-auto">
                <div className="relative w-full pt-[150%] rounded-2xl">
                  <div className="absolute inset-0 rounded-2xl bg-blue-500/20 blur-xl animate-pulse" />
                  <Image
                    src="/5.jpeg"
                    alt="Cran AI Avatar"
                    className="absolute inset-0 rounded-2xl shadow-xl object-cover w-full h-[80%]"
                    fill
                    priority
                    unoptimized
                  />
                </div>
              </div>
            </div>

            {/* Right column with swap card */}
            <div className="w-full md:w-1/2 z-10">
              <div className="w-full max-w-md mx-auto">
                <AnimatedShinyText className="text-4xl font-bold text-pink-600 mb-6 text-center" >
                    Buy Flowers to your GF
                </AnimatedShinyText>
                <div className="bg-white border border-gray-200 rounded-3xl shadow-lg overflow-hidden">
                  {/* Flowers section (moved to top) */}
                  <div className="p-4 border-b border-gray-100">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-500">Flowers</span>
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-gray-500">0.001 ETH per flower</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 flex gap-2">
                        {[1, 2, 3, 4].map((flowerCount) => (
                          <button
                            key={flowerCount}
                            onClick={() => setSelectedFlowers(flowerCount)}
                            className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                              flowerCount <= selectedFlowers
                                ? 'bg-pink-500 text-white'
                                : 'bg-gray-100 text-gray-400'
                            }`}
                          >
                            🌸
                          </button>
                        ))}
                      </div>
                      <Button variant="ghost" className="rounded-full h-10 gap-1 bg-gray-100 hover:bg-gray-200 font-medium">
                        <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-white text-xs">
                          <Image
                            src="/ethereum-eth-logo.png"
                            alt="ETH"
                            width={16}
                            height={16}
                          />
                        </div>
                        ETH
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="text-sm text-gray-500 mt-1">{(selectedFlowers * 0.001).toFixed(3)} ETH (${selectedFlowers * 5})</div>
                  </div>

                  {/* Arrow button */}
                  <div className="relative h-0">
                    <Button
                      variant="secondary"
                      size="icon"
                      className="absolute left-1/2 top-0 transform -translate-x-1/2 -translate-y-1/2 rounded-full bg-white border border-gray-200 shadow-md z-10 h-10 w-10"
                    >
                      <Smile className="h-5 w-5" />
                    </Button>
                  </div>

                  {/* Sell section (moved to bottom) */}
                  <div className="p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-500">You get (KWAII)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Input
                        className="text-3xl font-medium border-none shadow-none p-0 h-auto focus-visible:ring-0"
                        placeholder="0"
                      />
                      <Button
                        variant="secondary"
                        className="rounded-full h-10 gap-1 bg-pink-100 hover:bg-pink-200 text-pink-600 font-medium"
                      >
                        Select token
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="text-sm text-gray-500 mt-1">$0</div>
                  </div>

                  {/* Action button */}
                  <div className="p-4 pt-0">
                    <Button className="w-full py-6 text-lg font-medium rounded-2xl bg-pink-500 hover:bg-pink-600" onClick={() => {
                      router.push("/chat")
                    }}>
                      Date
                    </Button>
                  </div>
                </div>

                <div className="text-center text-gray-500 text-sm mt-4">
                  Deposit assets to your GF wallet
                  <br />
                  she will make you richer or die trying
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CSS for floating animation */}
      <style jsx global>{`
        @keyframes float {
          0%, 100% {
            transform: translate(-50%, -50%) translateY(0px);
          }
          50% {
            transform: translate(-50%, -50%) translateY(20px);
          }
        }
      `}</style>
    </div>
  )
}