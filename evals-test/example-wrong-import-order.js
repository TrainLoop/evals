// WRONG: This example shows what NOT to do

// Disable auto-initialization to demonstrate the warning
process.env.TRAINLOOP_DISABLE_AUTO_INIT = 'true';

require('dotenv').config();

// WRONG: Importing OpenAI before TrainLoop SDK
const OpenAI = require('openai');

// Now when we try to use TrainLoop, it will warn us
const { trainloopTag, collect } = require('trainloop-llm-logging');

try {
  console.log('Attempting to initialize TrainLoop after OpenAI import...');
  collect(true);
  console.log('This line should not be reached!');
} catch (error) {
  console.log('\n❌ Error caught (as expected):');
  console.log(error.message);
  console.log('\n✅ The SDK correctly detected that OpenAI was imported before initialization!');
}