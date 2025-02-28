'use client';

import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import Header from '@/components/header';
import { getDefaultWallets, RainbowKitProvider } from '@rainbow-me/rainbowkit';
import { WagmiProvider } from 'wagmi';
import { mainnet, sepolia } from 'wagmi/chains';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@rainbow-me/rainbowkit/styles.css';
import { createConfig } from 'wagmi';
import { http } from 'wagmi';
import { SessionProvider } from 'next-auth/react';
import { useSession, signOut } from 'next-auth/react';
import { useAccount } from 'wagmi';
import { useEffect } from 'react';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

const { connectors, wallets } = getDefaultWallets({
  appName: 'Cranberry',
  projectId: process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID || '',
});

const config = createConfig({
  connectors,
  chains: [mainnet, sepolia],
  transports: {
    [mainnet.id]: http(),
    [sepolia.id]: http(),
  },
});

const queryClient = new QueryClient();

const SessionManager = () => {
  const { status } = useAccount();
  const { data: session } = useSession();
  
  // Handle wallet disconnection
  useEffect(() => {
    if (status === 'disconnected' && session) {
      signOut();
    }
  }, [status, session]);

  // Set session timeout
  useEffect(() => {
    if (!session) return; // Don't set timeout if there's no session
    
    const timeoutDuration = 60 * 60 * 1000; // 1 hour in milliseconds
    const timeout = setTimeout(() => {
      signOut();
    }, timeoutDuration);

    return () => clearTimeout(timeout);
  }, [session]);

  return null;
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <title>Cranberry</title>
        <meta name="description" content="Cranberry is your AI Girlfriend" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-100 h-screen overflow-y-hidden`}
      >
        <WagmiProvider config={config}>
          <QueryClientProvider client={queryClient}>
            <RainbowKitProvider>
              <SessionProvider>
                <SessionManager />
                <Header />
                {children}
              </SessionProvider>
            </RainbowKitProvider>
          </QueryClientProvider>
        </WagmiProvider>
      </body>
    </html>
  );
}
