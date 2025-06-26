import { listBenchmarkRuns } from '@/database/benchmarks'
import { formatDistanceToNow } from 'date-fns'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Award, ChevronRight } from 'lucide-react'

export async function RecentBenchmarks() {
  const benchmarkRuns = await listBenchmarkRuns(0, 5)

  if (benchmarkRuns.length === 0) {
    return (
      <div className="text-center py-6">
        <Award className="mx-auto h-12 w-12 text-muted-foreground mb-2" />
        <p className="text-sm text-muted-foreground">No benchmark runs yet</p>
        <p className="text-xs text-muted-foreground mt-1">
          Run benchmarks to compare model performance
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {benchmarkRuns.map((run) => {
        // Parse timestamp
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
          runDate = new Date(run.timestamp)
        }

        const timeAgo = isNaN(runDate.getTime()) 
          ? run.timestamp 
          : formatDistanceToNow(runDate, { addSuffix: true })

        return (
          <div key={run.id} className="flex items-center justify-between py-2">
            <div className="space-y-1">
              <p className="text-sm font-medium">Benchmark Run</p>
              <p className="text-xs text-muted-foreground">{timeAgo}</p>
            </div>
            <Link href={`/benchmarks/${run.id}`}>
              <Button variant="ghost" size="sm">
                View
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            </Link>
          </div>
        )
      })}
      
      <div className="pt-2 border-t">
        <Link href="/benchmarks">
          <Button variant="outline" size="sm" className="w-full">
            View All Benchmarks
          </Button>
        </Link>
      </div>
    </div>
  )
}