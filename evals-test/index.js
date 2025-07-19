require('dotenv').config();

// CORRECT: Import and initialize TrainLoop SDK FIRST
const { trainloopTag, collect } = require('trainloop-llm-logging');
collect(true); // Initialize synchronously at module level

// THEN import HTTP client libraries
const OpenAI = require('openai');

async function main() {
  try {
    console.log('SDK already initialized at module level');
    
    // Create OpenAI client with TrainLoop headers
    const headers = trainloopTag("hello-test");
    console.log('TrainLoop headers:', headers);
    
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
      defaultHeaders: headers
    });
    
    console.log('Making OpenAI API call...');
    
    // Make OpenAI request
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'user',
          content: 'Hello, how are you?',
        },
      ],
    });

    console.log('Response:', completion.choices[0].message.content);
  } catch (error) {
    console.error('Error:', error);
  }
  
  console.log('Script completed, exiting naturally...');
  process.exit(0);
}

main();