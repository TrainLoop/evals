import { getDuckDB } from './duckdb'
import { convertBigIntsToNumbers } from '@/utils/json-helpers'
import type { Registry, RegistryEntry } from './schema'

export async function getRegistry(): Promise<Registry | null> {
  const db = await getDuckDB()
  const conn = await db.connect()
  try {
    const reader = await conn.runAndReadAll('SELECT * FROM registry LIMIT 1')
    const rows = reader.getRowObjects()
    if (rows.length === 0) return null
    
    // The registry data comes back as a single row with schema and files columns
    const row = rows[0]
    
    // Convert to Registry type (the structure should match)
    return convertBigIntsToNumbers<Registry>(row as unknown as Registry)
  } catch (err) {
    // If the registry table is empty or there's an error, return null
    console.warn('Warning: Failed to fetch registry:', err)
    return null
  } finally {
    conn.closeSync()
  }
}

export async function getRegistryEntries(): Promise<RegistryEntry[]> {
  const registry = await getRegistry()
  if (!registry || !registry.files) return []

  const entries: RegistryEntry[] = []
  Object.values(registry.files).forEach(fileEntries => {
    Object.values(fileEntries).forEach(entry => {
      entries.push(entry)
    })
  })

  return entries
}

export async function getRegistryByFile(filePath: string): Promise<Record<string, RegistryEntry> | null> {
  const registry = await getRegistry()
  if (!registry || !registry.files || !registry.files[filePath]) return null

  return registry.files[filePath]
}
