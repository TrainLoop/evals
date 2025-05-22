"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Database, MessageSquare, BarChart3, X } from "lucide-react"

interface NodeSelectorProps {
  position: { x: number; y: number }
  onSelect: (nodeType: string) => void
  onClose: () => void
}

export function NodeSelector({ position, onSelect, onClose }: NodeSelectorProps) {
  const nodeTypes = [
    {
      type: "dataNode",
      label: "Data Source",
      icon: <Database className="h-4 w-4 mr-2" />,
      description: "Input data for evaluation",
    },
    {
      type: "callNode",
      label: "Model Call",
      icon: <MessageSquare className="h-4 w-4 mr-2" />,
      description: "Call an LLM API (Groq, GPT-4, etc.)",
    },
    {
      type: "toolNode",
      label: "Evaluation Tool",
      icon: <BarChart3 className="h-4 w-4 mr-2" />,
      description: "Analyze and score responses",
    },
  ]

  return (
    <div
      className="absolute z-10"
      style={{
        left: position.x,
        top: position.y,
      }}
      onClick={(e) => e.stopPropagation()}
    >
      <Card className="w-64 shadow-lg">
        <div className="flex items-center justify-between p-2 border-b">
          <h3 className="text-sm font-medium">Add Node</h3>
          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardContent className="p-2">
          <div className="grid gap-1">
            {nodeTypes.map((node) => (
              <Button
                key={node.type}
                variant="ghost"
                className="justify-start h-auto py-2 px-2 text-left"
                onClick={() => onSelect(node.type)}
              >
                <div className="flex items-center">
                  {node.icon}
                  <div>
                    <div className="font-medium text-sm">{node.label}</div>
                    <div className="text-xs text-muted-foreground">{node.description}</div>
                  </div>
                </div>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
