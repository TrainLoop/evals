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

  // Handle DuckDB structure - data might be wrapped in entries
  const summaryData = summary.entries || summary
  const metadataData = metadata.entries || metadata

  // Find best and worst providers
  let bestProvider = { name: '', passRate: 0, cost: 0 }
  let worstProvider = { name: '', passRate: 100, cost: 0 }
  let fastestProvider = { name: '', latency: Infinity }
  let cheapestProvider = { name: '', cost: Infinity }

  const providerSummaries = summaryData.provider_summaries?.entries || summaryData.provider_summaries || {}
  
  Object.entries(providerSummaries).forEach(([provider, stats]: [string, any]) => {
    // Handle stats that might also be wrapped in entries
    const statsData = stats.entries || stats
    const passRate = (statsData.pass_rate || 0) * 100
    
    if (passRate > bestProvider.passRate) {
      bestProvider = { name: provider, passRate: passRate, cost: statsData.total_cost || 0 }
    }
    if (passRate < worstProvider.passRate && statsData.total_evaluations > 0) {
      worstProvider = { name: provider, passRate: passRate, cost: statsData.total_cost || 0 }
    }
    if (statsData.avg_latency_ms > 0 && statsData.avg_latency_ms < fastestProvider.latency) {
      fastestProvider = { name: provider, latency: statsData.avg_latency_ms }
    }
    if (statsData.total_cost >= 0 && statsData.total_cost < cheapestProvider.cost) {
      cheapestProvider = { name: provider, cost: statsData.total_cost }
    }
  })
  
  // Handle cases where no valid data was found
  if (fastestProvider.latency === Infinity) {
    fastestProvider = { name: 'N/A', latency: 0 }
  }
  if (cheapestProvider.cost === Infinity) {
    cheapestProvider = { name: 'N/A', cost: 0 }
  }
  if (!bestProvider.name) {
    bestProvider = { name: 'N/A', passRate: 0, cost: 0 }
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Best Performance</CardTitle>
          <Trophy className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{bestProvider.name || 'N/A'}</div>
          <p className="text-xs text-muted-foreground">
            {bestProvider.name !== 'N/A' ? `${bestProvider.passRate.toFixed(1)}% pass rate` : 'No data'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Fastest Response</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{fastestProvider.name || 'N/A'}</div>
          <p className="text-xs text-muted-foreground">
            {fastestProvider.name !== 'N/A' ? `${fastestProvider.latency.toFixed(0)}ms avg latency` : 'No data'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Most Cost Effective</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{cheapestProvider.name || 'N/A'}</div>
          <p className="text-xs text-muted-foreground">
            {cheapestProvider.name !== 'N/A' ? `$${cheapestProvider.cost.toFixed(4)} total cost` : 'No data'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Samples</CardTitle>
          <AlertCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{summaryData.total_samples || 0}</div>
          <p className="text-xs text-muted-foreground">
            Across {summaryData.total_providers || 0} providers
          </p>
        </CardContent>
      </Card>
    </div>
  )
}