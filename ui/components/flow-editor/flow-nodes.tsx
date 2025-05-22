"use client"

import type React from "react"

import { Handle, Position, type NodeProps } from "reactflow"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { LucideIcon } from "lucide-react"
import * as Icons from "lucide-react"

export interface NodeData {
  label: string
  description: string
  icon: string
}

const NodeWrapper = ({
  children,
  type,
  data,
  isConnectable,
}: {
  children: React.ReactNode
  type: string
  data: NodeData
  isConnectable: boolean
}) => {
  // Dynamically get the icon component
  const IconComponent = (Icons as Record<string, LucideIcon>)[data.icon] || Icons.Circle

  return (
    <Card className={`w-64 shadow-md ${getNodeColor(type)}`}>
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
        {children}
      </CardContent>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-primary border-2 border-background"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-primary border-2 border-background"
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

export function DataNode({ data, isConnectable }: NodeProps<NodeData>) {
  return (
    <NodeWrapper type="dataNode" data={data} isConnectable={isConnectable}>
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
    </NodeWrapper>
  )
}

export function CallNode({ data, isConnectable }: NodeProps<NodeData>) {
  return (
    <NodeWrapper type="callNode" data={data} isConnectable={isConnectable}>
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
    </NodeWrapper>
  )
}

export function ToolNode({ data, isConnectable }: NodeProps<NodeData>) {
  return (
    <NodeWrapper type="toolNode" data={data} isConnectable={isConnectable}>
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
    </NodeWrapper>
  )
}
