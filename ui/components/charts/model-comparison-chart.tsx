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
  const generateConfig = () => {
    const colors = [
      "hsl(var(--chart-1))",
      "hsl(var(--chart-2))",
      "hsl(var(--chart-3))",
      "hsl(var(--chart-4))",
      "hsl(var(--chart-5))",
    ]

    return models.reduce(
      (config, model, index) => {
        config[model] = {
          label: model,
          color: colors[index % colors.length],
        }
        return config
      },
      {} as Record<string, { label: string; color: string }>,
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <ChartContainer config={generateConfig()} className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="metric" angle={-45} textAnchor="end" height={70} tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Legend />
              {models.map((model, index) => (
                <Bar
                  key={model}
                  dataKey={model}
                  name={model}
                  stroke={`var(--color-${model})`}
                  fill={`var(--color-${model})`}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
