import { getDuckDB } from './duckdb'
import { convertBigIntsToNumbers } from '@/utils/json-helpers'

export interface ListEventsOptions {
  offset?: number
  limit?: number
  filters?: {
    from?: number
    to?: number
    tags?: string[]
    models?: string[]
    durationLt?: number
  }
}

export async function listEvents({ offset = 0, limit = 50, filters }: ListEventsOptions) {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    const clauses: string[] = []
    const params: Record<string, unknown> = {}
    if (filters?.from !== undefined && filters?.to !== undefined) {
      clauses.push('startTimeMs BETWEEN $from AND $to')
      params.from = filters.from
      params.to = filters.to
    }
    if (filters?.tags && filters.tags.length) {
      clauses.push(`tag IN (${filters.tags.map((_, i) => `$tag${i}`).join(',')})`)
      filters.tags.forEach((t, i) => (params[`tag${i}`] = t))
    }
    if (filters?.models && filters.models.length) {
      clauses.push(`model IN (${filters.models.map((_, i) => `$model${i}`).join(',')})`)
      filters.models.forEach((m, i) => (params[`model${i}`] = m))
    }
    if (filters?.durationLt !== undefined) {
      clauses.push('durationMs < $dur')
      params.dur = filters.durationLt
    }
    const where = clauses.length ? `WHERE ${clauses.join(' AND ')}` : ''
    const sql = `SELECT * FROM events ${where} ORDER BY startTimeMs DESC LIMIT ${limit} OFFSET ${offset}`
    // Cast params to the correct DuckDBValue type expected by the DuckDB API
    const reader = await conn.runAndReadAll(sql, params as Record<string, any>)
    const rows = reader.getRowObjects() as any[]
    // Convert BigInt values to Number to make them JSON serializable
    return convertBigIntsToNumbers(rows)
  } finally {
    conn.closeSync()
  }
}

export async function getEvent(id: number) {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    // Cast params to the correct DuckDBValue type expected by the DuckDB API
    const reader = await conn.runAndReadAll('SELECT * FROM events WHERE rowid = $id', { id } as Record<string, any>)
    const rows = reader.getRowObjects() as any[]
    if (rows.length === 0) return null
    return convertBigIntsToNumbers(rows)[0]
  } finally {
    conn.closeSync()
  }
}
