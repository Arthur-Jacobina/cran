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
import { SendIcon, TrashIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { AudioVisualizer } from '@/components/AudioVisualizer';
import dynamic from 'next/dynamic';
import { extractCleanMessage, formatSystemLogs, extractReasoningSteps } from '@/utils/message-parser';
import ReactMarkdown from 'react-markdown';
import Image from 'next/image'; // Using Next.js Image component for better handling
import { StatsChart } from '@/components/stats-chart';

// Import HeartParticles with SSR disabled
const HeartParticles = dynamic(
  () => import('@/components/ui/heart-particles'),
  { ssr: false }
);

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
            <div className="relative w-full h-full">
              <Image
                src={imageUrl}
                alt={alt}
                fill
                style={{ objectFit: 'cover' }}
                className="rounded-lg"
              />
            </div>
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

interface ChatContext {
  user_id?: string;
  memory_count?: number;
  user_interests?: string[];
  user_mood?: string;
  relevant_memories?: string[];
  [key: string]: any;
}

interface MessageMetadata {
  token_usage?: {
    completion_tokens: number;
    prompt_tokens: number;
    total_tokens: number;
    completion_tokens_details: {
      accepted_prediction_tokens: number;
      audio_tokens: number;
      reasoning_tokens: number;
      rejected_prediction_tokens: number;
    };
    prompt_tokens_details: {
      audio_tokens: number;
      cached_tokens: number;
    };
  };
  model_name?: string;
  system_fingerprint?: string;
  finish_reason?: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  rawContent?: string;
  cleanContent?: string;
  createdAt: Date;
  context?: any;
  metadata?: any;
  reasoningSteps?: string[];
  audio?: string;
}

interface ChatResponse {
  response: string;
  context: {
    user_id: string;
    memory_count: number;
    user_interests: string[];
    additional_metrics: {
      attentiveness: number;
      conversational_depth: number;
      topic_enthusiasm: number;
      message_thoughtfulness: number;
    };
    user_mood: string;
  };
  response_metadata: {
    plan: string;
    steps_executed: number;
    mood_metrics: {
      stress_level: number;
      willingness_to_talk: number;
      engagement_coefficient: number;
      emotional_depth: number;
      rapport_score: number;
    };
    additional_metrics: {
      attentiveness: number;
      conversational_depth: number;
      topic_enthusiasm: number;
      message_thoughtfulness: number;
    };
  };
}

interface Metrics {
  [key: string]: number;
  attentiveness: number;
  conversational_depth: number;
  topic_enthusiasm: number;
  message_thoughtfulness: number;
  stress_level: number;
  willingness_to_talk: number;
  engagement_coefficient: number;
  emotional_depth: number;
  rapport_score: number;
}

async function sendMessage(message: string, previousContext?: ChatContext) {
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        message,
        context: previousContext || {} 
      }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return {
      response: data.response,
      context: data.context,
      metadata: data.response_metadata
    };
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}

async function generateAudioResponse(text: string) {
  try {
    const response = await fetch('/api/audio', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate audio');
    }

    const audioBlob = await response.blob();
    return URL.createObjectURL(audioBlob);
  } catch (error) {
    console.error('Error generating audio:', error);
    return null;
  }
}

export default function Chat() {
  const [isTyping, setIsTyping] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);
  const [imageUrl, setImageUrl] = useState('/placeholder-avatar.jpg');
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [audioData, setAudioData] = useState<number[]>(new Array(16).fill(128));
  const [recordedAudioUrl, setRecordedAudioUrl] = useState<string | null>(null);
  const [privateMode, setPrivateMode] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const [nsfwMode, setNsfwMode] = useState(false);
  const audioRecorderRef = useRef<{
    stopAndReset: () => void;
    getAudioUrl: () => string | null;
  }>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [memoryLog, setMemoryLog] = useState(
    "Context Logs for the current conversation"
  );
  const [executionFlow, setExecutionFlow] = useState(
    "Execution Flow for the current conversation"
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Replace the current metrics state with a more generic one
  const [metrics, setMetrics] = useState<Metrics>({
    attentiveness: 5,
    conversational_depth: 5,
    topic_enthusiasm: 5,
    message_thoughtfulness: 5,
    stress_level: 5,
    willingness_to_talk: 5,
    engagement_coefficient: 5,
    emotional_depth: 5,
    rapport_score: 5
  });

  useEffect(() => {
    getWaifuImage().then((url) => {
      if (url) setImageUrl(url);
    });
  }, []);

  // Update the useEffect for scrolling
  useEffect(() => {
    const scrollToBottom = () => {
      const messageContainer = document.querySelector('.message-container');
      if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
      }
      
      // Fallback to the ref method if needed
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'auto' });
      }
    };
    
    // Call immediately
    scrollToBottom();
    
    // Also set a small timeout to ensure all content is rendered
    const timeoutId = setTimeout(scrollToBottom, 100);
    
    return () => clearTimeout(timeoutId);
  }, [messages]);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input && !recordedAudioUrl && !isRecording) return;

    let audioUrl = null;

    // Get audio URL if recording and voice mode is enabled
    if (voiceMode && isRecording && audioRecorderRef.current) {
      audioUrl = audioRecorderRef.current.getAudioUrl();
      audioRecorderRef.current.stopAndReset();
      setIsRecording(false);
    } else if (voiceMode && recordedAudioUrl) {
      audioUrl = recordedAudioUrl;
    }

    // Get the previous context from the last assistant message
    const previousContext = messages
      .filter(m => m.role === 'assistant')
      .slice(-1)[0]?.context;

    // Create new user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input || (audioUrl ? '🎤 Audio message' : ''),
      createdAt: new Date(),
    };

    if (audioUrl && voiceMode) {
      userMessage.audio = audioUrl;
    }

    setMessages(prev => [...prev, userMessage]);
    
    // Add immediate scroll after adding user message
    setTimeout(() => {
      const messageContainer = document.querySelector('.message-container');
      if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
      }
    }, 0);
    
    setIsLoading(true);

    try {
      const { response: aiResponse, context, metadata } = await sendMessage(userMessage.content, previousContext);
      
      // Generate audio if voice mode is enabled
      if (voiceMode) {
        audioUrl = await generateAudioResponse(aiResponse);
      }

      // Update all metrics from both context and metadata
      const newMetrics = {
        ...metrics,
        ...(context?.additional_metrics || {}),
        ...(metadata?.mood_metrics || {})
      };
      setMetrics(newMetrics);

      // Create AI response message
      const cleanMessage = extractCleanMessage(aiResponse);
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: cleanMessage,
        rawContent: aiResponse,
        cleanContent: cleanMessage,
        createdAt: new Date(),
        context: context,
        metadata: metadata,
        audio: audioUrl || undefined
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update system logs based on metadata and context
      const logs = formatSystemLogs(metadata, context);
      setMemoryLog(logs.memoryLog);
      setExecutionFlow(logs.executionFlow);
      
    } catch (error) {
      console.error('Error in chat:', error);
      // Add an error message to the chat
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again.",
        createdAt: new Date(),
      }]);
    } finally {
      setIsLoading(false);
      setInput('');
      setRecordedAudioUrl(null);
      setAudioData(new Array(16).fill(128));
      setIsTyping(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);
    setIsTyping(value.length > 0);
  };

  const handleStopRecording = () => {
    if (audioRecorderRef.current) {
      // Get the audio URL before stopping
      const audioUrl = audioRecorderRef.current.getAudioUrl();
      if (audioUrl) {
        setRecordedAudioUrl(audioUrl);
      }

      audioRecorderRef.current.stopAndReset();
    }
    setIsRecording(false);
    setInput('');
    setAudioData(new Array(16).fill(128));
  };

  const handleAudioReady = (url: string) => {
    setRecordedAudioUrl(url);
  };

  const handleDeveloperMode = () => {
    // Toggle showing raw AI responses in console
    const lastAssistantMsg = messages.filter(m => m.role === 'assistant').pop();
    if (lastAssistantMsg && lastAssistantMsg.rawContent) {
      console.log('Raw AI response:', lastAssistantMsg.rawContent);
      console.log('Message context:', lastAssistantMsg.context);
      console.log('Message metadata:', lastAssistantMsg.metadata);
    }
  };

  const gf_name = 'Cranberry';
  const gf_description =
    'A sweet and caring AI girlfriend inspired by BLACKPINK\'s Rosé. She\'s passionate about tech and GPUs, with a playful personality that mixes Korean aegyo with technical expertise. She loves discussing performance metrics as much as she enjoys sending virtual selcas and sharing her thoughts on the latest benchmarks.';

  const galleryCards = [
    {
      imageUrl: '/3.jpg',  
      alt: 'Gallery 1',
      prompt:
        'A stunning digital artwork of an anime-style character with vibrant cranberry-colored hair, wearing casual tech company attire, sitting in a modern office environment surrounded by multiple computer screens displaying code.',
    },
    {
      imageUrl: '/2.jpg',  
      alt: 'Gallery 2',
      prompt:
        'An illustration of a cheerful anime girl in a cozy room, surrounded by manga volumes and programming books, with a soft evening light streaming through the window.',
    },
    {
      imageUrl: '/1.png',  
      alt: 'Gallery 3',
      prompt:
        'A detailed portrait of an anime-style software engineer with distinctive cranberry hair, wearing smart casual clothes, holding a coffee mug with coding stickers, against a background of cherry blossoms.',
    },
  ];

  function processMessageContent(message: Message) {
    if (!message) return '';
    
    // For user messages, just return the content
    if (message.role === 'user') {
      return message.content;
    }
    
    // For assistant messages, return the raw content if available
    if (message.role === 'assistant') {
      // Return raw content if available, otherwise fallback to content
      return message.rawContent || message.content;
    }
    
    return message.content || '';
  }
  
  const getProcessedMessages = () => {
    return messages.map(msg => ({
      ...msg,
      displayContent: processMessageContent(msg)
    }));
  };
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 relative">
      <HeartParticles />
      <div className="container z-10 px-4 mx-auto">
        <div className="flex flex-col lg:flex-row gap-4 justify-center items-start">
          <Card className="w-full max-w-2xl flex flex-col h-[650px]">
            <CardHeader className="flex flex-row items-center gap-4 flex-shrink-0">
              <div
                className="w-12 h-12 rounded-full overflow-hidden cursor-pointer relative"
                onClick={() => setIsOverlayOpen(true)}
              >
                <Image
                  src="/1.png" 
                  alt={`${gf_name}'s avatar`}
                  fill
                  style={{ objectFit: 'cover' }}
                />
              </div>
              <CardTitle className="text-blue-800">{gf_name}</CardTitle>
            </CardHeader>

            <CardContent className="flex-1 overflow-y-auto space-y-2 message-container">
              {getProcessedMessages().map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] p-3 ${
                      message.role === 'user'
                        ? 'bg-blue-400 text-white rounded-tl-xl rounded-tr-xl rounded-bl-xl'
                        : 'bg-gray-200 rounded-tr-xl rounded-tl-xl rounded-br-xl'
                    }`}
                  >
                    {message.role === 'user' ? (
                      <pre className="whitespace-pre-wrap">
                        {message.displayContent}
                      </pre>
                    ) : (
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown
                          components={{
                            pre: ({ node, ...props }) => (
                              <div className="overflow-auto my-2 bg-gray-100 dark:bg-gray-800 p-2 rounded">
                                <pre {...props} />
                              </div>
                            ),
                            code: ({ node, ...props }) => (
                              <code className="bg-gray-100 dark:bg-gray-800 rounded px-1" {...props} />
                            ),
                          }}
                        >
                          {message.displayContent}
                        </ReactMarkdown>
                      </div>
                    )}

                    {message.audio && (
                      <audio controls className="mt-2 max-w-full">
                        <source src={message.audio} type="audio/webm" />
                        Your browser does not support the audio element.
                      </audio>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </CardContent>

            <CardFooter className="flex-shrink-0 border-t">
              <form onSubmit={onSubmit} className="flex w-full space-x-2">
                {!isRecording ? (
                  <Input
                    value={input}
                    onChange={handleInputChange}
                    placeholder={isLoading ? "Thinking..." : "Type your message..."}
                    disabled={isLoading}
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
                        {isTyping || recordedAudioUrl ? (
                          <motion.div
                            key="send-button"
                            initial={{ opacity: 0, scale: 0.8, width: 0 }}
                            animate={{ opacity: 1, scale: 1, width: 'auto' }}
                            exit={{ opacity: 0, scale: 0.8, width: 0 }}
                            transition={{ duration: 0.15 }}
                          >
                            <Button
                              type="submit"
                              disabled={isLoading}
                              className="bg-blue-500 text-white hover:bg-blue-600"
                            >
                              {isLoading ? (
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                              ) : (
                                <SendIcon className="w-4 h-4" />
                              )}
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
                            <AudioRecorder
                              onRecordingChange={setIsRecording}
                              onAudioData={setAudioData}
                              onAudioReady={handleAudioReady}
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
                    <h2 className="text-sm font-semibold mb-2 flex items-center gap-2">
                      <span>🧠</span>
                      <span>Memory Status</span>
                    </h2>
                    <div className="text-xs text-gray-600 max-h-32 overflow-y-auto font-mono">
                      <pre className="whitespace-pre-wrap">
                        {memoryLog}
                      </pre>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-3 rounded-lg">
                    <h2 className="text-sm font-semibold mb-2 flex items-center gap-2">
                      <span>⚙️</span>
                      <span>Process Flow</span>
                    </h2>
                    <div className="text-xs text-gray-600 max-h-32 overflow-y-auto font-mono">
                      <pre className="whitespace-pre-wrap">
                        {executionFlow}
                      </pre>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          <div className="flex flex-col gap-4 w-full max-w-md">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>User Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(metrics).map(([key, value]) => (
                  <div key={key} className="flex flex-col">
                    <span className="text-xs text-gray-500 capitalize">
                      {key.replace(/_/g, ' ')}
                    </span>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className="bg-blue-500 h-1.5 rounded-full" 
                        style={{ width: `${(Number(value) / 10) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter className="flex gap-2">
              <Button
                onClick={() => setVoiceMode(!voiceMode)}
                className={`text-sm ${
                  voiceMode
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-gray-100 text-gray-400 border border-gray-400 hover:bg-blue-100'
                }`}
              >
                Voice Mode
              </Button>
              <Button
                onClick={() => setNsfwMode(!nsfwMode)}
                className={`text-sm ${
                  nsfwMode
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-gray-100 text-gray-400 border border-gray-400 hover:bg-blue-100'
                }`}
              >
                NSFW
              </Button>
              <Button
                onClick={() => setPrivateMode(!privateMode)}
                className={`text-sm ${
                  privateMode
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-gray-100 text-gray-400 border border-gray-400 hover:bg-blue-100'
                }`}
              >
                 Private Mode
              </Button>
            </CardFooter>
          </Card>
          <Card className="w-full max-w-md mt-4">
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                <span>Vault Performance</span>
                <Button variant="link" className="text-blue-500" asChild>
                  <a href="/trading">View Details →</a>
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-2xl font-bold text-green-500">+21.3%</p>
                    <p className="text-sm text-gray-500">7d Return</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold">$1425</p>
                    <p className="text-sm text-gray-500">Total Value</p>
                  </div>
                </div>
                <StatsChart />
              </div>
            </CardContent>
          </Card>
          </div>
        </div>
      </div>
    </div>
  );
}