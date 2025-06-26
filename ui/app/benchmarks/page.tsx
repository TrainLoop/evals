import { listBenchmarkRuns } from '@/database/benchmarks'
import { BenchmarksList } from '@/components/benchmarks-list'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default async function BenchmarksPage() {
  const benchmarkRuns = await listBenchmarkRuns()

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Benchmarks</h1>
        <p className="text-muted-foreground">
          Compare performance across different models and providers
        </p>
      </div>

      {benchmarkRuns.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>No Benchmarks Found</CardTitle>
            <CardDescription>
              Run benchmarks using the CLI to see results here
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Benchmarks will appear here once you run them using the TrainLoop CLI.
            </p>
          </CardContent>
        </Card>
      ) : (
        <BenchmarksList benchmarkRuns={benchmarkRuns} />
      )}
    </div>
  )
}