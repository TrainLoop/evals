"use client"

import type React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { LucideIcon } from "lucide-react"
import * as Icons from "lucide-react"

interface NodeProps {
  id: string
  type: "dataNode" | "callNode" | "toolNode"
  data: {
    label: string
    description: string
    icon: string
  }
  onDragStart: (event: React.MouseEvent) => void
  onConnectStart: () => void
  onConnectEnd: () => void
}

export function SimpleNode({ id, type, data, onDragStart, onConnectStart, onConnectEnd }: NodeProps) {
  // Dynamically get the icon component
  const IconComponent = (Icons as Record<string, LucideIcon>)[data.icon] || Icons.Circle

  // Special content for call nodes that includes Groq
  const getCallNodeContent = () => {
    if (type === "callNode") {
      return (
        <div className="mt-2 grid grid-cols-1 gap-1 text-xs">
          <div className="flex items-center">
            <Icons.Bot className="mr-1 h-3 w-3" />
            <span>Models: GPT-4, Groq</span>
          </div>
          <div className="flex items-center">
            <Icons.Thermometer className="mr-1 h-3 w-3" />
            <span>Temperature: 0.7</span>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <Card className={`w-64 shadow-md ${getNodeColor(type)}`} onMouseDown={onDragStart}>
      <CardHeader className="p-3 pb-0">
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="text-xs">
            {type.replace("Node", "")}
          </Badge>
          <IconComponent className="h-4 w-4 text-muted-foreground" />
        </div>
        <CardTitle className="text-sm font-medium mt-1">{data.label}</CardTitle>
      </CardHeader>
      <CardContent className="p-3 pt-1">
        <p className="text-xs text-muted-foreground">{data.description}</p>

        {type === "dataNode" && (
          <div className="mt-2 grid grid-cols-2 gap-1 text-xs">
            <div className="flex items-center">
              <Icons.FileJson className="mr-1 h-3 w-3" />
              <span>dataset.json</span>
            </div>
            <div className="flex items-center">
              <Icons.ListFilter className="mr-1 h-3 w-3" />
              <span>50 samples</span>
            </div>
          </div>
        )}

        {getCallNodeContent() ||
          (type === "callNode" && (
            <div className="mt-2 grid grid-cols-1 gap-1 text-xs">
              <div className="flex items-center">
                <Icons.Bot className="mr-1 h-3 w-3" />
                <span>Model: GPT-4</span>
              </div>
              <div className="flex items-center">
                <Icons.Thermometer className="mr-1 h-3 w-3" />
                <span>Temperature: 0.7</span>
              </div>
            </div>
          ))}

        {type === "toolNode" && (
          <div className="mt-2 grid grid-cols-1 gap-1 text-xs">
            <div className="flex items-center">
              <Icons.BarChart3 className="mr-1 h-3 w-3" />
              <span>Metric: Semantic Similarity</span>
            </div>
            <div className="flex items-center">
              <Icons.Settings className="mr-1 h-3 w-3" />
              <span>Threshold: 0.8</span>
            </div>
          </div>
        )}
      </CardContent>

      {/* Connection handles */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-primary rounded-full cursor-pointer border-2 border-background"
        onMouseUp={onConnectEnd}
      />
      <div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-primary rounded-full cursor-pointer border-2 border-background"
        onMouseDown={(e) => {
          e.stopPropagation()
          onConnectStart()
        }}
      />
    </Card>
  )
}

function getNodeColor(type: string): string {
  switch (type) {
    case "dataNode":
      return "border-blue-200 bg-blue-50 dark:bg-blue-950 dark:border-blue-900"
    case "callNode":
      return "border-green-200 bg-green-50 dark:bg-green-950 dark:border-green-900"
    case "toolNode":
      return "border-amber-200 bg-amber-50 dark:bg-amber-950 dark:border-amber-900"
    default:
      return ""
  }
}
