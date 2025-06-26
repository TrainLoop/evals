import { getDuckDB } from './duckdb'
import { convertBigIntsToNumbers } from '@/utils/json-helpers'

export interface BenchmarkResult {
  provider: string
  metric: string
  score: number
  passed: number
  total: number
  reason?: string
}

export interface BenchmarkRun {
  id: string
  timestamp: string
  results: BenchmarkResult[]
}

export async function listBenchmarkRuns(offset = 0, limit = 50) {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    // Get unique benchmark runs (directories)
    const query = `
      SELECT DISTINCT 
        regexp_extract(filename, '/benchmarks/([^/]+)/', 1) AS id,
        regexp_extract(filename, '/benchmarks/([^/]+)/', 1) AS timestamp
      FROM read_json_auto('${process.env.TRAINLOOP_DATA_FOLDER}/benchmarks/*/*.jsonl', filename=true)
      ORDER BY timestamp DESC
      LIMIT ${limit} OFFSET ${offset}
    `
    
    const reader = await conn.runAndReadAll(query)
    const rows = reader.getRowObjects()
    return convertBigIntsToNumbers(rows)
  } catch (err) {
    // If the benchmarks directory doesn't exist or is empty, return empty array
    console.warn('Warning: Failed to fetch benchmark runs, returning empty array:', err)
    return []
  } finally {
    conn.closeSync()
  }
}

export async function getBenchmarkRun(id: string): Promise<BenchmarkRun | null> {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    // Read all results for a specific benchmark run, filtering for result records only
    const query = `
      SELECT 
        metric,
        sample->>'$.model' AS provider,
        passed,
        score,
        reason,
        type
      FROM read_json_auto('${process.env.TRAINLOOP_DATA_FOLDER}/benchmarks/${id}/*.jsonl')
      WHERE type = 'result'
    `
    
    const reader = await conn.runAndReadAll(query)
    const rows = reader.getRowObjects()
    
    if (rows.length === 0) {
      return null
    }
    
    // Group results by provider and metric
    const resultsMap = new Map<string, BenchmarkResult>()
    
    rows.forEach((row: any) => {
      const key = `${row.provider}-${row.metric}`
      if (!resultsMap.has(key)) {
        resultsMap.set(key, {
          provider: row.provider,
          metric: row.metric,
          score: 0,
          passed: 0,
          total: 0
        })
      }
      
      const result = resultsMap.get(key)!
      result.total += 1
      if (row.passed) {
        result.passed += 1
      }
      // Use the score field directly now that it exists
      if (row.score !== null && row.score !== undefined) {
        // Average the scores
        result.score = (result.score * (result.total - 1) + row.score) / result.total
      }
    })
    
    // Calculate pass rates as percentages
    const results = Array.from(resultsMap.values()).map(result => ({
      ...result,
      score: result.total > 0 ? (result.passed / result.total) * 100 : 0
    }))
    
    return {
      id,
      timestamp: id,
      results: convertBigIntsToNumbers(results)
    }
  } catch (err) {
    console.warn(`Warning: Failed to fetch benchmark run ${id}:`, err)
    return null
  } finally {
    conn.closeSync()
  }
}

export async function getBenchmarkComparison(id: string) {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    // Get aggregated data for chart visualization, filtering for result records only
    const query = `
      SELECT 
        metric,
        sample->>'$.model' AS provider,
        COUNT(*) AS total,
        SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) AS passed,
        ROUND((SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS pass_rate
      FROM read_json_auto('${process.env.TRAINLOOP_DATA_FOLDER}/benchmarks/${id}/*.jsonl')
      WHERE type = 'result'
      GROUP BY metric, provider
      ORDER BY metric, provider
    `
    
    const reader = await conn.runAndReadAll(query)
    const rows = reader.getRowObjects()
    
    // Transform data for chart format
    const metricsMap = new Map<string, any>()
    
    rows.forEach((row: any) => {
      if (!metricsMap.has(row.metric)) {
        metricsMap.set(row.metric, { metric: row.metric })
      }
      const metricData = metricsMap.get(row.metric)
      metricData[row.provider] = row.pass_rate
    })
    
    return {
      data: Array.from(metricsMap.values()),
      providers: [...new Set(rows.map((r: any) => r.provider))]
    }
  } catch (err) {
    console.warn(`Warning: Failed to fetch benchmark comparison for ${id}:`, err)
    return { data: [], providers: [] }
  } finally {
    conn.closeSync()
  }
}