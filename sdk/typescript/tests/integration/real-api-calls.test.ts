/**
 * Real API call tests - run without mocks
 * These tests make actual API calls and verify data capture
 */
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

describe('Real API Call Integration Tests', () => {
  const fixturesDir = path.join(__dirname, 'fixtures-real');

  beforeEach(() => {
    if (fs.existsSync(fixturesDir)) {
      fs.rmSync(fixturesDir, { recursive: true, force: true });
    }
    fs.mkdirSync(fixturesDir, { recursive: true });
  });

  afterEach(() => {
    if (fs.existsSync(fixturesDir)) {
      fs.rmSync(fixturesDir, { recursive: true, force: true });
    }
  });

  it('should capture real OpenAI API calls with TrainLoop SDK', (done) => {
    if (!process.env.OPENAI_API_KEY) {
      console.warn('Skipping real API test - OPENAI_API_KEY not set');
      done();
      return;
    }

    const testScript = `
const path = require('path');
const fs = require('fs');

// Set up environment
const testDataFolder = path.join(__dirname, 'test-data');
process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';
process.env.TRAINLOOP_LOG_LEVEL = 'ERROR';
process.env.OPENAI_API_KEY = '${process.env.OPENAI_API_KEY}';

// Import and initialize SDK first
const { collect, trainloopTag } = require('${path.resolve(__dirname, '../../dist/index.js')}');
collect(true);

// Then import OpenAI
const { default: OpenAI } = require('openai');

async function test() {
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    defaultHeaders: trainloopTag('real-api-test')
  });

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Say "test success" in exactly two words' }],
      max_tokens: 10
    });

    console.log('API_RESPONSE:', completion.choices[0].message.content);

    // Wait for flush
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Check if events were captured
    const eventsDir = path.join(testDataFolder, 'events');
    if (fs.existsSync(eventsDir)) {
      const files = fs.readdirSync(eventsDir);
      if (files.length > 0) {
        const eventFile = path.join(eventsDir, files[0]);
        const content = fs.readFileSync(eventFile, 'utf8');
        const lines = content.trim().split('\\n');
        const lastEvent = JSON.parse(lines[lines.length - 1]);
        
        console.log('EVENT_TAG:', lastEvent.tag);
        console.log('EVENT_MODEL:', lastEvent.model);
        console.log('SUCCESS: Event captured');
      } else {
        console.log('ERROR: No event files found');
      }
    } else {
      console.log('ERROR: Events directory not created');
    }
  } catch (error) {
    console.error('ERROR:', error.message);
  }
}

test();
`;

    const scriptPath = path.join(fixturesDir, 'real-api-test.js');
    fs.writeFileSync(scriptPath, testScript);

    try {
      const output = execSync(`node ${scriptPath}`, {
        encoding: 'utf8',
        stdio: 'pipe',
        timeout: 30000
      });

      expect(output).toContain('API_RESPONSE:');
      expect(output).toContain('EVENT_TAG: real-api-test');
      expect(output).toContain('EVENT_MODEL: gpt-4o-mini');
      expect(output).toContain('SUCCESS: Event captured');
      
      done();
    } catch (error) {
      done(error);
    }
  }, 30000);

  it('should show import order error when OpenAI is imported first', (done) => {
    const errorScript = `
process.env.TRAINLOOP_DISABLE_AUTO_INIT = 'true';
process.env.TRAINLOOP_DATA_FOLDER = '/tmp/test';

// Wrong order: OpenAI first
const { default: OpenAI } = require('openai');
const { collect } = require('${path.resolve(__dirname, '../../dist/index.js')}');

try {
  collect(true);
  console.log('ERROR: Should not reach here');
} catch (error) {
  if (error.message.includes('TrainLoop SDK must be initialized before importing')) {
    console.log('SUCCESS: Import order error detected');
  } else {
    console.log('ERROR: Wrong error:', error.message);
  }
}
`;

    const scriptPath = path.join(fixturesDir, 'import-error-test.js');
    fs.writeFileSync(scriptPath, errorScript);

    try {
      const output = execSync(`node ${scriptPath}`, {
        encoding: 'utf8',
        stdio: 'pipe'
      });

      expect(output).toContain('SUCCESS: Import order error detected');
      done();
    } catch (error) {
      done(error);
    }
  });
});