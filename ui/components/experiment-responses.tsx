"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

// Mock data for experiment responses
const responses = [
  {
    id: "resp-001",
    prompt: "Explain how to reset a password for a customer who has forgotten it.",
    responses: [
      {
        model: "GPT-4",
        text: "To reset your password, please follow these steps:\n\n1. Go to the login page\n2. Click on 'Forgot Password'\n3. Enter the email associated with your account\n4. Check your email for a password reset link\n5. Click the link and follow instructions to create a new password\n\nIf you don't receive an email within a few minutes, please check your spam folder or contact our support team at support@example.com.",
        metrics: {
          exactMatch: 85.2,
          semanticSimilarity: 92.7,
          factualAccuracy: 100,
        },
      },
      {
        model: "Claude 3",
        text: "I'd be happy to help you reset your password. Here's what you need to do:\n\n1. Navigate to our login page\n2. Select the 'Forgot password?' option below the login form\n3. Enter your email address\n4. You'll receive a password reset email with a secure link\n5. Follow the link and create a new password\n\nThe link expires after 24 hours for security. If you need additional help, our support team is available at help@example.com or call us at (555) 123-4567.",
        metrics: {
          exactMatch: 78.9,
          semanticSimilarity: 89.3,
          factualAccuracy: 95.5,
        },
      },
    ],
  },
  {
    id: "resp-002",
    prompt: "What is your return policy for items purchased online?",
    responses: [
      {
        model: "GPT-4",
        text: "Our return policy for online purchases allows returns within 30 days of delivery. Items must be unused, in original packaging with all tags attached. To initiate a return, log into your account, go to order history, and select 'Return Item'. You'll receive a prepaid shipping label via email. Refunds are processed within 5-7 business days after we receive the returned item. Note that personalized items and final sale merchandise cannot be returned.",
        metrics: {
          exactMatch: 62.1,
          semanticSimilarity: 88.4,
          factualAccuracy: 95.0,
        },
      },
      {
        model: "Claude 3",
        text: "For items purchased on our website, you have 30 days from the delivery date to return them. The products must be in their original condition with tags attached and original packaging. To start a return, visit your account, find the order, and click 'Return'. We'll email you a free return shipping label. Once we receive and inspect your return, we'll process your refund to the original payment method within 7 business days. Please note that customized products and items marked as final sale cannot be returned.",
        metrics: {
          exactMatch: 68.7,
          semanticSimilarity: 91.2,
          factualAccuracy: 97.5,
        },
      },
    ],
  },
]

export function ExperimentResponses() {
  const [activeResponse, setActiveResponse] = useState(0)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Response Comparison</CardTitle>
        <CardDescription>Compare responses from different models for the same prompts.</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs
          defaultValue={responses[0].id}
          onValueChange={(value) => {
            const index = responses.findIndex((r) => r.id === value)
            if (index !== -1) setActiveResponse(index)
          }}
        >
          <TabsList className="mb-4">
            {responses.map((response, index) => (
              <TabsTrigger key={response.id} value={response.id}>
                Prompt {index + 1}
              </TabsTrigger>
            ))}
          </TabsList>

          {responses.map((response, index) => (
            <TabsContent key={response.id} value={response.id}>
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2">Prompt:</h3>
                <div className="rounded-md border p-4 bg-muted/50">{response.prompt}</div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {response.responses.map((modelResponse) => (
                  <div key={modelResponse.model} className="rounded-md border p-4">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-semibold">{modelResponse.model}</h4>
                      <div className="flex gap-1">
                        {Object.entries(modelResponse.metrics).map(([key, value]) => (
                          <Badge key={key} variant="outline" className="text-xs">
                            {key.replace(/([A-Z])/g, " $1").trim()}: {value.toFixed(1)}%
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="whitespace-pre-line text-sm">{modelResponse.text}</div>
                  </div>
                ))}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  )
}
