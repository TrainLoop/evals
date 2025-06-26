"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

interface BenchmarkResult {
  provider: string
  metric: string
  score: number
  passed: number
  total: number
}

interface BenchmarkRun {
  id: string
  timestamp: string
  results: BenchmarkResult[]
}

interface BenchmarkDetailsProps {
  benchmarkRun: BenchmarkRun
}

export function BenchmarkDetails({ benchmarkRun }: BenchmarkDetailsProps) {
  // Group results by metric
  const resultsByMetric = benchmarkRun.results.reduce((acc, result) => {
    if (!acc[result.metric]) {
      acc[result.metric] = []
    }
    acc[result.metric].push(result)
    return acc
  }, {} as Record<string, BenchmarkResult[]>)

  return (
    <div className="space-y-6">
      {Object.entries(resultsByMetric).map(([metric, results]) => (
        <Card key={metric}>
          <CardHeader>
            <CardTitle>{metric}</CardTitle>
            <CardDescription>
              Performance comparison across providers
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Provider</TableHead>
                  <TableHead>Pass Rate</TableHead>
                  <TableHead>Passed / Total</TableHead>
                  <TableHead className="w-[200px]">Progress</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results
                  .sort((a, b) => b.score - a.score)
                  .map((result) => (
                    <TableRow key={`${result.provider}-${result.metric}`}>
                      <TableCell className="font-medium">
                        {result.provider}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={result.score >= 80 ? "default" : result.score >= 60 ? "secondary" : "destructive"}
                        >
                          {result.score.toFixed(1)}%
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {result.passed} / {result.total}
                      </TableCell>
                      <TableCell>
                        <Progress value={result.score} className="h-2" />
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}