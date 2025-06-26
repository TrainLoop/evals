"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

interface ModelComparisonChartProps {
  title: string
  description?: string
  data: Array<{
    metric: string
    [key: string]: string | number
  }>
  models: string[]
  className?: string
}

export function ModelComparisonChart({ title, description, data, models, className }: ModelComparisonChartProps) {
  // Generate a config object for ChartContainer with dynamic model colors
  const colors = [
    "hsl(var(--chart-1))",
    "hsl(var(--chart-2))",
    "hsl(var(--chart-3))",
    "hsl(var(--chart-4))",
    "hsl(var(--chart-5))",
  ]
  
  const chartConfig = models.reduce(
    (config, model, index) => {
      config[model] = {
        label: model,
        color: colors[index % colors.length],
      }
      return config
    },
    {} as Record<string, { label: string; color: string }>,
  )

  return (
    <Card className={className}>
      <CardHeader className="text-center">
        <CardTitle className="text-xl">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent className="pt-0">
        <ChartContainer config={chartConfig} className="h-[500px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 40, bottom: 100 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis 
                dataKey="metric" 
                angle={-45} 
                textAnchor="end" 
                height={100} 
                tick={{ fontSize: 12 }}
                interval={0}
              />
              <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              {models.map((model, index) => {
                const colorIndex = index % colors.length + 1
                return (
                  <Bar
                    key={model}
                    dataKey={model}
                    name={model}
                    fill={`hsl(var(--chart-${colorIndex}))`}
                    radius={[4, 4, 0, 0]}
                  />
                )
              })}
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
