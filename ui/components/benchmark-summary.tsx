import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Clock, DollarSign, AlertCircle, Trophy } from 'lucide-react'

interface BenchmarkSummaryProps {
  summary: any
  metadata: any
}

export function BenchmarkSummary({ summary, metadata }: BenchmarkSummaryProps) {
  if (!summary || !metadata) {
    return null
  }

  // Find best and worst providers
  let bestProvider = { name: '', passRate: 0, cost: 0 }
  let worstProvider = { name: '', passRate: 100, cost: 0 }
  let fastestProvider = { name: '', latency: Infinity }
  let cheapestProvider = { name: '', cost: Infinity }

  Object.entries(summary.provider_summaries || {}).forEach(([provider, stats]: [string, any]) => {
    if (stats.pass_rate > bestProvider.passRate) {
      bestProvider = { name: provider, passRate: stats.pass_rate * 100, cost: stats.total_cost }
    }
    if (stats.pass_rate < worstProvider.passRate) {
      worstProvider = { name: provider, passRate: stats.pass_rate * 100, cost: stats.total_cost }
    }
    if (stats.avg_latency_ms < fastestProvider.latency) {
      fastestProvider = { name: provider, latency: stats.avg_latency_ms }
    }
    if (stats.total_cost < cheapestProvider.cost) {
      cheapestProvider = { name: provider, cost: stats.total_cost }
    }
  })

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Best Performance</CardTitle>
          <Trophy className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{bestProvider.name}</div>
          <p className="text-xs text-muted-foreground">
            {bestProvider.passRate.toFixed(1)}% pass rate
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Fastest Response</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{fastestProvider.name}</div>
          <p className="text-xs text-muted-foreground">
            {fastestProvider.latency.toFixed(0)}ms avg latency
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Most Cost Effective</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{cheapestProvider.name}</div>
          <p className="text-xs text-muted-foreground">
            ${cheapestProvider.cost.toFixed(4)} total cost
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Samples</CardTitle>
          <AlertCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{summary.total_samples || 0}</div>
          <p className="text-xs text-muted-foreground">
            Across {summary.total_providers || 0} providers
          </p>
        </CardContent>
      </Card>
    </div>
  )
}