import { NextResponse } from 'next/server'
import { listResults } from '@/database/results'
import { convertBigIntsToNumbers } from '@/utils/json-helpers'

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const offset = parseInt(searchParams.get('offset') ?? '0', 10)
  const limit = parseInt(searchParams.get('limit') ?? '50', 10)
  const ts = searchParams.get('ts') || ''
  const suite = searchParams.get('suite') || ''
  const rows = await listResults({ ts, suite, offset, limit })

  const safeRows = convertBigIntsToNumbers(rows)
  return NextResponse.json(safeRows)
}
