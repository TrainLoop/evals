import Link from "next/link"
import { Button } from "@/components/ui/button"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardShell } from "@/components/dashboard-shell"
import { ProgressTimelineChart } from "@/components/charts/progress-timeline-chart"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft } from "lucide-react"

// Sample data for the progress chart
const progressData = {
  scope: [
    { x: "Jan 22", y: 20 },
    { x: "Feb 5", y: 35 },
    { x: "Feb 19", y: 45 },
    { x: "Mar 5", y: 55 },
    { x: "Mar 19", y: 65 },
    { x: "Apr 2", y: 75 },
    { x: "Apr 16", y: 80 },
    { x: "Apr 30", y: 85 },
    { x: "May 7", y: 86 },
    { x: "May 14", y: 86 },
    { x: "May 28", y: 86 },
    { x: "Jun 11", y: 86 },
    { x: "Jun 25", y: 86 },
    { x: "Jul 9", y: 86 },
    { x: "Jul 23", y: 86 },
    { x: "Jul 31", y: 86 },
  ],
  started: [
    { x: "Jan 22", y: 0 },
    { x: "Feb 5", y: 5 },
    { x: "Feb 19", y: 12 },
    { x: "Mar 5", y: 18 },
    { x: "Mar 19", y: 25 },
    { x: "Apr 2", y: 32 },
    { x: "Apr 16", y: 38 },
    { x: "Apr 30", y: 45 },
    { x: "May 7", y: 50 },
    { x: "May 14", y: 55 },
    { x: "May 28", y: 65 },
    { x: "Jun 11", y: 75 },
    { x: "Jun 25", y: 80 },
    { x: "Jul 9", y: 85 },
    { x: "Jul 23", y: 86 },
    { x: "Jul 31", y: 86 },
  ],
  completed: [
    { x: "Jan 22", y: 0 },
    { x: "Feb 5", y: 0 },
    { x: "Feb 19", y: 5 },
    { x: "Mar 5", y: 10 },
    { x: "Mar 19", y: 15 },
    { x: "Apr 2", y: 22 },
    { x: "Apr 16", y: 28 },
    { x: "Apr 30", y: 35 },
    { x: "May 7", y: 42 },
    { x: "May 14", y: 48 },
    { x: "May 28", y: 55 },
    { x: "Jun 11", y: 65 },
    { x: "Jun 25", y: 75 },
    { x: "Jul 9", y: 80 },
    { x: "Jul 23", y: 85 },
    { x: "Jul 31", y: 86 },
  ],
}

// Sample data for experiments timeline
const experimentsTimeline = [
  {
    id: "exp-001",
    name: "GPT-4 vs Claude 3",
    startDate: "Feb 5",
    endDate: "Feb 19",
    status: "completed",
  },
  {
    id: "exp-002",
    name: "Llama 3 Evaluation",
    startDate: "Mar 5",
    endDate: "Mar 19",
    status: "completed",
  },
  {
    id: "exp-003",
    name: "Mistral vs Gemini",
    startDate: "Apr 2",
    endDate: "Apr 16",
    status: "completed",
  },
  {
    id: "exp-004",
    name: "Groq Performance Analysis",
    startDate: "Apr 30",
    endDate: "May 14",
    status: "in-progress",
  },
  {
    id: "exp-005",
    name: "Multi-model Comparison",
    startDate: "May 28",
    endDate: "Jun 11",
    status: "planned",
  },
]

export default function TimelinePage() {
  return (
    <DashboardShell>
      <Link href="/" className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Dashboard
      </Link>

      <DashboardHeader
        heading="Evaluation Timeline"
        text="Track the progress of your LLM evaluation experiments over time."
      >
        <Button variant="outline">Export Timeline</Button>
      </DashboardHeader>

      <Tabs defaultValue="progress" className="mt-6">
        <TabsList>
          <TabsTrigger value="progress">Progress Chart</TabsTrigger>
          <TabsTrigger value="experiments">Experiments Timeline</TabsTrigger>
        </TabsList>
        <TabsContent value="progress" className="mt-4">
          <ProgressTimelineChart
            title="Evaluation Progress"
            description="Track the scope, started, and completed evaluations over time"
            data={progressData}
            currentDate="May 7"
            endDate="Jul 31"
            className="w-full"
          />
        </TabsContent>
        <TabsContent value="experiments" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Experiments Timeline</CardTitle>
              <CardDescription>Chronological view of all evaluation experiments</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-16 top-0 bottom-0 w-0.5 bg-border" />

                {/* Timeline items */}
                <div className="space-y-8">
                  {experimentsTimeline.map((experiment) => (
                    <div key={experiment.id} className="relative flex items-start">
                      {/* Date */}
                      <div className="min-w-32 pr-4 text-sm text-right text-muted-foreground">
                        {experiment.startDate} - {experiment.endDate}
                      </div>

                      {/* Circle */}
                      <div
                        className={`absolute left-16 -translate-x-1/2 w-4 h-4 rounded-full border-2 border-background ${
                          experiment.status === "completed"
                            ? "bg-green-500"
                            : experiment.status === "in-progress"
                              ? "bg-blue-500"
                              : "bg-gray-300"
                        }`}
                      />

                      {/* Content */}
                      <div className="ml-8 pb-2">
                        <div className="font-medium">{experiment.name}</div>
                        <div className="text-sm text-muted-foreground capitalize">{experiment.status}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </DashboardShell>
  )
}
