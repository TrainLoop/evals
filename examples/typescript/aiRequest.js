const OpenAI = require('openai');
require('dotenv').config();

// Initialize the OpenAI client (reads the key from the OPENAI_API_KEY env var).
const client = new OpenAI();

/**
 * Makes a request to the OpenAI API using the specified model and prompt.
 * 
 * @param {string} prompt - The prompt string to send to the model.
 * @param {string} model - The model ID to use for the request. Defaults to gpt-4o-mini.
 * @param {number} maxTokens - Maximum number of tokens to generate in the response.
 * @param {Object} extraHeaders - Additional headers to pass with the request (e.g., for tagging).
 * @returns {Promise<string|null>} The AI's response as a string or null if an error occurred.
 */
async function makeAiRequest(
    prompt,
    model = "gpt-4o-mini",
    maxTokens = 500,
    extraHeaders = {}
) {
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

module.exports = { makeAiRequest };