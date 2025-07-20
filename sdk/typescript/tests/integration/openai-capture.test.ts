import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';

describe('OpenAI API Call Capture Integration Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-openai');
  const eventsDir = path.join(testDataFolder, 'events');
  
  beforeEach(() => {
    // Clean up test data folder
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }

    // Clear environment variables
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;
    delete process.env.TRAINLOOP_CONFIG_PATH;
    delete process.env.TRAINLOOP_DISABLE_AUTO_INIT;

    // Set up test environment
    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';
    process.env.TRAINLOOP_LOG_LEVEL = 'ERROR'; // Reduce noise

    // Clear module cache
    jest.resetModules();
  });

  afterEach(async () => {
    // Clean up test data
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }

    // Clear environment variables
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;
    delete process.env.TRAINLOOP_CONFIG_PATH;
    delete process.env.TRAINLOOP_DISABLE_AUTO_INIT;
  });

  it('should capture OpenAI API calls with default headers', async () => {
    if (!process.env.OPENAI_API_KEY) {
      console.warn('Skipping OpenAI test - OPENAI_API_KEY not set');
      return;
    }

    // Import SDK first
    const { collect, trainloopTag } = await import('../../dist/index.js');
    collect(true); // Initialize with immediate flush

    // Then import OpenAI
    const { default: OpenAI } = await import('openai');
    
    // Create client with TrainLoop headers
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
      defaultHeaders: trainloopTag('test-capture')
    });

    // Make API call
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Say "test" in one word' }],
      max_tokens: 5
    });

    expect(completion.choices[0].message.content).toBeTruthy();

    // Wait for flush
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Check if event was captured
    expect(fs.existsSync(eventsDir)).toBe(true);
    const files = fs.readdirSync(eventsDir);
    expect(files.length).toBeGreaterThan(0);

    // Read and verify the event
    const eventFile = path.join(eventsDir, files[0]);
    const content = fs.readFileSync(eventFile, 'utf8');
    const lines = content.trim().split('\n');
    const lastEvent = JSON.parse(lines[lines.length - 1]);

    expect(lastEvent.tag).toBe('test-capture');
    expect(lastEvent.model).toBe('gpt-4o-mini');
    expect(lastEvent.input).toBeTruthy();
    expect(lastEvent.output).toBeTruthy();
    expect(lastEvent.durationMs).toBeGreaterThan(0);
  });

  it('should capture multiple API calls with different tags', async () => {
    if (!process.env.OPENAI_API_KEY) {
      console.warn('Skipping OpenAI test - OPENAI_API_KEY not set');
      return;
    }

    // Import SDK first
    const { collect, trainloopTag } = await import('../../dist/index.js');
    collect(true); // Initialize with immediate flush

    // Then import OpenAI
    const { default: OpenAI } = await import('openai');
    
    // Create clients with different tags
    const client1 = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
      defaultHeaders: trainloopTag('client-1')
    });

    const client2 = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
      defaultHeaders: trainloopTag('client-2')
    });

    // Make API calls
    const [response1, response2] = await Promise.all([
      client1.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: 'Say "one"' }],
        max_tokens: 5
      }),
      client2.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: 'Say "two"' }],
        max_tokens: 5
      })
    ]);

    expect(response1.choices[0].message.content).toBeTruthy();
    expect(response2.choices[0].message.content).toBeTruthy();

    // Wait for flush
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Check events
    const files = fs.readdirSync(eventsDir);
    expect(files.length).toBeGreaterThan(0);

    const eventFile = path.join(eventsDir, files[0]);
    const content = fs.readFileSync(eventFile, 'utf8');
    const events = content.trim().split('\n').map(line => JSON.parse(line));

    // Find events by tag
    const client1Events = events.filter(e => e.tag === 'client-1');
    const client2Events = events.filter(e => e.tag === 'client-2');

    expect(client1Events.length).toBeGreaterThan(0);
    expect(client2Events.length).toBeGreaterThan(0);
  });

  it('should work with synchronous collect at module level', async () => {
    if (!process.env.OPENAI_API_KEY) {
      console.warn('Skipping OpenAI test - OPENAI_API_KEY not set');
      return;
    }

    // This test simulates module-level initialization
    // by clearing the module cache and re-importing
    jest.resetModules();

    // Import and use in the correct order
    const sdkModule = await import('../../dist/index.js');
    sdkModule.collect(true); // Synchronous call

    const { default: OpenAI } = await import('openai');
    
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
      defaultHeaders: sdkModule.trainloopTag('sync-test')
    });

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Say "sync"' }],
      max_tokens: 5
    });

    expect(completion.choices[0].message.content).toBeTruthy();

    // Wait for flush
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Verify capture
    const files = fs.readdirSync(eventsDir);
    expect(files.length).toBeGreaterThan(0);
  });
});