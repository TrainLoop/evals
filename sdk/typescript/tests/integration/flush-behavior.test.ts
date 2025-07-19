import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';
import OpenAI from 'openai';

describe('Flush Behavior Integration Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-flush');
  const eventsDir = path.join(testDataFolder, 'events');

  beforeEach(() => {
    // Clean up test data folder
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }

    // Set up test environment
    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';
    process.env.TRAINLOOP_LOG_LEVEL = 'DEBUG';

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
  });

  it('should flush events manually with flush()', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    const { collect, flush, trainloopTag } = await import('../../src');
    
    // Initialize without instant flush to test manual flush
    await collect(false);

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Make API call
    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Hello!' }],
    }, {
      headers: { ...trainloopTag('flush-test') }
    });

    // Before flush, events directory might not exist or be empty
    let eventsBefore: string[] = [];
    if (fs.existsSync(eventsDir)) {
      eventsBefore = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    }

    // Manual flush
    await flush();

    // After flush, events should be written
    expect(fs.existsSync(eventsDir)).toBe(true);
    const eventsAfter = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventsAfter.length).toBeGreaterThan(0);

    // Verify event content
    const eventFile = path.join(eventsDir, eventsAfter[0]);
    const eventContent = fs.readFileSync(eventFile, 'utf8');
    const events = eventContent.trim().split('\n').map(line => JSON.parse(line));
    
    expect(events.some(event => event.tag === 'flush-test')).toBe(true);
  });

  it('should flush events on shutdown()', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    const { collect, shutdown, trainloopTag } = await import('../../src');
    
    // Initialize without instant flush
    await collect(false);

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Make API call
    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Shutdown test!' }],
    }, {
      headers: { ...trainloopTag('shutdown-test') }
    });

    // Before shutdown, events directory might not exist or be empty
    let eventsBefore: string[] = [];
    if (fs.existsSync(eventsDir)) {
      eventsBefore = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    }

    // Shutdown should flush buffered events
    await shutdown();

    // After shutdown, events should be written
    expect(fs.existsSync(eventsDir)).toBe(true);
    const eventsAfter = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventsAfter.length).toBeGreaterThan(0);

    // Verify event content
    const eventFile = path.join(eventsDir, eventsAfter[0]);
    const eventContent = fs.readFileSync(eventFile, 'utf8');
    const events = eventContent.trim().split('\n').map(line => JSON.parse(line));
    
    expect(events.some(event => event.tag === 'shutdown-test')).toBe(true);
  });

  it('should immediately flush with instant flush enabled', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    const { collect, trainloopTag } = await import('../../src');
    
    // Initialize with instant flush
    await collect(true);

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Make API call
    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Instant flush test!' }],
    }, {
      headers: { ...trainloopTag('instant-test') }
    });

    // With instant flush, events should be written immediately
    expect(fs.existsSync(eventsDir)).toBe(true);
    const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventFiles.length).toBeGreaterThan(0);

    // Verify event content
    const eventFile = path.join(eventsDir, eventFiles[0]);
    const eventContent = fs.readFileSync(eventFile, 'utf8');
    const events = eventContent.trim().split('\n').map(line => JSON.parse(line));
    
    expect(events.some(event => event.tag === 'instant-test')).toBe(true);
  });

  it('should handle multiple API calls with batch flushing', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    const { collect, flush, trainloopTag } = await import('../../src');
    
    // Initialize with batch size of 3 for testing
    await collect(false);

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Make multiple API calls
    for (let i = 0; i < 3; i++) {
      await openai.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: `Batch test ${i}` }],
      }, {
        headers: { ...trainloopTag(`batch-${i}`) }
      });
    }

    // Manual flush to ensure all events are written
    await flush();

    // Should have events for all API calls
    expect(fs.existsSync(eventsDir)).toBe(true);
    const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventFiles.length).toBeGreaterThan(0);

    // Verify all events are present
    const eventFile = path.join(eventsDir, eventFiles[0]);
    const eventContent = fs.readFileSync(eventFile, 'utf8');
    const events = eventContent.trim().split('\n').map(line => JSON.parse(line));
    
    expect(events.length).toBe(3);
    expect(events.some(event => event.tag === 'batch-0')).toBe(true);
    expect(events.some(event => event.tag === 'batch-1')).toBe(true);
    expect(events.some(event => event.tag === 'batch-2')).toBe(true);
  });
});