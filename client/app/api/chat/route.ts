import { NextRequest, NextResponse } from 'next/server';

const AGENT_SERVER_URL = process.env.NEXT_PUBLIC_AGENT_SERVER_URL || 'http://localhost:8001';

// Define types for our chat feature
interface ChatRequest {
  message: string;
  context?: {
    user_id?: string;
    [key: string]: any;
  };
}

interface ChatResponse {
  response: string;
  context: {
    user_id: string;
    memory_count: number;
    user_interests: string[];
    user_mood: string;
    relevant_memories?: string[];
    [key: string]: any;
  };
}

export async function POST(req: NextRequest) {
    try {
        const { message, context } = await req.json() as ChatRequest;

        if (!message) {
            return NextResponse.json(
                { error: 'Message is required' },
                { status: 400 }
            );
        }

        // Extract the user ID from cookies or create a new one
        const userIdCookie = req.cookies.get('rose_user_id');
        const userId = userIdCookie?.value || crypto.randomUUID();
        
        // Create a context object if not provided or add userId if missing
        const chatContext = context || {};
        chatContext.user_id = chatContext.user_id || userId;

        // Forward the request to the Python agent server
        const response = await fetch(`${AGENT_SERVER_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message, 
                context: chatContext 
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Agent server error: ${errorData.detail || response.statusText}`);
        }

        const data = await response.json() as ChatResponse;
        
        // Create a response object with the agent's response
        const nextResponse = NextResponse.json(data);
        
        // Set a cookie to maintain the user's identity across sessions if not already set
        if (!userIdCookie) {
            nextResponse.cookies.set('rose_user_id', userId, {
                maxAge: 60 * 60 * 24 * 30, // 30 days
                path: '/',
                sameSite: 'strict',
                secure: process.env.NODE_ENV === 'production',
                httpOnly: true,
            });
        }

        return nextResponse;

    } catch (error) {
        console.error('Chat error:', error);
        return NextResponse.json(
            { error: 'Internal server error', details: (error as Error).message },
            { status: 500 }
        );
    }
}