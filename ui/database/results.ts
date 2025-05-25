import { getDuckDB } from './duckdb'
import { convertBigIntsToNumbers } from '@/utils/json-helpers'

export interface ListResultsOptions {
  ts: string
  suite: string
  offset?: number
  limit?: number
}

export async function listResults({ ts, suite, offset = 0, limit = 50 }: ListResultsOptions) {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    let query = 'SELECT * FROM results'
    const conditions: string[] = []
    const queryParams: { [key: string]: string } = {}

    if (ts) {
      conditions.push('ts = $ts')
      queryParams.ts = ts
    }
    if (suite) {
      conditions.push('suite = $suite')
      queryParams.suite = suite
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ')
    }

    query += ` ORDER BY passed ASC, ts DESC, suite DESC LIMIT ${limit} OFFSET ${offset}`

    const reader = await conn.runAndReadAll(query, queryParams)
    const rows = reader.getRowObjects()
    return convertBigIntsToNumbers(rows)
  } catch (err) {
    // If the results table is empty or there's an error, return empty array
    console.warn('Warning: Failed to fetch results, returning empty array:', err)
    return []
  } finally {
    conn.closeSync()
  }
}

export async function getResult(id: string) {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    const reader = await conn.runAndReadAll('SELECT * FROM results WHERE rowid = $id', { id } as Record<string, any>)
    const rows = reader.getRowObjects()
    return convertBigIntsToNumbers(rows)[0]
  } catch (err) {
    // If there's an error fetching the result, return null
    console.warn(`Warning: Failed to fetch result with id ${id}:`, err)
    return null
  } finally {
    conn.closeSync()
  }
}
