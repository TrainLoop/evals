"use client"

import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ChevronRight, Clock, BarChart3 } from 'lucide-react'

interface BenchmarkRun {
  id: string
  timestamp: string
}

interface BenchmarksListProps {
  benchmarkRuns: BenchmarkRun[]
}

export function BenchmarksList({ benchmarkRuns }: BenchmarksListProps) {
  return (
    <div className="grid gap-4">
      {benchmarkRuns.map((run) => {
        // Parse timestamp assuming format YYYY-MM-DD_HH-MM-SS
        const dateParts = run.timestamp.match(/(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})/)
        let runDate: Date
        
        if (dateParts) {
          const [_, year, month, day, hour, minute, second] = dateParts
          runDate = new Date(
            parseInt(year),
            parseInt(month) - 1,
            parseInt(day),
            parseInt(hour),
            parseInt(minute),
            parseInt(second)
          )
        } else {
          // Fallback to parsing as-is
          runDate = new Date(run.timestamp)
        }

        const timeAgo = isNaN(runDate.getTime()) 
          ? run.timestamp 
          : formatDistanceToNow(runDate, { addSuffix: true })

        return (
          <Card key={run.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Benchmark Run
                  </CardTitle>
                  <CardDescription className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    {timeAgo}
                  </CardDescription>
                </div>
                <Link href={`/benchmarks/${run.id}`}>
                  <Button variant="ghost" size="sm">
                    View Details
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                ID: <code className="font-mono text-xs">{run.id}</code>
              </p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}