import { NextRequest, NextResponse } from 'next/server'
import { getBenchmarkRun, getBenchmarkComparison } from '@/database/benchmarks'

export const runtime = 'nodejs'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    
    const [benchmarkRun, comparison] = await Promise.all([
      getBenchmarkRun(id),
      getBenchmarkComparison(id)
    ])

    if (!benchmarkRun) {
      return NextResponse.json({ error: 'Benchmark run not found' }, { status: 404 })
    }

    return NextResponse.json({ benchmarkRun, comparison })
  } catch (error) {
    console.error('Failed to fetch benchmark run:', error)
    return NextResponse.json({ error: 'Failed to fetch benchmark run' }, { status: 500 })
  }
}