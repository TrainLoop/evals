import { notFound } from 'next/navigation'
import { getBenchmarkRun, getBenchmarkComparison } from '@/database/benchmarks'
import { ModelComparisonChart } from '@/components/charts/model-comparison-chart'
import { BenchmarkDetails } from '@/components/benchmark-details'
import { Button } from '@/components/ui/button'
import { ChevronLeft } from 'lucide-react'
import Link from 'next/link'

interface BenchmarkPageProps {
  params: {
    id: string
  }
}

export default async function BenchmarkPage({ params }: BenchmarkPageProps) {
  const [benchmarkRun, comparison] = await Promise.all([
    getBenchmarkRun(params.id),
    getBenchmarkComparison(params.id)
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
          Run ID: <code className="font-mono text-sm">{params.id}</code>
        </p>
      </div>

      {comparison.data.length > 0 && (
        <ModelComparisonChart
          title="Provider Performance Comparison"
          description="Pass rates for each metric across different providers"
          data={comparison.data}
          models={comparison.providers}
          className="w-full"
        />
      )}

      <BenchmarkDetails benchmarkRun={benchmarkRun} />
    </div>
  )
}