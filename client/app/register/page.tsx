'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import HyperText from '@/components/ui/hyper-text'

interface FormData {
  name: string
  twitter: string
  preferences: {
    looks: boolean
    personality: boolean
    justGirl: boolean
    neutral: boolean
    techSavvy: boolean
    romantic: boolean
    animeVibes: boolean
  }
  selectedWaifus: string[]
}

export default function RegisterPage() {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState<FormData>({
    name: '',
    twitter: '',
    preferences: {
      looks: false,
      personality: false,
      justGirl: false,
      neutral: false,
      techSavvy: false,
      romantic: false,
      animeVibes: false,
    },
    selectedWaifus: [],
  })
  const [waifuImages, setWaifuImages] = useState<string[]>([])

  async function getWaifuImage() {
    try {
      const response = await fetch('/api/waifu');
      const data = await response.json();
      return data.imageUrl;
    } catch (error) {
      console.error('Error fetching image:', error);
      return '/placeholder-avatar.jpg';
    }
  }

  useEffect(() => {
    const fetchWaifus = async () => {
      const images = []
      for (let i = 0; i < 15; i++) {
        const response = await fetch('/api/waifu')
        const data = await response.json()
        images.push(data.imageUrl)
      }
      setWaifuImages(images)
    }
    fetchWaifus()
  }, [])

  const handleBasicInfoSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.name && formData.twitter) {
      setStep(2)
    }
  }

  const handlePreferencesSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const hasSelection = Object.values(formData.preferences).some(value => value)
    if (hasSelection) {
      setStep(3)
    }
  }

  const handleWaifuSelection = (imageUrl: string) => {
    setFormData(prev => ({
      ...prev,
      selectedWaifus: prev.selectedWaifus.includes(imageUrl)
        ? prev.selectedWaifus.filter(url => url !== imageUrl)
        : [...prev.selectedWaifus, imageUrl]
    }))
  }

  const handleFinalSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.selectedWaifus.length >= 3) {
      console.log('Form submitted:', formData)
    }
  }

  const togglePreference = (key: keyof typeof formData.preferences) => {
    setFormData(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: !prev.preferences[key]
      }
    }))
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <div className="flex justify-end mb-8">
        <div className="flex space-x-2">
          {[1, 2, 3].map((stepNum) => (
            <div
              key={stepNum}
              className={`w-3 h-3 rounded-full ${
                stepNum <= step ? 'bg-blue-500' : 'bg-gray-500'
              }`}
            />
          ))}
        </div>
      </div>

      {step === 1 && (
        <form onSubmit={handleBasicInfoSubmit} className="space-y-4">
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="invisible"
              disabled={true}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <HyperText className="text-2xl font-bold text-blue-500" text="Basic Information" />
            <button
              type="submit"
              disabled={!formData.name || !formData.twitter}
              className="border-2 border-blue-500 text-white px-3 py-1 rounded-full bg-blue-500 text-sm hover:bg-blue-600 disabled:border-gray-400 disabled:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-transparent"
            >
              Next
            </button>
          </div>
          <div>
            <label className="block mb-2 text-gray-500 text-md">Username:</label>
            <input
              type="text"
              value={formData.name}
              placeholder="Username, e.g. Cranberry"
              onChange={e => setFormData({...formData, name: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block mb-2 text-gray-500 text-md">X Handle:</label>
            <input
              type="text"
              value={formData.twitter}
              placeholder="X Handle, e.g. @Cranberry"
              onChange={e => setFormData({...formData, twitter: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          </div>
        </form>
      )}

{step === 2 && (
        <form onSubmit={handlePreferencesSubmit} className="space-y-6">
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="text-blue-500 hover:text-blue-600"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <HyperText className="text-2xl font-bold text-blue-500" text="Your Ideal AI Waifu" />
            <button
              type="submit"
              disabled={!Object.values(formData.preferences).some(value => value)}
              className="border-2 border-blue-500 text-white px-3 py-1 rounded-full bg-blue-500 text-sm hover:bg-blue-600 disabled:border-gray-400 disabled:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-transparent"
            >
              Next
            </button>
          </div>

          <div className="space-y-4">
            <h3 className="text-gray-500">What matters most in your AI girlfriend? (Select one or more)</h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { key: 'looks', label: 'Stunning Looks' },
                { key: 'personality', label: 'Great Personality' },
                { key: 'techSavvy', label: 'Tech-Savvy' },
                { key: 'romantic', label: 'Hopeless Romantic' },
                { key: 'animeVibes', label: 'Anime Vibes' },
                { key: 'justGirl', label: 'Just a Girl' },
                { key: 'rosie', label: 'Rosie' },
                {key: "cranberry", label: "Cranberry"}
              ].map(({ key, label }) => (
                <div
                  key={key}
                  onClick={() => togglePreference(key as keyof typeof formData.preferences)}
                  className={`p-3 border-2 border-blue-500 rounded-lg cursor-pointer text-center transition-colors ${
                    formData.preferences[key as keyof typeof formData.preferences]
                      ? 'bg-blue-500 text-white'
                      : 'bg-transparent text-blue-500 hover:bg-blue-100'
                  }`}
                >
                  {label}
                </div>
              ))}
            </div>
          </div>
        </form>
      )}


      {step === 3 && (
        <form onSubmit={handleFinalSubmit} className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="text-blue-500 hover:text-blue-600"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <HyperText className="text-2xl font-bold text-blue-500" text="Choose Your Favorite Waifus" />
            <button
              type="submit"
              disabled={formData.selectedWaifus.length < 3}
              className="border-2 border-blue-500 text-white px-3 py-1 rounded-full bg-blue-500 text-sm hover:bg-blue-600 disabled:border-gray-400 disabled:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-transparent"
            >
              Submit
            </button>
          </div>
          <p className="mb-4 text-gray-500">Select at least 3 favorites:</p>
          <div className="h-[calc(100vh-300px)] overflow-y-auto overflow-x-hidden">
            <div className="grid grid-cols-3 gap-4">
              {waifuImages.map((url, index) => (
                <div
                  key={index}
                  className={`relative cursor-pointer border-4 rounded-2xl overflow-hidden ${
                    formData.selectedWaifus.includes(url) ? 'border-blue-500' : 'border-transparent'
                  }`}
                  onClick={() => handleWaifuSelection(url)}
                >
                  <div className="relative w-full pt-[150%]">
                    {/* Using img tag instead of Next.js Image to avoid domain configuration issues */}
                    <img
                      src={url}
                      alt={`Waifu ${index + 1}`}
                      className="absolute inset-0 w-full h-full object-cover"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </form>
      )}
    </div>
  )
}