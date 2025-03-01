import { NextResponse } from 'next/server';
import { ElevenLabsClient } from 'elevenlabs';
import { Readable } from 'stream';

const client = new ElevenLabsClient({
  apiKey: process.env.NEXT_PUBLIC_ELEVEN_LABS_API_KEY!,
});

export async function POST(request: Request) {
  try {
    const { text } = await request.json();

    const audio = await client.textToSpeech.convert('eVItLK1UvXctxuaRV2Oq', {
      model_id: 'eleven_multilingual_v2',
      text,
      output_format: 'mp3_44100_128',
      voice_settings: {
        stability: 0,
        similarity_boost: 0,
        use_speaker_boost: true,
        speed: 1.0,
      },
    });

    // Convert Readable to Blob
    const chunks: Buffer[] = [];
    const readable = audio as Readable;
    for await (const chunk of readable) {
      chunks.push(Buffer.from(chunk));
    }
    const audioBlob = new Blob(chunks, { type: 'audio/mpeg' });

    return new NextResponse(audioBlob, {
      headers: {
        'Content-Type': 'audio/mpeg',
      },
    });
  } catch (error) {
    console.error('Error generating audio:', error);
    return NextResponse.json({ error: 'Failed to generate audio' }, { status: 500 });
  }
} 