"use client"

import { useState } from "react"
import { ResponsiveLine } from "@nivo/line"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface ProgressTimelineChartProps {
  title: string
  description?: string
  data: {
    scope: Array<{ x: string; y: number }>
    started: Array<{ x: string; y: number }>
    completed: Array<{ x: string; y: number }>
  }
  currentDate: string
  endDate: string
  className?: string
}

export function ProgressTimelineChart({
  title,
  description,
  data,
  currentDate,
  endDate,
  className,
}: ProgressTimelineChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<{ serieId: string; data: { x: string; y: number } } | null>(null)

  // Find the current values for scope, started, and completed
  const currentScope = data.scope.find((d) => d.x === currentDate)?.y || 0
  const currentStarted = data.started.find((d) => d.x === currentDate)?.y || 0
  const currentCompleted = data.completed.find((d) => d.x === currentDate)?.y || 0

  // Calculate percentages
  const startedPercentage = currentScope > 0 ? Math.round((currentStarted / currentScope) * 100) : 0
  const completedPercentage = currentScope > 0 ? Math.round((currentCompleted / currentScope) * 100) : 0

  // Format the chart data for Nivo
  const chartData = [
    {
      id: "Scope",
      data: data.scope,
      color: "#94a3b8", // slate-400
    },
    {
      id: "Started",
      data: data.started,
      color: "#fbbf24", // amber-400
    },
    {
      id: "Completed",
      data: data.completed,
      color: "#3b82f6", // blue-500
    },
  ]

  // Find the max Y value for the chart
  const maxY = Math.max(...data.scope.map((d) => d.y)) * 1.1

  // Custom layer to render the current date line and future area
  const CustomLayer = ({ xScale, yScale, innerHeight }: any) => {
    if (!xScale || !yScale) return null

    const currentX = xScale(currentDate)
    const endX = xScale(endDate)
    const width = endX - currentX

    return (
      <g>
        {/* Current date line */}
        <line
          x1={currentX}
          y1={0}
          x2={currentX}
          y2={innerHeight}
          stroke="#ef4444" // red-500
          strokeWidth={1}
        />

        {/* Future area (striped pattern) */}
        <defs>
          <pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="8" height="8">
            <path
              d="M-2,2 l4,-4 M0,8 l8,-8 M6,10 l4,-4"
              stroke="#ef444433" // red-500 with opacity
              strokeWidth={1}
            />
          </pattern>
        </defs>
        <rect x={currentX} y={0} width={width} height={innerHeight} fill="url(#diagonalHatch)" fillOpacity={0.5} />

        {/* Blue area between Started and Completed */}
        <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
          <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.1} />
        </linearGradient>
      </g>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          <div className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className="text-sm text-muted-foreground">Scope</div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold">{currentScope}</span>
              </div>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-sm text-muted-foreground">Started</div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold">{currentStarted}</span>
                <Badge variant="outline" className="text-amber-500">
                  {startedPercentage}%
                </Badge>
              </div>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-sm text-muted-foreground">Completed</div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold">{currentCompleted}</span>
                <Badge variant="outline" className="text-blue-500">
                  {completedPercentage}%
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveLine
            data={chartData}
            margin={{ top: 20, right: 20, bottom: 50, left: 60 }}
            xScale={{
              type: "point",
            }}
            yScale={{
              type: "linear",
              min: 0,
              max: maxY,
            }}
            curve="monotoneX"
            axisBottom={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: "Date",
              legendOffset: 36,
              legendPosition: "middle",
            }}
            axisLeft={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: "Count",
              legendOffset: -40,
              legendPosition: "middle",
            }}
            colors={(d) => d.color}
            pointSize={10}
            pointColor={{ theme: "background" }}
            pointBorderWidth={2}
            pointBorderColor={{ from: "serieColor" }}
            pointLabelYOffset={-12}
            enableArea={true}
            areaOpacity={0.1}
            useMesh={true}
            enableSlices="x"
            layers={["grid", "markers", "axes", "areas", "lines", CustomLayer, "points", "slices", "mesh", "legends"]}
            theme={{
              axis: {
                ticks: {
                  text: {
                    fontSize: 12,
                  },
                },
              },
            }}
            legends={[
              {
                anchor: "bottom",
                direction: "row",
                justify: false,
                translateX: 0,
                translateY: 50,
                itemsSpacing: 0,
                itemDirection: "left-to-right",
                itemWidth: 80,
                itemHeight: 20,
                itemOpacity: 0.75,
                symbolSize: 12,
                symbolShape: "circle",
                symbolBorderColor: "rgba(0, 0, 0, .5)",
              },
            ]}
            onMouseMove={(point) => {
              if (point.data) {
                setHoveredPoint({
                  serieId: point.serieId as string,
                  data: { x: point.data.x as string, y: point.data.y as number },
                })
              }
            }}
            onMouseLeave={() => setHoveredPoint(null)}
          />
        </div>
      </CardContent>
    </Card>
  )
}
