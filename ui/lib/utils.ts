import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

// Core evaluation metrics implementation
export type EvalMetric = {
  name: string
  description: string
  calculate: (response: string, reference: string) => number
}

export const evalMetrics = {
  exactMatch: {
    name: "Exact Match",
    description: "Percentage of exact character matches between response and reference",
    calculate: (response: string, reference: string): number => {
      if (!response || !reference) return 0
      return response === reference ? 100 : 0
    },
  },

  semanticSimilarity: {
    name: "Semantic Similarity",
    description: "Measures how similar the meanings are between response and reference",
    calculate: (response: string, reference: string): number => {
      // In a real implementation, this would use embeddings or a semantic similarity model
      // This is a simplified placeholder implementation
      if (!response || !reference) return 0

      const responseWords = new Set(response.toLowerCase().split(/\s+/))
      const referenceWords = new Set(reference.toLowerCase().split(/\s+/))

      const intersection = new Set([...responseWords].filter((x) => referenceWords.has(x)))
      const union = new Set([...responseWords, ...referenceWords])

      return (intersection.size / union.size) * 100
    },
  },

  factualAccuracy: {
    name: "Factual Accuracy",
    description: "Evaluates the factual correctness of the response",
    calculate: (response: string, reference: string): number => {
      // In a real implementation, this would use a fact-checking model or approach
      // This is a simplified placeholder implementation
      if (!response || !reference) return 0

      // Simple implementation based on keyword matching
      const factKeywords = reference.toLowerCase().match(/\b\w{5,}\b/g) || []
      const responseText = response.toLowerCase()

      let matches = 0
      for (const keyword of factKeywords) {
        if (responseText.includes(keyword)) {
          matches++
        }
      }

      return factKeywords.length > 0 ? (matches / factKeywords.length) * 100 : 0
    },
  },
}

// Helper function for class names
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Groq API helper
export async function callGroqModel(prompt: string, model = "llama3-8b-8192") {
  const response = await fetch("/api/groq", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
      model,
    }),
  })

  if (!response.ok) {
    throw new Error("Failed to call Groq API")
  }

  return await response.json()
}
