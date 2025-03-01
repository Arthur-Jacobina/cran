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
  const [isLoading, setIsLoading] = useState(true);
  const [roleText, setRoleText] = useState('');
  const roles = [
    'Girlfriend',
    'GPU Enthusiast',
    'Hyperbolic Dealer',
    'Crypto memeologist',
    '(Not so)Professional Trader',
    'Sometimes a singer',
    'Onchain personal stylist',
  ];
  const [currentRoleIndex, setCurrentRoleIndex] = useState(0);

  useEffect(() => {
    getWaifuImage().then((url) => {
      if (url) {
        setImageUrl(url);
        setIsLoading(false);
      }
    });
  }, []);

  useEffect(() => {
    let currentText = '';
    let currentIndex = 0;
    let isDeleting = false;
    let timeout: NodeJS.Timeout;

    const type = () => {
      const currentRole = roles[currentRoleIndex];

      if (isDeleting) {
        currentText = currentRole.substring(0, currentIndex - 1);
        currentIndex--;
      } else {
        currentText = currentRole.substring(0, currentIndex + 1);
        currentIndex++;
      }

      setRoleText(currentText);

      let typeSpeed = isDeleting ? 50 : 100;

      if (!isDeleting && currentIndex === currentRole.length) {
        // Pause at the end of typing
        typeSpeed = 2000;
        isDeleting = true;
      } else if (isDeleting && currentIndex === 0) {
        isDeleting = false;
        setCurrentRoleIndex((prev) => (prev + 1) % roles.length);
        typeSpeed = 500;
      }

      timeout = setTimeout(type, typeSpeed);
    };

    type();
    return () => clearTimeout(timeout);
  }, [currentRoleIndex]);

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100 overflow-y-hidden">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-12">
          {/* Left column with image */}
          <div className="w-full md:w-1/2">
            <div className="relative max-w-[500px] mx-auto">
              <div className="relative w-full pt-[150%] rounded-2xl">
                <div className="absolute inset-0 rounded-2xl bg-blue-500/20 blur-xl animate-pulse" />
                {isLoading ? (
                  <div className="absolute inset-0 rounded-2xl bg-gray-200 animate-pulse" />
                ) : (
                  <Image
                    src="/4.jpeg"
                    alt="Cran AI Avatar"
                    className="absolute inset-0 rounded-2xl shadow-xl object-cover w-full h-[80%]"
                    fill
                    priority
                    unoptimized
                  />
                )}
              </div>
            </div>
          </div>

          {/* Right column with text and button */}
          <div className="w-full md:w-1/2 flex flex-col text-center items-center md:text-left">
            <AnimatedShinyText className="text-4xl md:text-5xl font-bold mb-6">
              Say Hi to Cran!
            </AnimatedShinyText>
            <p className="text-neutral-600 text-lg mb-8">
              She is here to be your AI{' '}
              <span className="text-blue-500">{roleText}</span>
              <span className="inline-block w-0.5 h-5 ml-1 bg-blue-500 items-center justify-center animate-blink"></span>
            </p>
            <Button
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold"
              onClick={() => router.push('/login')}
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
