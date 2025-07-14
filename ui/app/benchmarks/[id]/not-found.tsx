import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileQuestion, ChevronLeft } from 'lucide-react'

export default function BenchmarkNotFound() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/benchmarks">
          <Button variant="ghost" size="sm">
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back to Benchmarks
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <FileQuestion className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Benchmark Not Found</CardTitle>
          </div>
          <CardDescription>
            The benchmark run you&apos;re looking for doesn&apos;t exist or has been removed.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            This could happen if:
          </p>
          <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1 mb-4">
            <li>The benchmark ID is incorrect</li>
            <li>The benchmark data has been deleted</li>
            <li>You don&apos;t have access to this benchmark</li>
          </ul>
          <Link href="/benchmarks">
            <Button variant="outline">
              View All Benchmarks
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}