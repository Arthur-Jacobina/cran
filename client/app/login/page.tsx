'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useRouter } from 'next/navigation';
import AnimatedShinyText from '@/components/ui/animated-shiny-text';
import { useEffect, useState } from 'react';
import Image from 'next/image';
import dynamic from 'next/dynamic';

// Import HeartParticles with SSR disabled
const HeartParticles = dynamic(
  () => import('@/components/ui/heart-particles'),
  { ssr: false }
);

export default function Login() {
  const router = useRouter();
  const [waifuImage, setWaifuImage] = useState<string>(
    './placeholder-avatar.jpg',
  );

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
    getWaifuImage().then((url) => {
      if (url) setWaifuImage(url);
    });
  }, []);

  return (
    <div className="flex h-screen">
      {/* Left column - Login content */}
      <div className="w-1/2 flex items-center justify-center bg-gray-100 relative">
        <HeartParticles />
        <div className="container z-10 mx-auto px-4">
          <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
            <AnimatedShinyText className="text-2xl font-bold mb-6 text-center">
              Welcome to Cranberry
            </AnimatedShinyText>
            <p className="text-gray-600 mb-6 text-center">
              Connect your wallet to get started
            </p>
            <div className="flex flex-col items-center gap-6">
              <ConnectButton />
            </div>
          </div>
        </div>
      </div>

      {/* Right column - Waifu image */}
      <div className="w-1/2 h-screen relative">
        <Image
          src={waifuImage}
          alt="Cran AI Avatar"
          className="relative rounded-2xl shadow-xl object-cover w-full h-full"
          style={{ objectFit: 'cover', objectPosition: 'center' }}
          fill
          priority
          unoptimized
        />
      </div>
    </div>
  );
}
