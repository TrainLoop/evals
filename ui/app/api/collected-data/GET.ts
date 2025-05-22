import { NextResponse } from 'next/server';
import { select } from '@/database/utils';

export const GET = async () => {
  try {
    const rows = await select("events", {
      tag: true,
      durationMs: true,
      input: true,
      output: true,
      modelParams: true,
      url: true,
      location: true,
      endTimeMs: true,
      model: true,
      startTimeMs: true,
    })

    return new NextResponse(JSON.stringify(rows), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error("Error in /api/collected-data:", error);
    return NextResponse.json(
      { error: 'Failed to retrieve data', message: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
