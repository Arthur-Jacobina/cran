// hooks/use-audio.ts

import { useState, useRef, useCallback } from 'react';

type UploadHandler = (blob: Blob) => Promise<void>;

interface UseAudioRecorderReturn {
  isRecording: boolean;
  toggleRecording: () => void;
  audioBlob: Blob | null;
}

export function useAudioRecorder(
  onUpload?: UploadHandler,
): UseAudioRecorderReturn {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      // Reset chunks
      chunksRef.current = [];

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create media recorder
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      // Set up event handlers
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Combine chunks into a single blob
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());

        // Upload if handler provided
        if (onUpload && audioBlob.size > 0) {
          await onUpload(audioBlob);
        }
      };

      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      setIsRecording(false);
    }
  }, [onUpload]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  return {
    isRecording,
    toggleRecording,
    audioBlob,
  };
}
