'use client'
import { useCallback, useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

interface Row {
  rowid: number
  tag: string
  model: string
  input: {
    items: Array<{
      entries: {
        role: string
        content: string
      }
    }>
  }
  output: {
    entries: {
      content: string
    }
  }
  durationMs: number | { micros: number }
  startTimeMs: number | { micros: number }
  endTimeMs: { micros: number }
  url: string
  location: {
    entries: {
      file: string
      lineNumber: string
    }
  }
  modelParams: {
    entries: {
      max_tokens: number
      system: any
      temperature: number
      stream: boolean
    }
  }
}

export function EventsTable() {
  const [rows, setRows] = useState<Row[]>([])
  const isLoadingRef = useRef(false)
  const currentPageRef = useRef(-1)  // Start at -1 so first load is page 0
  const hasMoreDataRef = useRef(true)  // Track if there's more data to load

  // Define load function without dependencies
  const loadNextPage = async () => {
    // Skip if already loading or no more data
    if (isLoadingRef.current || !hasMoreDataRef.current) return;

    const nextPage = currentPageRef.current + 1;

    // Set loading flag using ref to avoid re-renders
    isLoadingRef.current = true;

    try {
      const res = await fetch(`/api/events?offset=${nextPage * 50}&limit=50`);
      if (!res.ok) {
        console.error(`Failed to load events: ${res.status}`);
        return;
      }

      const data = await res.json();

      // If we got less than requested or empty, we've reached the end
      if (data.length === 0 || data.length < 50) {
        hasMoreDataRef.current = false;
      }

      // Only update state once
      if (data.length > 0) {
        setRows(prevRows => [...prevRows, ...data]);
        currentPageRef.current = nextPage;
      }
    } catch (err) {
      console.error('Error loading events:', err);
    } finally {
      isLoadingRef.current = false;
    }
  };

  // Load initial data only once when component mounts
  useEffect(() => {
    loadNextPage();

    // Set up intersection observer for infinite scrolling
    const observer = new IntersectionObserver(entries => {
      // Only load more if the sentinel is visible and we're not already loading
      if (entries[0].isIntersecting && !isLoadingRef.current && hasMoreDataRef.current) {
        loadNextPage();
      }
    });

    // Get the sentinel element
    const sentinel = document.getElementById('events-sentinel');
    if (sentinel) observer.observe(sentinel);

    // Cleanup
    return () => observer.disconnect();
  }, []); // Empty deps array ensures this only runs once
  return (
    <div className="container mx-auto">
      <Table className="w-full border-collapse">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[15%]">Time</TableHead>
            <TableHead className="w-[10%]">Tag</TableHead>
            <TableHead className="w-[15%]">Model</TableHead>
            <TableHead className="w-[22%]">Input</TableHead>
            <TableHead className="w-[22%]">Output</TableHead>
            <TableHead className="w-[10%] text-right">Duration</TableHead>
            <TableHead className="w-[6%]">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((r) => (
            <TableRow key={r.rowid}>
              <TableCell>
                {(() => {
                  // Handle complex timestamp format
                  const timestamp = typeof r.startTimeMs === 'object' && r.startTimeMs?.micros
                    ? new Date(r.startTimeMs.micros / 1000)
                    : typeof r.startTimeMs === 'number'
                      ? new Date(r.startTimeMs)
                      : null;

                  return timestamp && !isNaN(timestamp.getTime())
                    ? timestamp.toLocaleString()
                    : 'Unknown';
                })()}
              </TableCell>
              <TableCell>{r.tag || 'Unknown'}</TableCell>
              <TableCell>{r.model || 'Unknown'}</TableCell>
              <TableCell className="max-w-[200px] truncate">
                {(() => {
                  // Get the last user message from the complex input structure
                  if (r.input?.items && Array.isArray(r.input.items) && r.input.items.length > 0) {
                    // Find the last user message
                    const userMessages = r.input.items
                      .filter(item => item.entries?.role === 'user')
                      .map(item => item.entries?.content);

                    if (userMessages.length > 0) {
                      return userMessages[userMessages.length - 1];
                    }

                    // Fallback: just take the last message regardless of role
                    const lastItem = r.input.items[r.input.items.length - 1];
                    return lastItem?.entries?.content || 'No input content';
                  }
                  return 'No input';
                })()}
              </TableCell>
              <TableCell className="max-w-[200px] truncate">
                {r.output?.entries?.content
                  ? r.output.entries.content.split('\n')[0]
                  : 'No output'}
              </TableCell>
              <TableCell className="text-right font-mono">
                {typeof r.durationMs === 'object' && r.durationMs?.micros
                  ? `${(r.durationMs.micros / 1000).toFixed(2)}ms`
                  : (typeof r.durationMs === 'number'
                    ? `${r.durationMs.toFixed(2)}ms`
                    : 'N/A')}
              </TableCell>
              <TableCell>
                <Link href={`/events/${r.rowid}`} className="underline">view</Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div id="events-sentinel" className="h-4" />
    </div>
  )
}
