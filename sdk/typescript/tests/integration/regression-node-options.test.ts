import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';
import OpenAI from 'openai';

describe('NODE_OPTIONS Regression Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-node-options');

  beforeEach(() => {
    // Clean up test data folder
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }

    // Clear all TrainLoop environment variables to simulate clean slate
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;
    delete process.env.TRAINLOOP_CONFIG_PATH;

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

  it('should handle NODE_OPTIONS loading order correctly (regression test)', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    // This test reproduces the original issue:
    // 1. SDK is required via NODE_OPTIONS (before dotenv and user script)
    // 2. Environment variables are undefined when SDK loads
    // 3. Later, dotenv sets the variables
    // 4. SDK should still work correctly

    // Step 1: Simulate NODE_OPTIONS require (SDK loaded with no env vars)
    const sdk = await import('../../src');

    // At this point, TRAINLOOP_LOG_LEVEL might be undefined
    const initialLogLevel = process.env.TRAINLOOP_LOG_LEVEL;

    // Step 2: Simulate dotenv.config() setting environment variables
    // This happens AFTER the SDK is already loaded
    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';
    process.env.TRAINLOOP_LOG_LEVEL = 'DEBUG';

    // The SDK should still work even though env vars were set after import
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Step 3: Make API call (this was the failing scenario)
    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Regression test' }],
    }, {
      headers: { ...sdk.trainloopTag('node-options-regression') }
    });

    // Step 4: Force flush to ensure events are written
    // (Original issue: events were buffered but never written)
    await sdk.flush();

    // Step 5: Verify events were written despite the timing issue
    const eventsDir = path.join(testDataFolder, 'events');
    expect(fs.existsSync(eventsDir)).toBe(true);

    const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventFiles.length).toBeGreaterThan(0);

    // Verify event content
    const eventFile = path.join(eventsDir, eventFiles[0]);
    const eventContent = fs.readFileSync(eventFile, 'utf8');
    const events = eventContent.trim().split('\n').map(line => JSON.parse(line));

    expect(events.some(event => event.tag === 'node-options-regression')).toBe(true);
  });

  it('should work with config file loading after SDK import', async () => {
    // Create a config file
    const configDir = path.join(testDataFolder, 'config');
    fs.mkdirSync(configDir, { recursive: true });
    const configPath = path.join(configDir, 'trainloop.config.yaml');
    
    const configContent = `
trainloop:
  data_folder: data
  host_allowlist:
    - api.openai.com
  log_level: debug
`;
    fs.writeFileSync(configPath, configContent);

    // Step 1: Import SDK without any env vars (simulating NODE_OPTIONS)
    const sdk = await import('../../src');

    // Step 2: Set config path after SDK import (simulating dotenv loading)
    process.env.TRAINLOOP_CONFIG_PATH = configPath;

    // Step 3: Explicit collect should load the config
    await sdk.collect(true);

    // Verify config was loaded
    expect(process.env.TRAINLOOP_DATA_FOLDER).toContain('data');
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('api.openai.com');
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('DEBUG');
  });

  it('should handle short-lived script scenario', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    // This simulates the scenario where:
    // 1. NODE_OPTIONS loads the SDK
    // 2. Script makes a quick API call
    // 3. Script exits before timer-based flush occurs
    // 4. Events should still be written with proper flush

    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';

    // Import SDK (auto-initializes)
    const sdk = await import('../../src');

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Make API call without explicit collect (relies on auto-init)
    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Short script test' }],
    }, {
      headers: { ...sdk.trainloopTag('short-script') }
    });

    // Simulate script ending - this should trigger shutdown flush
    await sdk.shutdown();

    // Verify events were written despite short execution time
    const eventsDir = path.join(testDataFolder, 'events');
    expect(fs.existsSync(eventsDir)).toBe(true);

    const eventFiles = fs.readdirSync(eventsDir).filter(f => f.endsWith('.jsonl'));
    expect(eventFiles.length).toBeGreaterThan(0);

    const eventFile = path.join(eventsDir, eventFiles[0]);
    const eventContent = fs.readFileSync(eventFile, 'utf8');
    const events = eventContent.trim().split('\n').map(line => JSON.parse(line));

    expect(events.some(event => event.tag === 'short-script')).toBe(true);
  });

  it('should handle logger timing issue correctly', async () => {
    // This test specifically targets the logger timing issue
    // where loggers were created before config was loaded

    // Import SDK without log level set
    const sdk = await import('../../src');

    // Set log level after import (simulating the timing issue)
    process.env.TRAINLOOP_LOG_LEVEL = 'DEBUG';
    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';

    // Capture console output to verify debug logs appear
    const consoleSpy = jest.spyOn(console, 'debug').mockImplementation();

    try {
      // Re-initialize to pick up the new log level
      await sdk.collect(true);

      // Debug logs should now appear (with lazy logger fix)
      const debugLogs = consoleSpy.mock.calls
        .filter(call => call[0]?.includes('[DEBUG]'))
        .map(call => call[0]);

      // With the fix, we should see debug logs
      expect(debugLogs.length).toBeGreaterThan(0);
    } finally {
      consoleSpy.mockRestore();
    }
  });
});