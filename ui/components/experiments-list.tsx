"use client"

import { useState } from "react"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MoreHorizontal, BarChart3, FileText, Filter } from "lucide-react"

// Mock data for experiments
const experiments = [
  {
    id: "exp-001",
    name: "GPT-4 vs Claude 3",
    description: "Comparing response quality on customer service queries",
    created: "2023-05-01",
    status: "completed",
    models: ["GPT-4", "Claude 3"],
    metrics: {
      exactMatch: 68.5,
      semanticSimilarity: 82.3,
      factualAccuracy: 91.2,
    },
  },
  {
    id: "exp-002",
    name: "Llama 3 Evaluation",
    description: "Evaluating Llama 3 on coding tasks",
    created: "2023-05-03",
    status: "in-progress",
    models: ["Llama 3", "GPT-4", "Claude 3"],
    metrics: {
      exactMatch: 42.1,
      semanticSimilarity: 76.8,
      factualAccuracy: 84.5,
    },
  },
  {
    id: "exp-003",
    name: "Mistral vs Gemini",
    description: "Comparing reasoning capabilities",
    created: "2023-05-05",
    status: "completed",
    models: ["Mistral", "Gemini"],
    metrics: {
      exactMatch: 58.9,
      semanticSimilarity: 79.4,
      factualAccuracy: 88.7,
    },
  },
]

export function ExperimentsList() {
  const [activeTab, setActiveTab] = useState("all")

  const filteredExperiments = activeTab === "all" ? experiments : experiments.filter((exp) => exp.status === activeTab)

  return (
    <Tabs defaultValue="all" className="w-full" onValueChange={setActiveTab}>
      <div className="flex items-center justify-between">
        <TabsList>
          <TabsTrigger value="all">All Experiments</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="in-progress">In Progress</TabsTrigger>
        </TabsList>
        <Button variant="outline" size="sm" className="ml-auto">
          <Filter className="mr-2 h-4 w-4" />
          Filter
        </Button>
      </div>
      <TabsContent value="all" className="mt-0">
        <Card>
          <CardHeader>
            <CardTitle>Experiments</CardTitle>
            <CardDescription>View and manage your LLM evaluation experiments.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Models</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Top Metric</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredExperiments.map((experiment) => (
                  <TableRow key={experiment.id}>
                    <TableCell className="font-medium">
                      <Link href={`/experiments/${experiment.id}`} className="hover:underline">
                        {experiment.name}
                      </Link>
                      <p className="text-sm text-muted-foreground">{experiment.description}</p>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {experiment.models.map((model) => (
                          <Badge key={model} variant="outline">
                            {model}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={experiment.status === "completed" ? "default" : "secondary"}>
                        {experiment.status === "completed" ? "Completed" : "In Progress"}
                      </Badge>
                    </TableCell>
                    <TableCell>{experiment.created}</TableCell>
                    <TableCell>
                      {Object.entries(experiment.metrics)
                        .sort(([, a], [, b]) => b - a)
                        .map(([key, value], index) =>
                          index === 0 ? (
                            <div key={key} className="flex items-center">
                              <span className="font-medium">{key.replace(/([A-Z])/g, " $1").trim()}</span>
                              <span className="ml-2 text-emerald-600 font-bold">{value.toFixed(1)}%</span>
                            </div>
                          ) : null,
                        )}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Open menu</span>
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem>
                            <FileText className="mr-2 h-4 w-4" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <BarChart3 className="mr-2 h-4 w-4" />
                            View Results
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem>Delete</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="completed" className="mt-0">
        <Card>
          <CardHeader>
            <CardTitle>Completed Experiments</CardTitle>
            <CardDescription>View all your completed LLM evaluation experiments.</CardDescription>
          </CardHeader>
          <CardContent>{/* Same table structure as above, but filtered for completed experiments */}</CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="in-progress" className="mt-0">
        <Card>
          <CardHeader>
            <CardTitle>In-Progress Experiments</CardTitle>
            <CardDescription>View all your ongoing LLM evaluation experiments.</CardDescription>
          </CardHeader>
          <CardContent>{/* Same table structure as above, but filtered for in-progress experiments */}</CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  )
}
