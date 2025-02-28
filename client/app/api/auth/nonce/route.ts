import { generateNonce } from 'siwe';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const nonce = generateNonce();
    return new NextResponse(nonce);
  } catch (error) {
    console.error('Error generating nonce:', error);
    return new NextResponse('Failed to generate nonce', { status: 500 });
  }
} 