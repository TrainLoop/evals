import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardShell } from "@/components/dashboard-shell"
import { ExperimentMetrics } from "@/components/experiment-metrics"
import { ExperimentResponses } from "@/components/experiment-responses"
import { ArrowLeft } from "lucide-react"
import { RadarComparisonChart } from "@/components/charts/radar-comparison-chart"

// Mock data for a single experiment
const experiment = {
  id: "exp-001",
  name: "GPT-4 vs Claude 3 vs Groq",
  description: "Comparing response quality on customer service queries",
  created: "2023-05-01",
  status: "completed",
  models: ["GPT-4", "Claude 3", "Groq"],
  metrics: {
    exactMatch: 68.5,
    semanticSimilarity: 82.3,
    factualAccuracy: 91.2,
    responseTime: 1.2,
    tokensUsed: 2450,
  },
}

// Sample data for the radar chart
const radarData = [
  { metric: "Exact Match", "GPT-4": 72.3, "Claude 3": 68.5, Groq: 70.1 },
  { metric: "Semantic Similarity", "GPT-4": 85.1, "Claude 3": 82.3, Groq: 83.7 },
  { metric: "Factual Accuracy", "GPT-4": 89.7, "Claude 3": 91.2, Groq: 88.5 },
  { metric: "Response Time", "GPT-4": 65.2, "Claude 3": 78.4, Groq: 92.1 },
  { metric: "Tokens Used", "GPT-4": 68.9, "Claude 3": 72.5, Groq: 75.3 },
]

export default function ExperimentPage({ params }: { params: { id: string } }) {
  // In a real app, you would fetch the experiment data based on params.id

  return (
    <DashboardShell>
      <Link href="/" className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Dashboard
      </Link>

      <DashboardHeader heading={experiment.name} text={experiment.description}>
        <div className="flex items-center gap-2">
          <Badge variant={experiment.status === "completed" ? "default" : "secondary"}>
            {experiment.status === "completed" ? "Completed" : "In Progress"}
          </Badge>
          <Button variant="outline">Export Results</Button>
        </div>
      </DashboardHeader>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mt-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Exact Match</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{experiment.metrics.exactMatch.toFixed(1)}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Semantic Similarity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{experiment.metrics.semanticSimilarity.toFixed(1)}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Factual Accuracy</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{experiment.metrics.factualAccuracy.toFixed(1)}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{experiment.metrics.responseTime.toFixed(1)}s</div>
          </CardContent>
        </Card>
      </div>

      {/* Add radar chart for quick overview */}
      <div className="mt-6">
        <RadarComparisonChart
          title="Model Performance Overview"
          description="Comparison across all evaluation metrics"
          data={radarData}
          models={["GPT-4", "Claude 3", "Groq"]}
        />
      </div>

      <Tabs defaultValue="metrics" className="mt-6">
        <TabsList>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="responses">Responses</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        <TabsContent value="metrics" className="mt-4">
          <ExperimentMetrics />
        </TabsContent>
        <TabsContent value="responses" className="mt-4">
          <ExperimentResponses />
        </TabsContent>
        <TabsContent value="settings" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Experiment Settings</CardTitle>
              <CardDescription>Configure your experiment settings and parameters.</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Settings content would go here...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </DashboardShell>
  )
}
