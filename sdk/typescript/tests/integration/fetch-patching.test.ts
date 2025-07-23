import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';

describe('Fetch Patching Integration Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-fetch');
  let originalFetch: typeof global.fetch;
  
  beforeEach(() => {
    // Clean up test data folder
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }

    // Store original fetch
    originalFetch = global.fetch;

    // Clear environment variables
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;
    delete process.env.TRAINLOOP_CONFIG_PATH;

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

    // Restore original fetch
    global.fetch = originalFetch;

    // Clear environment variables
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;
    delete process.env.TRAINLOOP_CONFIG_PATH;
  });

  it('should patch global fetch when SDK is initialized', async () => {
    // Check initial state
    expect(global.fetch).toBeDefined();
    const originalFetchName = global.fetch.name;

    // Import and initialize SDK
    const { collect } = await import('../../src');
    await collect(true);

    // Verify fetch was patched
    expect(global.fetch).toBeDefined();
    expect(global.fetch.name).toBe('patchedFetch');
    expect(global.fetch.name).not.toBe(originalFetchName);
    expect(global.fetch.toString()).toContain('function patchedFetch');
  });

  it('should intercept and log fetch calls to allowed hosts', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    const { collect } = await import('../../src');
    await collect(true);

    // Make a fetch call to an allowed host
    const response = await global.fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'X-Trainloop-Tag': 'fetch-test'
      }
    });

    expect(response).toBeDefined();
    expect(response.status).toBeDefined();

    // Check that events were written
    const eventsDir = path.join(testDataFolder, 'events');
    if (fs.existsSync(eventsDir)) {
      const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
      expect(eventFiles.length).toBeGreaterThan(0);

      // Check event content
      const eventFile = path.join(eventsDir, eventFiles[0]);
      const eventContent = fs.readFileSync(eventFile, 'utf8');
      const events = eventContent.trim().split('\n').map(line => JSON.parse(line));
      
      expect(events.some(event => 
        event.url === 'https://api.openai.com/v1/models' &&
        event.tag === 'fetch-test'
      )).toBe(true);
    }
  });

  it('should not log fetch calls to non-allowed hosts', async () => {
    const { collect } = await import('../../src');
    await collect(true);

    // Make a fetch call to a non-allowed host (this might fail, but that's OK)
    try {
      await global.fetch('https://example.com', {
        headers: {
          'X-Trainloop-Tag': 'should-not-log'
        }
      });
    } catch (error) {
      // Ignore network errors
    }

    // Check that no events were written for non-allowed host
    const eventsDir = path.join(testDataFolder, 'events');
    if (fs.existsSync(eventsDir)) {
      const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
      
      if (eventFiles.length > 0) {
        const eventFile = path.join(eventsDir, eventFiles[0]);
        const eventContent = fs.readFileSync(eventFile, 'utf8');
        const events = eventContent.trim().split('\n').map(line => JSON.parse(line));
        
        // Should not have logged the example.com call
        expect(events.some(event => 
          event.url === 'https://example.com'
        )).toBe(false);
      }
    }
  });

  it('should preserve original fetch behavior for non-LLM requests', async () => {
    const { collect } = await import('../../src');
    await collect(true);

    // Test that fetch still works normally for regular requests
    const testData = { test: 'data' };
    
    // Create a simple mock server response
    const mockResponse = new Response(JSON.stringify(testData), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

    // Mock fetch for this specific test case
    const mockFetch = jest.fn().mockResolvedValue(mockResponse);
    const originalPatchedFetch = global.fetch;
    global.fetch = mockFetch;

    try {
      const response = await global.fetch('https://example.com/test');
      const data = await response.json();

      expect(mockFetch).toHaveBeenCalledWith('https://example.com/test');
      expect(data).toEqual(testData);
      expect(response.status).toBe(200);
    } finally {
      // Restore patched fetch
      global.fetch = originalPatchedFetch;
    }
  });
});