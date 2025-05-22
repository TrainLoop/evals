import { NextResponse, NextRequest } from 'next/server'
import { getEvent } from '@/database/events'
import { convertBigIntsToNumbers } from '@/utils/json-helpers'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const row = await getEvent(Number(id));
  if (!row) return NextResponse.json({ error: 'not found' }, { status: 404 });

  // Convert BigInt values to string for serialization
  const safeRow = convertBigIntsToNumbers(row);
  return NextResponse.json(safeRow);
}
