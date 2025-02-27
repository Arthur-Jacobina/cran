import { NextRequest, NextResponse } from 'next/server';
import { writeFile, unlink } from 'fs/promises';
import path from 'path';
import fs from 'fs';
import OpenAI from 'openai';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as Blob | null;

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    // Ensure uploads directory exists
    const uploadsDir = path.join(process.cwd(), 'public/uploads');
    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir, { recursive: true });
    }

    // Save file to a temporary path
    const buffer = Buffer.from(await file.arrayBuffer());
    const tempFilePath = path.join(
      process.cwd(),
      'public/uploads',
      'temp_recording.mp3',
    );

    await writeFile(tempFilePath, buffer);

    // Send file to OpenAI for transcription
    const transcription = await openai.audio.transcriptions.create({
      file: fs.createReadStream(tempFilePath),
      model: 'whisper-1',
    });

    console.log(transcription.text);

    // Delete the temp file after processing
    await unlink(tempFilePath);

    return NextResponse.json({
      message: 'Transcription successful',
      text: transcription.text,
    });

    //aqui eu vou chamar a api do nosso agent
    //com o text de input
  } catch (error) {
    console.error('Upload or transcription error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 },
    );
  }
}
