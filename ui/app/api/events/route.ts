import { NextResponse } from 'next/server'
import { listEvents } from '@/database/events'
import { convertBigIntsToNumbers } from '@/utils/json-helpers'

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const offset = parseInt(searchParams.get('offset') ?? '0', 10)
  const limit = parseInt(searchParams.get('limit') ?? '50', 10)
  const from = searchParams.get('from') ? Number(searchParams.get('from')) : undefined
  const to = searchParams.get('to') ? Number(searchParams.get('to')) : undefined
  const tags = searchParams.getAll('tag')
  const models = searchParams.getAll('model')
  const durationLt = searchParams.get('durationLt') ? Number(searchParams.get('durationLt')) : undefined
  
  const rows = await listEvents({ offset, limit, filters: { from, to, tags, models, durationLt } })
  
  // Convert any BigInt values to numbers before serializing to JSON
  const safeRows = convertBigIntsToNumbers(rows);
  
  return NextResponse.json(safeRows)
}
