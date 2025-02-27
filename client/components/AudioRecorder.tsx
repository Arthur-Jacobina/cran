'use client';

import { Button } from '@/components/ui/button';
import { MicIcon } from 'lucide-react';
import { useAudioRecorder } from '@/hooks/use-audio';

export const AudioRecorder = () => {
  const handleUpload = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.mp3');

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        console.log('Audio uploaded successfully');
      } else {
        console.error('Upload failed:', response.statusText);
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  const { isRecording, toggleRecording } = useAudioRecorder(handleUpload);

  return (
    <Button variant="outline" size="icon" onClick={toggleRecording}>
      <MicIcon
        className={`h-4 w-4 ${isRecording ? 'text-red-500 animate-pulse' : ''}`}
      />
      <span className="sr-only">
        {isRecording ? 'Stop' : 'Start'} recording
      </span>
    </Button>
  );
};
