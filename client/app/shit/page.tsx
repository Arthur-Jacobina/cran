'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { AudioRecorder } from '@/components/AudioRecorder';
import { ImageIcon, MicIcon, SendIcon } from 'lucide-react';

export default function Chat() {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [files, setFiles] = useState<FileList | undefined>(undefined);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (input.trim() || files) {
      setIsTyping(true);
      // Handle submission logic here
      console.log('Submitting:', input, files);
      setInput('');
      setFiles(undefined);
      if (fileInputRef.current) fileInputRef.current.value = '';
      if (audioInputRef.current) audioInputRef.current.value = '';
      // Simulate typing completion after 2 seconds
      setTimeout(() => setIsTyping(false), 2000);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(event.target.files);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-blue-100 to-blue-200">
      <div className="absolute inset-0 bg-[url('/placeholder.svg?height=100&width=100')] opacity-5 bg-repeat"></div>
      <Card className="w-full max-w-2xl shadow-xl border-blue-200">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-t-lg">
          <CardTitle className="text-center text-xl font-bold">
            AI Chat Assistant
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[60vh] overflow-y-auto p-6 bg-white">
          {/* Chat messages would go here */}
          <div className="flex flex-col space-y-4">
            <div className="self-end">
              <span className="inline-block p-3 rounded-lg bg-blue-500 text-white max-w-xs">
                Hello! How can I help you today?
              </span>
            </div>
            <div className="self-start">
              <span className="inline-block p-3 rounded-lg bg-gray-200 text-gray-800 max-w-xs">
                I'm your AI assistant. You can send me text, images, or audio
                messages.
              </span>
            </div>
          </div>
          {isTyping && (
            <div className="mt-4 self-start">
              <span className="inline-block p-2 rounded-lg bg-gray-200 text-gray-800">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                </div>
              </span>
            </div>
          )}
        </CardContent>
        <CardFooter className="p-4 bg-blue-50">
          <form onSubmit={onSubmit} className="flex w-full space-x-2">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Type your message here..."
              className="flex-grow border-blue-200 focus:border-blue-500 focus:ring-blue-500"
            />
            <input
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              ref={fileInputRef}
              className="hidden"
            />
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileUpload}
              ref={audioInputRef}
              className="hidden"
            />
            <Button
              type="button"
              variant="outline"
              className="bg-blue-100 border-blue-300 hover:bg-blue-200 text-blue-700"
              onClick={() => fileInputRef.current?.click()}
            >
              <ImageIcon className="w-4 h-4" />
            </Button>
            <AudioRecorder />
            <Button
              type="submit"
              disabled={isTyping}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <SendIcon className="w-4 h-4" />
            </Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}
