'use client'
import { useEffect, useRef, useState, useCallback } from 'react'
import Link from 'next/link'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

interface Row {
  rowid: string
  metric: string
  passed: number
  reason: string | null
  sample: {
    entries: Record<string, unknown>[]
  }
  ts: string
  suite: string
}

export function ResultsList({ ts, suite }: { ts: string; suite: string }) {
  const [rows, setRows] = useState<Row[]>([])
  const isLoadingRef = useRef(false)
  const currentPageRef = useRef(-1) // Start at -1 so first load is page 0
  const hasMoreDataRef = useRef(true)
  const sentinelRef = useRef<HTMLDivElement>(null)

  const loadNextPage = useCallback(async (currentTs: string, currentSuite: string) => {
    if (isLoadingRef.current || !hasMoreDataRef.current) return

    const nextPage = currentPageRef.current + 1
    isLoadingRef.current = true

    try {
      const params = new URLSearchParams({
        ts: currentTs,
        suite: currentSuite,
        offset: String(nextPage * 50),
        limit: '50',
      })
      const res = await fetch(`/api/results?${params}`)
      if (!res.ok) {
        console.error(`Failed to load results: ${res.status}`)
        // Potentially set hasMoreDataRef.current = false or handle error state
        return
      }
      const rawData: Row[] = await res.json()

      if (rawData.length === 0 || rawData.length < 50) {
        hasMoreDataRef.current = false
      }

      if (rawData.length > 0) {
        setRows((prevRows) => (nextPage === 0 ? rawData : [...prevRows, ...rawData]))
        currentPageRef.current = nextPage
      }
    } catch (err) {
      console.error('Error loading results:', err)
      // Potentially set hasMoreDataRef.current = false or handle error state
    } finally {
      isLoadingRef.current = false
    }
  }, []) // useCallback to memoize, dependencies will be handled by how it's called

  // Effect for initial load and when ts/suite changes
  useEffect(() => {
    setRows([]) // Clear existing rows
    currentPageRef.current = -1 // Reset page
    hasMoreDataRef.current = true // Assume there's data
    // Manually trigger load for page 0 with current ts/suite
    // Need to ensure loadNextPage uses the *current* ts/suite from props for this call
    loadNextPage(ts, suite)
  }, [ts, suite, loadNextPage]) // loadNextPage is stable due to useCallback

  // Effect for intersection observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isLoadingRef.current && hasMoreDataRef.current) {
          // Pass current ts and suite to loadNextPage when scrolling
          loadNextPage(ts, suite)
        }
      },
      { threshold: 1.0 } // Trigger when element is fully visible
    )

    const currentSentinel = sentinelRef.current
    if (currentSentinel) {
      observer.observe(currentSentinel)
    }

    return () => {
      if (currentSentinel) {
        observer.unobserve(currentSentinel)
      }
      observer.disconnect()
    }
    // Dependencies: ts and suite are needed if loadNextPage inside observer needs them directly
    // loadNextPage itself is stable, but the values it uses (ts, suite) for scrolling loads might change
  }, [ts, suite, loadNextPage])

  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>metric</TableHead>
            <TableHead>passed</TableHead>
            <TableHead>reason</TableHead>
            <TableHead>sample</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((r) => (
            <TableRow key={r.rowid} className={r.passed ? '' : 'bg-red-50'}>
              <TableCell>{r.metric}</TableCell>
              <TableCell>{r.passed ? '✓' : '✗'}</TableCell>
              <TableCell>{r.reason ? r.reason : 'pass'}</TableCell>
              <TableCell>
                <Link href={`/results/${r.rowid}`} className="underline">view</Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div ref={sentinelRef} className="h-4" />
    </div>
  )
}
