import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';
import OpenAI from 'openai';

describe('Auto-Initialization Integration Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-auto-init');

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

  it('should auto-initialize when SDK is imported', async () => {
    // Import SDK - this triggers auto-initialization
    const sdk = await import('../../src');

    // Verify auto-initialization sets up environment correctly
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(testDataFolder);
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('api.openai.com');
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('DEBUG');

    // Verify SDK exports are available
    expect(sdk.collect).toBeDefined();
    expect(sdk.trainloopTag).toBeDefined();
    expect(sdk.flush).toBeDefined();
    expect(sdk.shutdown).toBeDefined();
  });

  it('should capture events without explicit collect() call', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    // Import SDK (auto-initializes)
    const sdk = await import('../../src');

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Make API call without explicit collect() - should work due to auto-init
    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Auto-init test' }],
    }, {
      headers: { ...sdk.trainloopTag('auto-init-test') }
    });

    // Force a flush to ensure events are written
    await sdk.flush();

    // Verify events were captured
    const eventsDir = path.join(testDataFolder, 'events');
    expect(fs.existsSync(eventsDir)).toBe(true);

    const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventFiles.length).toBeGreaterThan(0);

    // Verify event content
    const eventFile = path.join(eventsDir, eventFiles[0]);
    const eventContent = fs.readFileSync(eventFile, 'utf8');
    const events = eventContent.trim().split('\n').map(line => JSON.parse(line));

    expect(events.some(event => event.tag === 'auto-init-test')).toBe(true);
  });

  it('should handle module loading order correctly', async () => {
    // Test that auto-initialization works even when environment is set after module load
    // This simulates the dotenv.config() loading order issue

    // Clear environment
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;

    // Import SDK with no environment set (should not crash)
    const sdk = await import('../../src');

    // Now set environment (simulating dotenv loading after require)
    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';
    process.env.TRAINLOOP_LOG_LEVEL = 'DEBUG';

    // Try to use SDK (should work, though might not capture events without re-init)
    const tag = sdk.trainloopTag('late-env-test');
    expect(tag).toHaveProperty(sdk.HEADER_NAME, 'late-env-test');

    // Explicit collect should pick up new environment
    sdk.collect(true);
  });

  it('should work with NODE_OPTIONS pattern', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    // This test simulates what happens when using NODE_OPTIONS="--require=trainloop-llm-logging"
    // The SDK is imported before user code runs

    // Import SDK first (simulating NODE_OPTIONS)
    const sdk = await import('../../src');

    // Then user code runs
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'NODE_OPTIONS test' }],
    }, {
      headers: { ...sdk.trainloopTag('node-options-test') }
    });

    // Without explicit flush, events might not be written for short scripts
    // But explicit flush should work
    await sdk.flush();

    // Verify events were written
    const eventsDir = path.join(testDataFolder, 'events');
    expect(fs.existsSync(eventsDir)).toBe(true);

    const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventFiles.length).toBeGreaterThan(0);
  });

  it('should gracefully handle disabled state when no data folder is set', async () => {
    // Clear data folder to test disabled state
    delete process.env.TRAINLOOP_DATA_FOLDER;

    // Import SDK - should not crash even when disabled
    const sdk = await import('../../src');

    // SDK functions should be available but disabled
    expect(sdk.collect).toBeDefined();
    expect(sdk.trainloopTag).toBeDefined();
    expect(sdk.flush).toBeDefined();
    expect(sdk.shutdown).toBeDefined();

    // trainloopTag should still work
    const tag = sdk.trainloopTag('disabled-test');
    expect(tag).toHaveProperty(sdk.HEADER_NAME, 'disabled-test');

    // These should not throw even when SDK is disabled
    expect(() => sdk.collect(true)).not.toThrow();
    await expect(sdk.flush()).resolves.not.toThrow();
    await expect(sdk.shutdown()).resolves.not.toThrow();
  });
});