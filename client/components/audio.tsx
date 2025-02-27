'use client';

import React, { useState, useRef } from 'react';
import { Button } from './ui/button';
import { MicIcon } from 'lucide-react';

const [isRecording, setIsRecording] = useState(false);
const mediaRecorderRef = useRef<MediaRecorder | null>(null);
const audioChunksRef = useRef<Blob[]>([]);

const startRecording = async () => {
  audioChunksRef.current = [];

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);

    mediaRecorderRef.current = mediaRecorder;

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };
    mediaRecorder.start();
    setIsRecording(true);
  } catch (error) {
    console.error('Error accessing microphone:', error);
    alert('Could not access your microphone. Please check permissions.');
  }
};

const stopRecording = () => {
  if (!mediaRecorderRef.current) return;

  mediaRecorderRef.current.onstop = async () => {
    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mp3' });
    if (mediaRecorderRef.current != null) {
      mediaRecorderRef.current.stream
        .getTracks()
        .forEach((track) => track.stop());
    } else {
      console.log('Error!');
    }
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.mp3');

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        console.log('File uploaded successfully!');
      } else {
        console.error('File upload failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  mediaRecorderRef.current.stop();
  setIsRecording(false);
};

const toggleRecording = () => {
  if (isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
};

const AudioRecording: React.FC<{}> = ({}) => {
  return (
    <Button type="button" variant="outline" onClick={() => toggleRecording()}>
      <MicIcon className="w-4 h-4" />
    </Button>
  );
};

export default AudioRecording;

// export async function handleRecording(){
//     const options = { mimeType: "video/webm"}
//     const stream = await navigator
//     .mediaDevices
//     .getUserMedia({audio : true})
//     .then((audioStream) => {
//         const mediaRecorder = new MediaRecorder(audioStream);
//         mediaRecorder.addEventListener('click', function (){
//             try{
//                 mediaRecorder.start();
//                 console.log('recording started!')
//             }catch(e){
//                 console.log(e);
//             }
//         })
//     }).catch((error) => {
//         console.error(`Error when capturing user audio ${error}`);
//         });
// }
