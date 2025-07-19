// CORRECT: Initialize TrainLoop SDK before importing HTTP client libraries
require('dotenv').config();

// Step 1: Import and initialize TrainLoop SDK FIRST
const { trainloopTag, collect } = require('trainloop-llm-logging');
collect(true); // Initialize with immediate flush for testing

// Step 2: THEN import HTTP client libraries
const OpenAI = require('openai');

async function main() {
  console.log('TrainLoop SDK initialized correctly!');
  
  // Create OpenAI client with TrainLoop headers
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    defaultHeaders: trainloopTag("correct-order-demo")
  });
  
  console.log('Making OpenAI API call...');
  
  const completion = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'user',
        content: 'What is 2+2?',
      },
    ],
  });
  
  console.log('Response:', completion.choices[0].message.content);
  
  // Give SDK time to flush
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Check if event was captured
  const fs = require('fs');
  const eventsDir = './trainloop/data/events';
  const files = fs.readdirSync(eventsDir);
  console.log(`\n✅ Success! Found ${files.length} event file(s) in ${eventsDir}`);
  
  // Show the latest event
  if (files.length > 0) {
    const latestFile = files[files.length - 1];
    const content = fs.readFileSync(`${eventsDir}/${latestFile}`, 'utf8');
    const lines = content.trim().split('\n');
    const lastEvent = JSON.parse(lines[lines.length - 1]);
    console.log(`✅ Latest event captured with tag: "${lastEvent.tag}"`);
  }
}

main().catch(console.error);