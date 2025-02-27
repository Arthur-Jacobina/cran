'use client';

import { useState, useRef, useEffect } from 'react';
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
import { ImageIcon, SendIcon, TrashIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { AudioVisualizer } from '@/components/AudioVisualizer';

async function getWaifuImage() {
    try {
      const response = await fetch('/api/waifu');
      const data = await response.json();
      return data.imageUrl;
    } catch (error) {
      console.error('Error fetching image:', error);
      return '/placeholder-avatar.jpg';
    }
  }

interface FlipCardProps {
  imageUrl: string;
  alt: string;
  prompt: string;
}

const FlipCard = ({ imageUrl, alt, prompt }: FlipCardProps) => {
  const [isFlipped, setIsFlipped] = useState(false);

  return (
    <div
      className="relative w-full h-28 cursor-pointer"
      onClick={() => setIsFlipped(!isFlipped)}
    >
      <AnimatePresence initial={false} mode="wait">
        {!isFlipped ? (
          <motion.div
            key="front"
            className="absolute w-full h-full"
            initial={{ rotateY: 180 }}
            animate={{ rotateY: 0 }}
            exit={{ rotateY: 180 }}
            transition={{ duration: 0.3 }}
            style={{ backfaceVisibility: 'hidden' }}
          >
            <img
              src={imageUrl}
              alt={alt}
              className="w-full h-full object-cover rounded-lg"
            />
          </motion.div>
        ) : (
          <motion.div
            key="back"
            className="absolute w-full h-full bg-white p-2 rounded-lg shadow-md"
            initial={{ rotateY: -180 }}
            animate={{ rotateY: 0 }}
            exit={{ rotateY: -180 }}
            transition={{ duration: 0.3 }}
            style={{ backfaceVisibility: 'hidden' }}
          >
            <p className="text-xs text-gray-600 overflow-auto h-full">
              {prompt}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default function Chat() {
  const [isTyping, setIsTyping] = useState(false);
  const [files, setFiles] = useState<FileList | undefined>(undefined);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);
  const [imageUrl, setImageUrl] = useState('/placeholder-avatar.jpg');
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioData, setAudioData] = useState<number[]>(new Array(16).fill(128));
  const audioRecorderRef = useRef<{ stopAndReset: () => void }>(null);

  useEffect(() => {
    getWaifuImage().then(url => {
      if (url) setImageUrl(url);
    });
  }, []);

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // If recording is active, stop it
    if (isRecording && audioRecorderRef.current) {
      audioRecorderRef.current.stopAndReset();
      setIsRecording(false);
    }
    
    setIsTyping(false);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(event.target.files);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);
    setIsTyping(value.length > 0);
  };

  const handleStopRecording = () => {
    if (audioRecorderRef.current) {
      audioRecorderRef.current.stopAndReset();
    }
    setIsRecording(false);
  };

  console.log(files);
  const gf_name = 'Cranberry';
  const gf_description = 'A cute and friendly AI girlfriend, who is a bit of a nerd and loves to talk about anime and manga.';

  const galleryCards = [
    {
      imageUrl: imageUrl,
      alt: "Gallery 1",
      prompt: "A stunning digital artwork of an anime-style character with vibrant cranberry-colored hair, wearing casual tech company attire, sitting in a modern office environment surrounded by multiple computer screens displaying code."
    },
    {
      imageUrl: imageUrl,
      alt: "Gallery 2",
      prompt: "An illustration of a cheerful anime girl in a cozy room, surrounded by manga volumes and programming books, with a soft evening light streaming through the window."
    },
    {
      imageUrl: imageUrl,
      alt: "Gallery 3",
      prompt: "A detailed portrait of an anime-style software engineer with distinctive cranberry hair, wearing smart casual clothes, holding a coffee mug with coding stickers, against a background of cherry blossoms."
    }
  ];

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="container px-4 mx-auto">
        <div className="flex flex-col lg:flex-row gap-4 justify-center items-start">
          <Card className="w-full max-w-2xl">
            <CardHeader className="flex flex-row items-center gap-4">
              <div 
                className="w-12 h-12 rounded-full overflow-hidden cursor-pointer"
                onClick={() => setIsOverlayOpen(true)}
              >
                <img
                  src={imageUrl}
                  alt={`${gf_name}'s avatar`}
                  className="w-full h-full object-cover"
                />
              </div>
              <CardTitle>{gf_name}</CardTitle>
            </CardHeader>

            <AnimatePresence>
              {isOverlayOpen && (
                <motion.div 
                  className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center"
                  onClick={() => setIsOverlayOpen(false)}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <motion.div 
                    className="relative max-w-xl w-full m-4 bg-white rounded-lg shadow-2xl overflow-hidden"
                    onClick={(e) => e.stopPropagation()}
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.9, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <img
                      src={imageUrl}
                      alt={`${gf_name}'s avatar`}
                      className="w-full h-auto object-contain rounded-lg"
                    />
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>

            <CardContent className="h-[60vh] overflow-y-auto">
              {/* Chat messages would go here */}
            </CardContent>
            <CardFooter>
              <form onSubmit={onSubmit} className="flex w-full space-x-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  onChange={handleFileUpload}
                  accept="image/*"
                />
                
                {!isRecording ? (
                  <Input
                    value={input}
                    onChange={handleInputChange}
                    placeholder="Type your message..."
                    className="flex-grow rounded-full focus-visible:ring-0 focus-visible:ring-offset-0"
                  />
                ) : (
                  <div className="flex-grow bg-gray-100 rounded-full px-4 py-2 flex items-center">
                    <AudioVisualizer audioData={audioData} />
                  </div>
                )}
                <AnimatePresence mode="wait" initial={false}>
                  {!isRecording ? (
                    <motion.div
                      key="typing-controls"
                      className="flex gap-2"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.15 }}
                    >
                      <AnimatePresence mode="wait">
                        {isTyping ? (
                          <motion.div
                            key="send-button"
                            initial={{ opacity: 0, scale: 0.8, width: 0 }}
                            animate={{ opacity: 1, scale: 1, width: 'auto' }}
                            exit={{ opacity: 0, scale: 0.8, width: 0 }}
                            transition={{ duration: 0.15 }}
                          >
                            <Button type="submit" className="bg-blue-500 text-white hover:bg-blue-600">
                              <SendIcon className="w-4 h-4" />
                            </Button>
                          </motion.div>
                        ) : (
                          <motion.div 
                            key="inactive-buttons"
                            className="flex gap-2"
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.8 }}
                            transition={{ duration: 0.15 }}
                          >
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => fileInputRef.current?.click()}
                            >
                              <ImageIcon className="w-4 h-4 text-blue-500" />
                            </Button>
                            <AudioRecorder 
                              onRecordingChange={setIsRecording} 
                              onAudioData={setAudioData}
                              ref={audioRecorderRef}
                            />
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="recording-controls"
                      className="flex gap-2"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.15 }}
                    >
                      <Button 
                        type="button" 
                        variant="outline"
                        onClick={handleStopRecording}
                        className="bg-white text-red-500 hover:bg-gray-100"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </Button>
                      <Button 
                        type="submit" 
                        className="bg-blue-500 text-white hover:bg-blue-600"
                      >
                        <SendIcon className="w-4 h-4" />
                      </Button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </form>
            </CardFooter>
          </Card>
          
          <div className="flex flex-col gap-4 w-full max-w-md">
            <Card className="w-full">
              <CardHeader>
                <CardTitle>Bio</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600 text-justify">
                    {gf_description}
                  </p>
                  <h1 className="text-md font-semibold">Gallery</h1>
                  <div className="grid grid-cols-3 gap-2">
                    {galleryCards.map((card, index) => (
                      <FlipCard
                        key={index}
                        imageUrl={card.imageUrl}
                        alt={card.alt}
                        prompt={card.prompt}
                      />
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="w-full">
              <CardHeader>
                <CardTitle>System Logs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <h2 className="text-sm font-semibold mb-2">Memory Log</h2>
                    <div className="text-xs text-gray-600 max-h-24 overflow-y-auto">
                      <pre className="whitespace-pre-wrap">
                        Last conversation: Discussed anime recommendations
                        Core memory: Loves Sousou no Frieren
                        Recent context: Technical discussion about React
                      </pre>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <h2 className="text-sm font-semibold mb-2">Execution Flow</h2>
                    <div className="text-xs text-gray-600 max-h-24 overflow-y-auto">
                      <pre className="whitespace-pre-wrap">
                        → Processing user input
                        → Accessing memory context
                        → Generating response
                        → Updating conversation history
                      </pre>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}