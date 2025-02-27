"use client";
import { useState, useRef } from "react";
import { MicIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function AudioButton() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  async function handleRecording() {
    if (isRecording) {
      // Stop recording
      mediaRecorder.current?.stop();
      setIsRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorder.current = new MediaRecorder(stream, { mimeType: "audio/webm" });
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/webm" });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  }

  return (
    <div className="p-4">
      <Button type="button" variant="outline" onClick={handleRecording}>
        <MicIcon className="w-4 h-4" />
        {isRecording ? "Stop Recording" : "Start Recording"}
      </Button>

      {audioURL && (
        <div className="mt-4">
          <audio controls src={audioURL}></audio>
          <a href={audioURL} download="recorded_audio.webm" className="block mt-2 text-blue-500 underline">
            Download Audio
          </a>
        </div>
      )}
    </div>
  );
}
