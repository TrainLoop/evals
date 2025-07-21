import OpenAI from 'openai';
import dotenv from 'dotenv';

dotenv.config();

// Initialize the OpenAI client (reads the key from the OPENAI_API_KEY env var).
const client = new OpenAI();

/**
 * Makes a request to the OpenAI API using the specified model and prompt.
 * 
 * @param prompt - The prompt string to send to the model.
 * @param model - The model ID to use for the request. Defaults to gpt-4o-mini.
 * @param maxTokens - Maximum number of tokens to generate in the response.
 * @param extraHeaders - Additional headers to pass with the request (e.g., for tagging).
 * @returns The AI's response as a string or null if an error occurred.
 */
export async function makeAiRequest(
    prompt: string,
    model: string = "gpt-4o-mini",
    maxTokens: number = 500,
    extraHeaders: Record<string, string> = {}
): Promise<string | null> {
    try {
        const response = await client.chat.completions.create({
            model,
            messages: [{ role: "user", content: prompt }],
            max_tokens: maxTokens,
        }, {
            headers: extraHeaders
        });
        
        return response.choices[0].message.content;
    } catch (error) {
        console.error(`An error occurred: ${error}`);
        return null;
    }
}