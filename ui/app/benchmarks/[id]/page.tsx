import { notFound } from 'next/navigation'
import { getBenchmarkRun, getBenchmarkComparison, getBenchmarkSummary } from '@/database/benchmarks'
import { ModelComparisonChart } from '@/components/charts/model-comparison-chart'
import { BenchmarkDetails } from '@/components/benchmark-details'
import { BenchmarkSummary } from '@/components/benchmark-summary'
import { Button } from '@/components/ui/button'
import { ChevronLeft } from 'lucide-react'
import Link from 'next/link'

interface BenchmarkPageProps {
  params: Promise<{
    id: string
  }>
}

export default async function BenchmarkPage({ params }: BenchmarkPageProps) {
  const { id } = await params
  
  const [benchmarkRun, comparison, summaryData] = await Promise.all([
    getBenchmarkRun(id),
    getBenchmarkComparison(id),
    getBenchmarkSummary(id)
  ])

  if (!benchmarkRun) {
    notFound()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/benchmarks">
          <Button variant="ghost" size="sm">
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back to Benchmarks
          </Button>
        </Link>
      </div>

      <div>
        <h1 className="text-3xl font-bold tracking-tight">Benchmark Details</h1>
        <p className="text-muted-foreground">
          Run ID: <code className="font-mono text-sm">{id}</code>
        </p>
      </div>

      {summaryData && (
        <BenchmarkSummary summary={summaryData.summary} metadata={summaryData.metadata} />
      )}

      {comparison.data.length > 0 && (
        <div className="w-full max-w-6xl mx-auto">
          <ModelComparisonChart
            title="Provider Performance Comparison"
            description="Pass rates for each metric across different providers"
            data={comparison.data}
            models={comparison.providers}
            className="w-full"
          />
        </div>
      )}

      <BenchmarkDetails benchmarkRun={benchmarkRun} />
    </div>
  )
}