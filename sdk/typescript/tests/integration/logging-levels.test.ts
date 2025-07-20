import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { SpyInstance } from 'jest-mock';
import * as fs from 'fs';
import * as path from 'path';
import { collect, shutdown, trainloopTag } from '../../src';
import OpenAI from 'openai';

describe('Logging Levels Integration Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-logging');
  let consoleLogSpy: SpyInstance;
  let consoleDebugSpy: SpyInstance;
  let consoleInfoSpy: SpyInstance;
  let consoleWarnSpy: SpyInstance;
  let consoleErrorSpy: SpyInstance;

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

    // Spy on console methods
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    consoleDebugSpy = jest.spyOn(console, 'debug').mockImplementation(() => {});
    consoleInfoSpy = jest.spyOn(console, 'info').mockImplementation(() => {});
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    // Clear module cache to ensure fresh initialization
    jest.resetModules();
  });

  afterEach(async () => {
    await shutdown();
    
    // Restore console methods
    consoleLogSpy.mockRestore();
    consoleDebugSpy.mockRestore();
    consoleInfoSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();

    // Clean up test data
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }
  });

  it('should show debug logs when TRAINLOOP_LOG_LEVEL=DEBUG', async () => {
    // Set up environment
    process.env.TRAINLOOP_LOG_LEVEL = 'DEBUG';
    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';

    // Re-import to get fresh module with correct log level
    const { collect: freshCollect } = await import('../../src');
    
    await freshCollect(true);

    // Check that debug logs were written
    const debugLogs = consoleDebugSpy.mock.calls
      .filter(call => (call[0] as string)?.includes('[DEBUG]'))
      .map(call => call[0] as string);

    expect(debugLogs.length).toBeGreaterThan(0);
    expect(debugLogs.some(log => log.includes('collect() called'))).toBe(true);
    expect(debugLogs.some(log => log.includes('Loading config'))).toBe(true);
  });

  it('should show INFO logs for HTTP instrumentation with debug level', async () => {
    // Skip if no OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping OpenAI test - no API key');
      return;
    }

    // Set up environment with debug level
    process.env.TRAINLOOP_LOG_LEVEL = 'DEBUG';
    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com';

    // Re-import to get fresh module with correct log level
    const { collect: freshCollect, trainloopTag: freshTag } = await import('../../src');
    
    await freshCollect(true);

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Make API call
    await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Say hello' }],
    }, {
      headers: { ...freshTag('info-log-test') }
    });

    // Check for INFO logs from fetch instrumentation
    const infoLogs = consoleInfoSpy.mock.calls
      .filter(call => (call[0] as string)?.includes('[INFO]'))
      .map(call => call[0] as string);

    expect(infoLogs.some(log => log.includes('START FETCH CALL'))).toBe(true);
    expect(infoLogs.some(log => log.includes('END FETCH CALL'))).toBe(true);
    expect(infoLogs.some(log => log.includes('Method: POST'))).toBe(true);
    expect(infoLogs.some(log => log.includes('api.openai.com'))).toBe(true);
  });

  it('should not show debug logs when TRAINLOOP_LOG_LEVEL=WARN', async () => {
    // Set up environment
    process.env.TRAINLOOP_LOG_LEVEL = 'WARN';
    process.env.TRAINLOOP_DATA_FOLDER = testDataFolder;

    // Re-import to get fresh module with correct log level
    const { collect: freshCollect } = await import('../../src');
    
    await freshCollect(true);

    // Check that no debug logs were written
    const debugLogs = consoleDebugSpy.mock.calls
      .filter(call => (call[0] as string)?.includes('[DEBUG]'));

    expect(debugLogs.length).toBe(0);

    // But warnings should still appear
    const warnLogs = consoleWarnSpy.mock.calls;
    // Note: There might not be any warnings in normal operation
  });
});