import { NextResponse } from 'next/server';

async function getWaifuImage() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5); // 5 second timeout

    const response = await fetch(
      'https://api.waifu.im/search?included_tags=waifu&is_nsfw=false&height=<=1500',
    );

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.images[0]?.url || '/cran2.jpg';
  } catch (error) {
    console.error('Error fetching waifu image:', error);
    return '/cran2.jpg';
  }
}

export async function GET() {
  const imageUrl = await getWaifuImage();
  return NextResponse.json({ imageUrl });
}
