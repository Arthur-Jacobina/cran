'use client';

import { Button } from '@/components/ui/button';
import AnimatedShinyText from '@/components/ui/animated-shiny-text';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import HyperText from '@/components/ui/hyper-text';
import { useRouter } from 'next/navigation';

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

export default function Home() {
  const router = useRouter();
  const [imageUrl, setImageUrl] = useState('/placeholder-avatar.jpg');

  useEffect(() => {
    getWaifuImage().then(url => {
      if (url) setImageUrl(url);
    });
  }, []);

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100 overflow-y-hidden">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-12">
          {/* Left column with image */}
          <div className="w-full md:w-1/2">
            <div className="relative aspect-square max-w-[500px] mx-auto">
              <div className="absolute inset-0 rounded-2xl bg-blue-500/20 blur-xl animate-pulse" />
              <Image
                src={imageUrl}
                alt="Cran AI Avatar"
                className="relative rounded-2xl shadow-xl object-cover w-full h-full"
                style={{ objectFit: 'cover', objectPosition: 'center' }}
                fill
                priority
                unoptimized
              />
            </div>
          </div>

          {/* Right column with text and button */}
          <div className="w-full md:w-1/2 flex flex-col text-center items-center md:text-left">
            <AnimatedShinyText className="text-4xl md:text-5xl font-bold mb-6">
              Say Hi to Cran!
            </AnimatedShinyText>
            <p className="text-neutral-600 text-lg mb-8">
              She is here to be your AI Girlfriend.
            </p>
            <Button
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold"
              onClick={() => router.push('/chat')}
            >
              <HyperText
                className="text-lg font-bold text-white"
                text="Get Started"
              />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
