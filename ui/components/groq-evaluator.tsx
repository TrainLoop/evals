"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { callGroqModel } from "@/lib/utils"
import { Loader2 } from "lucide-react"

interface GroqEvaluatorProps {
  referenceText?: string
}

export function GroqEvaluator({ referenceText }: GroqEvaluatorProps) {
  const [prompt, setPrompt] = useState("")
  const [response, setResponse] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleEvaluate = async () => {
    if (!prompt) return

    setLoading(true)
    setError("")

    try {
      const result = await callGroqModel(prompt)
      setResponse(result.response)
    } catch (err) {
      setError("Failed to get response from Groq")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Groq Model Evaluation</CardTitle>
        <CardDescription>Test your prompts with Groq&apos;s LLM models</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="prompt">Prompt</Label>
          <Textarea
            id="prompt"
            placeholder="Enter your prompt here..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
          />
        </div>

        {referenceText && (
          <div className="space-y-2">
            <Label htmlFor="reference">Reference Text</Label>
            <div className="p-3 border rounded-md bg-muted/50">{referenceText}</div>
          </div>
        )}

        {response && (
          <div className="space-y-2">
            <Label htmlFor="response">Model Response</Label>
            <div className="p-3 border rounded-md whitespace-pre-wrap">{response}</div>
          </div>
        )}

        {error && <div className="text-red-500 text-sm">{error}</div>}
      </CardContent>
      <CardFooter>
        <Button onClick={handleEvaluate} disabled={loading || !prompt}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Evaluating...
            </>
          ) : (
            "Evaluate with Groq"
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}
