import { getDuckDB } from './duckdb'
import { convertBigIntsToNumbers } from '@/utils/json-helpers'

export interface ListResultsOptions {
  ts: string
  suite: string
  offset?: number
  limit?: number
}

export async function listResults({ offset = 0, limit = 50, ts, suite }: ListResultsOptions) {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    const clauses: string[] = []
    
    if (ts) {
      clauses.push(`ts = '${ts.replace(/'/g, "''")}'`) // Basic SQL injection protection
    }
    if (suite) {
      clauses.push(`suite = '${suite.replace(/'/g, "''")}'`) // Basic SQL injection protection
    }

    const whereClause = clauses.length > 0 ? `WHERE ${clauses.join(' AND ')}` : ''
    const query = `SELECT * FROM results ${whereClause} ORDER BY passed ASC, ts DESC, suite DESC LIMIT ${limit} OFFSET ${offset}`
    
    const reader = await conn.runAndReadAll(query)
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
