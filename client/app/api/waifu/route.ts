import { NextResponse } from 'next/server';

async function getWaifuImage() {
  try {
    const response = await fetch(
      'https://api.waifu.im/search?included_tags=waifu&is_nsfw=false&height=<=1500',
    );
    const data = await response.json();
    return data.images[0]?.url;
  } catch (error) {
    console.error('Error fetching image:', error);
    return '/placeholder-avatar.jpg';
  }
}

export async function GET() {
  const imageUrl = await getWaifuImage();
  return NextResponse.json({ imageUrl });
}
