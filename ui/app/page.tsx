import DashboardContent from '@/components/dashboard/dashboard-content'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { RecentEvents } from '@/components/dashboard/recent-events'
import { RecentResults } from '@/components/dashboard/recent-results'

async function getData() {
  // This would ideally come from an API but for now we'll use placeholder data
  return {
    totalEvents: 328,
    totalSuites: 5,
    totalMetrics: 12,
    passRate: 92.4,
    recentActivity: true
  }
}

export default async function DashboardPage() {
  const data = await getData()

  return (
    <>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">TrainLoop Evaluations Dashboard</h1>
      </div>

      {/* New Dashboard Data Visualization */}
      <div className="mb-8">
        <DashboardContent />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Events</CardTitle>
            <CardDescription>Latest model interactions collected</CardDescription>
          </CardHeader>
          <CardContent>
            <RecentEvents />
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Evaluation Results</CardTitle>
            <CardDescription>Recent model evaluation metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <RecentResults />
          </CardContent>
        </Card>
      </div>
    </>
  )
}
