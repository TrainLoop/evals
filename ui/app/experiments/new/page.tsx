"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardShell } from "@/components/dashboard-shell"
import { ArrowLeft } from "lucide-react"
import { SimpleCanvas } from "@/components/flow-editor/simple-canvas"

export default function NewExperimentPage() {
  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([])

  const availableModels = [
    { id: "gpt-4", name: "GPT-4" },
    { id: "claude-3", name: "Claude 3" },
    { id: "llama-3", name: "Llama 3" },
    { id: "mistral", name: "Mistral" },
    { id: "gemini", name: "Gemini" },
    { id: "groq", name: "Groq" }, // Added Groq as an available model
  ]

  const availableMetrics = [
    { id: "exactMatch", name: "Exact Match" },
    { id: "semanticSimilarity", name: "Semantic Similarity" },
    { id: "factualAccuracy", name: "Factual Accuracy" },
    { id: "responseTime", name: "Response Time" },
    { id: "tokensUsed", name: "Tokens Used" },
  ]

  const toggleModel = (modelId: string) => {
    setSelectedModels((prev) => (prev.includes(modelId) ? prev.filter((id) => id !== modelId) : [...prev, modelId]))
  }

  const toggleMetric = (metricId: string) => {
    setSelectedMetrics((prev) => (prev.includes(metricId) ? prev.filter((id) => id !== metricId) : [...prev, metricId]))
  }

  return (
    <DashboardShell>
      <Link href="/" className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Dashboard
      </Link>

      <DashboardHeader heading="Create New Experiment" text="Set up a new LLM evaluation experiment." />

      <Tabs defaultValue="basic" className="mt-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="basic">Basic Setup</TabsTrigger>
          <TabsTrigger value="workflow">Workflow Editor</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="mt-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card className="col-span-full">
              <CardHeader>
                <CardTitle>Experiment Details</CardTitle>
                <CardDescription>Provide basic information about your experiment.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Experiment Name</Label>
                    <Input id="name" placeholder="E.g., GPT-4 vs Claude 3 Comparison" />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea id="description" placeholder="Describe the purpose of this experiment..." />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Select Models</CardTitle>
                <CardDescription>Choose the models you want to evaluate.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  {availableModels.map((model) => (
                    <div key={model.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`model-${model.id}`}
                        checked={selectedModels.includes(model.id)}
                        onCheckedChange={() => toggleModel(model.id)}
                      />
                      <Label htmlFor={`model-${model.id}`}>{model.name}</Label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Select Metrics</CardTitle>
                <CardDescription>Choose the metrics to evaluate performance.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  {availableMetrics.map((metric) => (
                    <div key={metric.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`metric-${metric.id}`}
                        checked={selectedMetrics.includes(metric.id)}
                        onCheckedChange={() => toggleMetric(metric.id)}
                      />
                      <Label htmlFor={`metric-${metric.id}`}>{metric.name}</Label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data Source</CardTitle>
                <CardDescription>Select or upload your evaluation dataset.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="data-source">Source Type</Label>
                    <Select>
                      <SelectTrigger id="data-source">
                        <SelectValue placeholder="Select data source" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="upload">Upload CSV/JSON</SelectItem>
                        <SelectItem value="api">Connect API</SelectItem>
                        <SelectItem value="manual">Manual Entry</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="upload">Upload File</Label>
                    <Input id="upload" type="file" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="workflow" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Editor</CardTitle>
              <CardDescription>
                Design your evaluation workflow by adding and connecting nodes. Click on the canvas to add a new node.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SimpleCanvas />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="mt-6 flex justify-end">
        <Button variant="outline" className="mr-2">
          Cancel
        </Button>
        <Button>Create Experiment</Button>
      </div>
    </DashboardShell>
  )
}
