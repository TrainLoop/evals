"use client"

import type React from "react"

import { useCallback, useRef, useState } from "react"
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type Edge,
  type NodeTypes,
  Panel,
} from "reactflow"
import "reactflow/dist/style.css"

import { Button } from "@/components/ui/button"
import { PlusCircle, Save } from "lucide-react"
import { type NodeData, DataNode, CallNode, ToolNode } from "./flow-nodes"
import { NodeSelector } from "./node-selector"

const nodeTypes: NodeTypes = {
  dataNode: DataNode,
  callNode: CallNode,
  toolNode: ToolNode,
}

const initialNodes = [
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

const initialEdges: Edge[] = []

export function FlowCanvas() {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null)
  const [showNodeSelector, setShowNodeSelector] = useState(false)
  const [nodeSelectorPosition, setNodeSelectorPosition] = useState({ x: 0, y: 0 })

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    [setEdges],
  )

  const onDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"
  }, [])

  const onSave = useCallback(() => {
    if (reactFlowInstance) {
      const flow = reactFlowInstance.toObject()
      console.log(flow)
      // In a real app, you would save this to your backend
      localStorage.setItem("evalFlow", JSON.stringify(flow))
    }
  }, [reactFlowInstance])

  const onAddNode = useCallback(
    (nodeType: string) => {
      const position = reactFlowInstance.screenToFlowPosition({
        x: nodeSelectorPosition.x,
        y: nodeSelectorPosition.y,
      })

      let newNodeData: NodeData = {
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
        type: nodeType,
        position,
        data: newNodeData,
      }

      setNodes((nds) => nds.concat(newNode))
      setShowNodeSelector(false)
    },
    [nodeSelectorPosition, reactFlowInstance, setNodes],
  )

  const onCanvasClick = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      if (reactFlowWrapper.current && reactFlowInstance) {
        const boundingRect = reactFlowWrapper.current.getBoundingClientRect()
        const position = {
          x: event.clientX - boundingRect.left,
          y: event.clientY - boundingRect.top,
        }
        setNodeSelectorPosition(position)
        setShowNodeSelector(true)
      }
    },
    [reactFlowInstance],
  )

  return (
    <div className="h-[600px] w-full border rounded-md" ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onInit={setReactFlowInstance}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        onPaneClick={onCanvasClick}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background variant="dots" gap={12} size={1} />

        <Panel position="top-right">
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => setShowNodeSelector(true)}>
              <PlusCircle className="mr-2 h-4 w-4" />
              Add Node
            </Button>
            <Button size="sm" onClick={onSave}>
              <Save className="mr-2 h-4 w-4" />
              Save Flow
            </Button>
          </div>
        </Panel>

        {showNodeSelector && (
          <NodeSelector
            position={nodeSelectorPosition}
            onSelect={onAddNode}
            onClose={() => setShowNodeSelector(false)}
          />
        )}
      </ReactFlow>
    </div>
  )
}
