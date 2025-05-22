"use client"

import type React from "react"

import { useCallback, useRef, useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { PlusCircle, Save } from "lucide-react"
import { SimpleNode } from "./simple-node"
import { NodeSelector } from "./node-selector"

export interface NodeItem {
  id: string
  type: "dataNode" | "callNode" | "toolNode"
  position: { x: number; y: number }
  data: {
    label: string
    description: string
    icon: string
  }
}

export interface EdgeItem {
  id: string
  source: string
  target: string
}

const initialNodes: NodeItem[] = [
  {
    id: "1",
    type: "dataNode",
    position: { x: 250, y: 100 },
    data: {
      label: "Input Dataset",
      description: "Evaluation prompts and expected outputs",
      icon: "Database",
    },
  },
]

const initialEdges: EdgeItem[] = []

export function SimpleCanvas() {
  const canvasRef = useRef<HTMLDivElement>(null)
  const [nodes, setNodes] = useState<NodeItem[]>(initialNodes)
  const [edges, setEdges] = useState<EdgeItem[]>(initialEdges)
  const [showNodeSelector, setShowNodeSelector] = useState(false)
  const [nodeSelectorPosition, setNodeSelectorPosition] = useState({ x: 0, y: 0 })
  const [draggedNode, setDraggedNode] = useState<string | null>(null)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null)
  const [canvasOffset, setCanvasOffset] = useState({ x: 0, y: 0 })
  const [canvasScale, setCanvasScale] = useState(1)

  // Update canvas offset when component mounts
  useEffect(() => {
    if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect()
      setCanvasOffset({ x: rect.left, y: rect.top })
    }
  }, [])

  const onCanvasClick = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      if (connectingFrom) {
        // Cancel connection if clicking on empty canvas
        setConnectingFrom(null)
        return
      }

      if (canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect()
        const position = {
          x: (event.clientX - rect.left) / canvasScale,
          y: (event.clientY - rect.top) / canvasScale,
        }
        setNodeSelectorPosition(position)
        setShowNodeSelector(true)
      }
    },
    [connectingFrom, canvasScale],
  )

  const onAddNode = useCallback(
    (nodeType: string) => {
      let newNodeData = {
        label: "",
        description: "",
        icon: "Circle",
      }

      switch (nodeType) {
        case "dataNode":
          newNodeData = {
            label: "Data Source",
            description: "Input data for evaluation",
            icon: "Database",
          }
          break
        case "callNode":
          newNodeData = {
            label: "Model Call",
            description: "Call an LLM API",
            icon: "MessageSquare",
          }
          break
        case "toolNode":
          newNodeData = {
            label: "Evaluation Tool",
            description: "Analyze and score responses",
            icon: "BarChart3",
          }
          break
      }

      const newNode = {
        id: `node_${Date.now()}`,
        type: nodeType as "dataNode" | "callNode" | "toolNode",
        position: nodeSelectorPosition,
        data: newNodeData,
      }

      setNodes((nds) => [...nds, newNode])
      setShowNodeSelector(false)
    },
    [nodeSelectorPosition],
  )

  const onNodeDragStart = useCallback(
    (event: React.MouseEvent, nodeId: string) => {
      setDraggedNode(nodeId)
      const node = nodes.find((n) => n.id === nodeId)
      if (node) {
        setDragOffset({
          x: event.clientX / canvasScale - node.position.x,
          y: event.clientY / canvasScale - node.position.y,
        })
      }
    },
    [nodes, canvasScale],
  )

  const onNodeDrag = useCallback(
    (event: React.MouseEvent) => {
      if (draggedNode) {
        setNodes((nds) =>
          nds.map((n) => {
            if (n.id === draggedNode) {
              return {
                ...n,
                position: {
                  x: event.clientX / canvasScale - dragOffset.x,
                  y: event.clientY / canvasScale - dragOffset.y,
                },
              }
            }
            return n
          }),
        )
      }
    },
    [draggedNode, dragOffset, canvasScale],
  )

  const onNodeDragEnd = useCallback(() => {
    setDraggedNode(null)
  }, [])

  const onConnectStart = useCallback((nodeId: string) => {
    setConnectingFrom(nodeId)
  }, [])

  const onConnectEnd = useCallback(
    (nodeId: string) => {
      if (connectingFrom && connectingFrom !== nodeId) {
        // Create a new edge
        const newEdge = {
          id: `edge_${connectingFrom}_${nodeId}`,
          source: connectingFrom,
          target: nodeId,
        }
        setEdges((eds) => [...eds, newEdge])
      }
      setConnectingFrom(null)
    },
    [connectingFrom],
  )

  const onSave = useCallback(() => {
    const flow = { nodes, edges }
    console.log(flow)
    // In a real app, you would save this to your backend
    localStorage.setItem("evalFlow", JSON.stringify(flow))
  }, [nodes, edges])

  const onZoomIn = useCallback(() => {
    setCanvasScale((scale) => Math.min(scale + 0.1, 2))
  }, [])

  const onZoomOut = useCallback(() => {
    setCanvasScale((scale) => Math.max(scale - 0.1, 0.5))
  }, [])

  const onZoomReset = useCallback(() => {
    setCanvasScale(1)
  }, [])

  return (
    <div className="relative h-[600px] w-full border rounded-md overflow-hidden bg-gray-50 dark:bg-gray-900">
      <div className="absolute top-2 right-2 z-10 flex gap-2">
        <Button size="sm" variant="outline" onClick={() => setShowNodeSelector(true)}>
          <PlusCircle className="mr-2 h-4 w-4" />
          Add Node
        </Button>
        <Button size="sm" onClick={onSave}>
          <Save className="mr-2 h-4 w-4" />
          Save Flow
        </Button>
      </div>

      <div className="absolute bottom-2 right-2 z-10 flex gap-1">
        <Button size="icon" variant="outline" onClick={onZoomIn}>
          +
        </Button>
        <Button size="icon" variant="outline" onClick={onZoomReset}>
          100%
        </Button>
        <Button size="icon" variant="outline" onClick={onZoomOut}>
          -
        </Button>
      </div>

      <div
        ref={canvasRef}
        className="h-full w-full relative"
        onClick={onCanvasClick}
        onMouseMove={onNodeDrag}
        onMouseUp={onNodeDragEnd}
      >
        <div
          className="absolute top-0 left-0 w-full h-full"
          style={{
            backgroundImage: "radial-gradient(circle, rgba(0,0,0,0.1) 1px, transparent 1px)",
            backgroundSize: `${20 * canvasScale}px ${20 * canvasScale}px`,
            transform: `scale(${canvasScale})`,
            transformOrigin: "0 0",
          }}
        >
          {/* Render edges */}
          <svg className="absolute top-0 left-0 w-full h-full pointer-events-none">
            {edges.map((edge) => {
              const sourceNode = nodes.find((n) => n.id === edge.source)
              const targetNode = nodes.find((n) => n.id === edge.target)
              if (!sourceNode || !targetNode) return null

              const sourceX = sourceNode.position.x + 128 // Half of node width
              const sourceY = sourceNode.position.y + 100 // Approximate node height
              const targetX = targetNode.position.x + 128 // Half of node width
              const targetY = targetNode.position.y

              return (
                <g key={edge.id}>
                  <path
                    d={`M${sourceX},${sourceY} C${sourceX},${
                      sourceY + 50
                    } ${targetX},${targetY - 50} ${targetX},${targetY}`}
                    stroke="rgba(0,0,0,0.3)"
                    strokeWidth="2"
                    fill="none"
                    strokeDasharray="5,5"
                  />
                </g>
              )
            })}

            {/* Render connecting line when dragging a connection */}
            {connectingFrom && (
              <path
                d={`M${nodes.find((n) => n.id === connectingFrom)?.position.x ?? 0},${
                  (nodes.find((n) => n.id === connectingFrom)?.position.y ?? 0) + 100
                } L${nodeSelectorPosition.x},${nodeSelectorPosition.y}`}
                stroke="rgba(0,0,0,0.3)"
                strokeWidth="2"
                fill="none"
                strokeDasharray="5,5"
              />
            )}
          </svg>

          {/* Render nodes */}
          {nodes.map((node) => (
            <div
              key={node.id}
              style={{
                position: "absolute",
                left: `${node.position.x}px`,
                top: `${node.position.y}px`,
                cursor: draggedNode === node.id ? "grabbing" : "grab",
              }}
            >
              <SimpleNode
                id={node.id}
                type={node.type}
                data={node.data}
                onDragStart={(e) => onNodeDragStart(e, node.id)}
                onConnectStart={() => onConnectStart(node.id)}
                onConnectEnd={() => onConnectEnd(node.id)}
              />
            </div>
          ))}
        </div>
      </div>

      {showNodeSelector && (
        <NodeSelector position={nodeSelectorPosition} onSelect={onAddNode} onClose={() => setShowNodeSelector(false)} />
      )}
    </div>
  )
}
