import { NextRequest, NextResponse } from 'next/server'
import { listBenchmarkRuns } from '@/database/benchmarks'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const offset = parseInt(searchParams.get('offset') || '0')
  const limit = parseInt(searchParams.get('limit') || '50')

  try {
    const benchmarkRuns = await listBenchmarkRuns(offset, limit)
    return NextResponse.json({ benchmarkRuns })
  } catch (error) {
    console.error('Failed to fetch benchmark runs:', error)
    return NextResponse.json({ error: 'Failed to fetch benchmark runs' }, { status: 500 })
  }
}