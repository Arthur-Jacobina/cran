'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useRouter } from 'next/navigation';
import AnimatedShinyText from '@/components/ui/animated-shiny-text';
import { useEffect, useState } from 'react';
import Image from 'next/image';
import dynamic from 'next/dynamic';
import { useAccount } from 'wagmi';
import { signIn, useSession } from 'next-auth/react';
import { SiweMessage } from 'siwe';
import { useSignMessage } from 'wagmi';

// Import HeartParticles with SSR disabled
const HeartParticles = dynamic(
  () => import('@/components/ui/heart-particles'),
  { ssr: false }
);

export default function Login() {
  const router = useRouter();
  const { address, isConnected } = useAccount();
  const { signMessageAsync } = useSignMessage();
  const { data: session } = useSession();
  const [waifuImage, setWaifuImage] = useState<string>(
    './placeholder-avatar.jpg',
  );
  const [isRegistered, setIsRegistered] = useState<boolean>(false);
  // Remove states related to inline registration form
  const [error, setError] = useState<string>('');

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

  useEffect(() => {
    if (session?.address) {
      router.push('/chat');
    }
  }, [session, router]);

  // Check if user is registered when address changes
  useEffect(() => {
    if (address) {
      checkUserRegistration();
    }
  }, [address]);

  const checkUserRegistration = async () => {
    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/${address}`);
        const data = await response.json();
        console.log(data);
        if (response.status === 404 || response.status === 500) {
          setIsRegistered(false);
        } else {
          setIsRegistered(true);
        }
    } catch (error) {
      console.error('Error checking registration:', error);
      setIsRegistered(false);
    }
  };

  const handleAuth = async () => {
    try {
      if (!isRegistered) {
        router.push('/register');
        return;
      }
      
      // Get nonce as plain text
      const nonceRes = await fetch('/api/auth/nonce');
      if (!nonceRes.ok) throw new Error('Failed to get nonce');
      const nonce = await nonceRes.text();

      const message = new SiweMessage({
        domain: window.location.host,
        address: address,
        statement: "Sign in with Ethereum to Cranberry",
        uri: window.location.origin,
        version: '1',
        chainId: 1,
        nonce: nonce
      });

      const signature = await signMessageAsync({
        message: message.prepareMessage(),
      });

      const response = await signIn('credentials', {
        message: JSON.stringify(message),
        signature,
        redirect: false,
      });

      if (response?.error) {
        console.error('Error signing in:', response.error);
      } else {
        router.push('/chat');
      }
    } catch (error) {
      console.error('Error during authentication:', error);
    }
  };

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
            
            {!isConnected && (
              <>
                <p className="text-gray-600 mb-6 text-center">
                  Connect your wallet to start chatting with Cran!
                </p>
                <div className="flex justify-center">
                  <ConnectButton />
                </div>
              </>
            )}

            {/* Registration form removed as we're now redirecting to /register */}

            {isConnected && (
              <>
                <p className="text-gray-600 mb-6 text-center">
                  {isRegistered 
                    ? 'Sign in to continue to your account' 
                    : 'You need to register before signing in'}
                </p>
                <div className="flex flex-col items-center gap-4">
                  {isRegistered ? (
                    <button
                      onClick={handleAuth}
                      className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                    >
                      Sign In with Ethereum
                    </button>
                  ) : (
                    <button
                      onClick={() => router.push('/register')}
                      className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors"
                    >
                      Register Account
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Right column - Waifu image */}
      <div className="w-1/2 h-screen relative">
        <div className="relative w-full h-full rounded-2xl overflow-hidden">
          <Image
            src={waifuImage}
            alt="Cran AI Avatar"
            className="object-cover"
            fill
            priority
            unoptimized
          />
        </div>
      </div>
    </div>
  );
}