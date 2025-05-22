import Groq from 'groq-sdk';

export async function POST(request: Request) {
  const groq = new Groq()

  try {
    const { prompt, model = "llama3-8b-8192" } = await request.json()

    if (!prompt) {
      return Response.json({ error: "Prompt is required" }, { status: 400 })
    }

    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: "user",
          content: prompt,
        },
      ],
      model: model,
    })

    return Response.json({
      response: completion.choices[0].message.content,
      model: model,
      usage: completion.usage,
    })
  } catch (error) {
    console.error("Error calling Groq API:", error)
    return Response.json({ error: "Failed to get response from Groq" }, { status: 500 })
  }
}
