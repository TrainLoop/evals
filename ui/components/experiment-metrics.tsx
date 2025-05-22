"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ModelComparisonChart } from "@/components/charts/model-comparison-chart"
import { RadarComparisonChart } from "@/components/charts/radar-comparison-chart"
import { MetricsTrendChart } from "@/components/charts/metrics-trend-chart"

// Sample data for charts
const comparisonData = [
  { metric: "Exact Match", "GPT-4": 72.3, "Claude 3": 68.5, Groq: 70.1, "Llama 3": 65.8 },
  { metric: "Semantic Similarity", "GPT-4": 85.1, "Claude 3": 82.3, Groq: 83.7, "Llama 3": 79.2 },
  { metric: "Factual Accuracy", "GPT-4": 89.7, "Claude 3": 91.2, Groq: 88.5, "Llama 3": 84.3 },
  { metric: "Response Time", "GPT-4": 65.2, "Claude 3": 78.4, Groq: 92.1, "Llama 3": 71.5 },
  { metric: "Tokens Used", "GPT-4": 68.9, "Claude 3": 72.5, Groq: 75.3, "Llama 3": 82.1 },
]

const trendData = [
  { date: "2023-01", "Exact Match": 62.5, "Semantic Similarity": 75.2, "Factual Accuracy": 81.3 },
  { date: "2023-02", "Exact Match": 65.1, "Semantic Similarity": 77.8, "Factual Accuracy": 82.5 },
  { date: "2023-03", "Exact Match": 67.3, "Semantic Similarity": 79.4, "Factual Accuracy": 84.2 },
  { date: "2023-04", "Exact Match": 68.9, "Semantic Similarity": 81.2, "Factual Accuracy": 85.7 },
  { date: "2023-05", "Exact Match": 72.3, "Semantic Similarity": 85.1, "Factual Accuracy": 89.7 },
]

export function ExperimentMetrics() {
  const models = ["GPT-4", "Claude 3", "Groq", "Llama 3"]
  const metrics = ["Exact Match", "Semantic Similarity", "Factual Accuracy"]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Metrics Overview</CardTitle>
        <CardDescription>Detailed metrics for your experiment comparing model performance.</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="chart">
          <TabsList className="mb-4">
            <TabsTrigger value="chart">Chart View</TabsTrigger>
            <TabsTrigger value="radar">Radar View</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="table">Table View</TabsTrigger>
          </TabsList>

          <TabsContent value="chart">
            <ModelComparisonChart
              title="Model Performance Comparison"
              description="Performance across key evaluation metrics"
              data={comparisonData}
              models={models}
            />
          </TabsContent>

          <TabsContent value="radar">
            <RadarComparisonChart
              title="Model Capabilities Radar"
              description="Visualize strengths and weaknesses across metrics"
              data={comparisonData}
              models={models}
            />
          </TabsContent>

          <TabsContent value="trends">
            <MetricsTrendChart
              title="Performance Trends"
              description="How metrics have evolved over time"
              data={trendData}
              metrics={metrics}
            />
          </TabsContent>

          <TabsContent value="table">
            <div className="rounded-md border">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-2 text-left font-medium">Metric</th>
                    <th className="p-2 text-left font-medium">GPT-4</th>
                    <th className="p-2 text-left font-medium">Claude 3</th>
                    <th className="p-2 text-left font-medium">Groq</th>
                    <th className="p-2 text-left font-medium">Llama 3</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="p-2">Exact Match</td>
                    <td className="p-2">72.3%</td>
                    <td className="p-2">68.5%</td>
                    <td className="p-2">70.1%</td>
                    <td className="p-2">65.8%</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-2">Semantic Similarity</td>
                    <td className="p-2">85.1%</td>
                    <td className="p-2">82.3%</td>
                    <td className="p-2">83.7%</td>
                    <td className="p-2">79.2%</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-2">Factual Accuracy</td>
                    <td className="p-2">89.7%</td>
                    <td className="p-2">91.2%</td>
                    <td className="p-2">88.5%</td>
                    <td className="p-2">84.3%</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-2">Response Time</td>
                    <td className="p-2">1.5s</td>
                    <td className="p-2">1.2s</td>
                    <td className="p-2">0.8s</td>
                    <td className="p-2">1.3s</td>
                  </tr>
                  <tr>
                    <td className="p-2">Tokens Used</td>
                    <td className="p-2">2,850</td>
                    <td className="p-2">2,450</td>
                    <td className="p-2">2,250</td>
                    <td className="p-2">2,650</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
