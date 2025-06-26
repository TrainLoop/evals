"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { ChevronRight, CheckCircle, XCircle } from 'lucide-react'

interface BenchmarkResultDetailsProps {
  results: any[]
  metric: string
}

export function BenchmarkResultDetails({ results, metric }: BenchmarkResultDetailsProps) {
  const [selectedResult, setSelectedResult] = useState<any>(null)
  
  return (
    <>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {results.map((result, idx) => (
          <Card key={idx} className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedResult(result)}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium">
                  {result.provider}
                </CardTitle>
                {result.verdict ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-500" />
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Status:</span>
                  <Badge variant={result.verdict ? "default" : "destructive"}>
                    {result.verdict ? 'Passed' : 'Failed'}
                  </Badge>
                </div>
                {result.latency_ms && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Latency:</span>
                    <span className="font-mono">{result.latency_ms}ms</span>
                  </div>
                )}
                {result.cost !== undefined && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Cost:</span>
                    <span className="font-mono">${result.cost.toFixed(4)}</span>
                  </div>
                )}
              </div>
              <Button variant="ghost" size="sm" className="w-full mt-3">
                View Details <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={!!selectedResult} onOpenChange={() => setSelectedResult(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>
              {selectedResult?.provider} - {metric} Evaluation
            </DialogTitle>
            <DialogDescription>
              Detailed evaluation results and response content
            </DialogDescription>
          </DialogHeader>
          
          {selectedResult && (
            <ScrollArea className="h-[60vh] pr-4">
              <div className="space-y-4">
                {/* Response Content */}
                <div>
                  <h4 className="font-medium mb-2">Response:</h4>
                  <div className="bg-muted p-3 rounded-md">
                    <pre className="whitespace-pre-wrap text-sm">
                      {selectedResult.response || 'No response'}
                    </pre>
                  </div>
                </div>
                
                {/* Evaluation Results */}
                {selectedResult.metric_results && (
                  <div>
                    <h4 className="font-medium mb-2">Evaluation Details:</h4>
                    <div className="space-y-2">
                      {Object.entries(selectedResult.metric_results).map(([metricName, result]: [string, any]) => (
                        <div key={metricName} className="flex items-center justify-between p-2 border rounded">
                          <span className="text-sm font-medium">{metricName}</span>
                          <div className="flex items-center gap-2">
                            {result.passed ? (
                              <Badge variant="default">Passed</Badge>
                            ) : (
                              <Badge variant="destructive">Failed</Badge>
                            )}
                            {result.error && (
                              <span className="text-xs text-red-500">{result.error}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Failure Reason */}
                {selectedResult.reason && (
                  <div>
                    <h4 className="font-medium mb-2">Failure Reason:</h4>
                    <div className="bg-destructive/10 text-destructive p-3 rounded-md">
                      <p className="text-sm">{selectedResult.reason}</p>
                    </div>
                  </div>
                )}
                
                {/* Model Parameters */}
                {selectedResult.model_params && (
                  <div>
                    <h4 className="font-medium mb-2">Model Parameters:</h4>
                    <div className="bg-muted p-3 rounded-md">
                      <pre className="text-sm">
                        {JSON.stringify(selectedResult.model_params, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}