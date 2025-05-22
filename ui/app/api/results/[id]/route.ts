import { NextResponse } from 'next/server'
import { getResult } from '@/database/results'

export async function GET(_: Request, { params }: { params: { id: string } }) {
  const row = await getResult(params.id)
  if (!row) return NextResponse.json({ error: 'not found' }, { status: 404 })
  return NextResponse.json(row)
}
