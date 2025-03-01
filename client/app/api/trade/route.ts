import { NextResponse } from 'next/server';

interface TradeResponse {
  status: string;
  actions: string[];
  metadata: {
    execution_time?: string;
    total_actions?: number;
    status?: string;
  };
}

export async function POST() {
  try {
    // Call the Python backend trade endpoint
    const response = await fetch(`${process.env.NEXT_PUBLIC_AGENT_SERVER_URL}/trade`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: TradeResponse = await response.json();

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error executing trade:', error);
    return NextResponse.json(
      {
        status: 'error',
        actions: [`Error occurred: ${error instanceof Error ? error.message : 'Unknown error'}`],
        metadata: {
          execution_time: new Date().toISOString(),
          status: 'failed'
        }
      },
      { status: 500 }
    );
  }
}
