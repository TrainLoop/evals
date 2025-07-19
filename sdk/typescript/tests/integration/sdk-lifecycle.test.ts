import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';
import OpenAI from 'openai';

describe('SDK Lifecycle Integration Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-lifecycle');

  beforeEach(() => {
    // Clean up test data folder
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }

    // Clear all environment variables
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

    // Clear environment variables
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;
    delete process.env.TRAINLOOP_CONFIG_PATH;
  });

  it('should initialize SDK with environment variables', async () => {
    // Import SDK - this triggers auto-initialization
    const sdk = await import('../../src');

    // Check that exports are available
    expect(sdk.collect).toBeDefined();
    expect(sdk.flush).toBeDefined();
    expect(sdk.shutdown).toBeDefined();
    expect(sdk.trainloopTag).toBeDefined();
    expect(sdk.HEADER_NAME).toBeDefined();

    // Environment variables should be set after initialization
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(testDataFolder);
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('api.openai.com');
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('DEBUG');
  });

  it('should handle explicit collect() initialization', async () => {
    const sdk = await import('../../src');

    // Explicitly initialize
    expect(() => sdk.collect(true)).not.toThrow();

    // Should be able to use trainloopTag
    const tag = sdk.trainloopTag('explicit-init-test');
    expect(tag).toHaveProperty(sdk.HEADER_NAME, 'explicit-init-test');
  });

  it('should complete full lifecycle: init -> API call -> flush -> shutdown', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    const sdk = await import('../../src');

    // 1. Initialize
    await sdk.collect(false); // Use batch mode for this test

    // 2. Make API call
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Lifecycle test' }],
    }, {
      headers: { ...sdk.trainloopTag('lifecycle-test') }
    });

    // 3. Flush events
    await expect(sdk.flush()).resolves.not.toThrow();

    // 4. Verify events were written
    const eventsDir = path.join(testDataFolder, 'events');
    expect(fs.existsSync(eventsDir)).toBe(true);
    
    const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventFiles.length).toBeGreaterThan(0);

    // 5. Verify event content
    const eventFile = path.join(eventsDir, eventFiles[0]);
    const eventContent = fs.readFileSync(eventFile, 'utf8');
    const events = eventContent.trim().split('\n').map(line => JSON.parse(line));
    
    expect(events.some(event => event.tag === 'lifecycle-test')).toBe(true);

    // 6. Shutdown
    await expect(sdk.shutdown()).resolves.not.toThrow();
  });

  it('should handle multiple collect() calls gracefully', async () => {
    const sdk = await import('../../src');

    // Multiple calls to collect should be idempotent
    expect(() => sdk.collect(true)).not.toThrow();
    expect(() => sdk.collect(true)).not.toThrow();
    expect(() => sdk.collect(false)).not.toThrow();

    // Should still work normally
    const tag = sdk.trainloopTag('multi-collect-test');
    expect(tag).toHaveProperty(sdk.HEADER_NAME, 'multi-collect-test');
  });

  it('should handle SDK without TRAINLOOP_DATA_FOLDER gracefully', async () => {
    // Remove data folder to test disabled state
    delete process.env.TRAINLOOP_DATA_FOLDER;

    const sdk = await import('../../src');

    // Should initialize without throwing
    expect(() => sdk.collect(true)).not.toThrow();

    // Functions should still be available but SDK is disabled
    const tag = sdk.trainloopTag('disabled-test');
    expect(tag).toHaveProperty(sdk.HEADER_NAME, 'disabled-test');

    // Should handle flush and shutdown gracefully
    await expect(sdk.flush()).resolves.not.toThrow();
    await expect(sdk.shutdown()).resolves.not.toThrow();
  });

  it('should create and update registry properly', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    const sdk = await import('../../src');
    await sdk.collect(true);

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Registry test' }],
    }, {
      headers: { ...sdk.trainloopTag('registry-test') }
    });

    // Check that registry was created
    const registryPath = path.join(testDataFolder, '_registry.json');
    expect(fs.existsSync(registryPath)).toBe(true);

    // Verify registry content
    const registryContent = fs.readFileSync(registryPath, 'utf8');
    const registry = JSON.parse(registryContent);
    
    expect(registry).toHaveProperty('schema', 1);
    expect(registry).toHaveProperty('files');
    expect(Object.keys(registry.files).length).toBeGreaterThan(0);

    // Should have an entry for our test call
    const entries = Object.values(registry.files).flatMap(file => 
      Object.values(file as any)
    ) as any[];
    
    expect(entries.some(entry => entry.tag === 'registry-test')).toBe(true);
  });
});