"use client"

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer } from "@/components/ui/chart"

interface RadarComparisonChartProps {
  title: string
  description?: string
  data: Array<{
    metric: string
    [key: string]: string | number
  }>
  models: string[]
  className?: string
}

export function RadarComparisonChart({ title, description, data, models, className }: RadarComparisonChartProps) {
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
            <RadarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
              {models.map((model) => (
                <Radar
                  key={model}
                  name={model}
                  dataKey={model}
                  stroke={`var(--color-${model})`}
                  fill={`var(--color-${model})`}
                  fillOpacity={0.3}
                />
              ))}
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
