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
    
    if (filters?.from !== undefined && filters?.to !== undefined) {
      clauses.push(`startTimeMs BETWEEN ${filters.from} AND ${filters.to}`)
    }
    if (filters?.tags?.length) {
      const tagsList = filters.tags.map(tag => `'${tag.replace(/'/g, "''")}'`).join(',')
      clauses.push(`tag IN (${tagsList})`)
    }
    if (filters?.models?.length) {
      const modelsList = filters.models.map(model => `'${model.replace(/'/g, "''")}'`).join(',')
      clauses.push(`model IN (${modelsList})`)
    }
    if (filters?.durationLt !== undefined) {
      clauses.push(`durationMs < ${filters.durationLt}`)
    }

    const whereClause = clauses.length > 0 ? `WHERE ${clauses.join(' AND ')}` : ''
    const query = `SELECT * FROM events ${whereClause} ORDER BY startTimeMs DESC LIMIT ${limit} OFFSET ${offset}`
    
    const reader = await conn.runAndReadAll(query)
    const rows = reader.getRowObjects()
    return convertBigIntsToNumbers(rows)
  } catch (err) {
    // If there's an error (e.g., empty table), return empty array
    console.warn('Warning: Failed to fetch events, returning empty array:', err)
    return []
  } finally {
    conn.closeSync()
  }
}

export async function getEvent(id: number) {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    const query = `SELECT * FROM events WHERE rowid = ${id}`
    const reader = await conn.runAndReadAll(query)
    const rows = reader.getRowObjects() as any[]
    if (rows.length === 0) return null
    return convertBigIntsToNumbers(rows)[0]
  } catch (err) {
    // If there's an error fetching the event, return null
    console.warn(`Warning: Failed to fetch event with id ${id}:`, err)
    return null
  } finally {
    conn.closeSync()
  }
}
