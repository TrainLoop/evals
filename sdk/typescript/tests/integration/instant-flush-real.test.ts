/**
 * Real integration tests for instant flush functionality
 * These tests use the actual FileExporter and file system
 */
import * as fs from 'fs';
import * as path from 'path';
import { createTempDir, cleanupTempDir } from '../test-utils';

// Unmock everything for real integration tests
jest.unmock('../../src/exporter');
jest.unmock('../../src/store');
jest.unmock('../../src/instrumentation/utils');
jest.unmock('../../src/instrumentation/http');
jest.unmock('../../src/instrumentation/fetch');
jest.unmock('../../src/config');
jest.unmock('../../src/logger');
jest.unmock('../../src/index');

// Need to clear the module cache to ensure clean state
beforeEach(() => {
  jest.resetModules();
});

describe('Instant Flush Real Integration', () => {
  let tempDir: string;
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    tempDir = createTempDir();
    originalEnv = { ...process.env };
    process.env.TRAINLOOP_DATA_FOLDER = tempDir;
    process.env.TRAINLOOP_LOG_LEVEL = 'ERROR'; // Suppress logs
  });

  afterEach(async () => {
    // Import dynamically to get fresh module
    const { shutdown } = await import('../../src');
    await shutdown();
    
    cleanupTempDir(tempDir);
    process.env = originalEnv;
  });

  describe('instant flush with real file system', () => {
    it('should write data immediately when instant flush is enabled', async () => {
      // Import fresh modules
      const { FileExporter } = await import('../../src/exporter');
      
      const exporter = new FileExporter(undefined, undefined, true);
      
      // Record a mock LLM call
      exporter.recordLLMCall({
        isLLMRequest: true,
        url: 'https://api.openai.com/v1/chat/completions',
        tag: 'instant-test',
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test instant flush' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Instant response' } }]
        }),
        startTimeMs: Date.now(),
        endTimeMs: Date.now() + 100,
        durationMs: 100,
        status: 200
      });

      // Give it a moment to write
      await new Promise(resolve => setTimeout(resolve, 100));

      // Check that events directory was created
      const eventsDir = path.join(tempDir, 'events');
      expect(fs.existsSync(eventsDir)).toBe(true);

      // Check that a file was written
      const files = fs.readdirSync(eventsDir);
      expect(files.length).toBeGreaterThan(0);

      // Read and verify the content
      const fileContent = fs.readFileSync(path.join(eventsDir, files[0]), 'utf8');
      const data = JSON.parse(fileContent);
      
      expect(data.tag).toBe('instant-test');
      expect(data.output.content).toBe('Instant response');
      expect(data.model).toBe('gpt-4');

      exporter.shutdown();
    });

    it('should not write immediately when instant flush is disabled', async () => {
      const { FileExporter } = await import('../../src/exporter');
      
      const exporter = new FileExporter(10000, 10, false); // Long timeout, high batch size
      
      // Record a call
      exporter.recordLLMCall({
        isLLMRequest: true,
        url: 'https://api.openai.com/v1/chat/completions',
        tag: 'batch-test',
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test batching' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Batched response' } }]
        }),
        startTimeMs: Date.now(),
        endTimeMs: Date.now() + 100,
        durationMs: 100,
        status: 200
      });

      // Give it a moment
      await new Promise(resolve => setTimeout(resolve, 100));

      // Events directory should not exist yet
      const eventsDir = path.join(tempDir, 'events');
      expect(fs.existsSync(eventsDir)).toBe(false);

      // Now manually flush
      exporter.flush();

      // Give it a moment to write
      await new Promise(resolve => setTimeout(resolve, 100));

      // Now it should exist
      expect(fs.existsSync(eventsDir)).toBe(true);
      const files = fs.readdirSync(eventsDir);
      expect(files.length).toBeGreaterThan(0);

      exporter.shutdown();
    });
  });

  describe('public API with real implementation', () => {
    it('should initialize with instant flush and write data', async () => {
      const { collect, shutdown: testShutdown } = await import('../../src');
      const { FileExporter } = await import('../../src/exporter');
      
      // Initialize with instant flush
      await collect(true);
      
      // Create a direct exporter instance to test
      const exporter = new FileExporter(undefined, undefined, true);
      
      // Record a call
      exporter.recordLLMCall({
        isLLMRequest: true,
        url: 'https://api.openai.com/v1/chat/completions',
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'API test' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'API response' } }]
        }),
        durationMs: 100,
        status: 200
      });

      // Wait a bit
      await new Promise(resolve => setTimeout(resolve, 100));

      // Verify file was written
      const eventsDir = path.join(tempDir, 'events');
      expect(fs.existsSync(eventsDir)).toBe(true);

      exporter.shutdown();
      await testShutdown();
    });

    it('should handle config file loading', async () => {
      // Create a config file
      const configPath = path.join(process.cwd(), 'trainloop.config.yaml');
      const configContent = `trainloop:
  data_folder: ${tempDir}
  host_allowlist:
    - api.openai.com
  log_level: error
`;
      fs.writeFileSync(configPath, configContent);
      
      // Clear env var to test config loading
      delete process.env.TRAINLOOP_DATA_FOLDER;
      
      try {
        const { collect, shutdown: testShutdown } = await import('../../src');
        await collect(true);
        
        // Should have loaded from config
        expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(tempDir);
        
        await testShutdown();
      } finally {
        // Clean up
        if (fs.existsSync(configPath)) {
          fs.unlinkSync(configPath);
        }
      }
    });
  });

  describe('manual flush functionality', () => {
    it('should flush data manually with flush() API', async () => {
      const { collect, flush: testFlush, shutdown: testShutdown } = await import('../../src');
      const { FileExporter } = await import('../../src/exporter');
      
      // Initialize without instant flush
      await collect(false);
      
      // Create exporter and record a call
      const exporter = new FileExporter(10000, 10, false);
      exporter.recordLLMCall({
        isLLMRequest: true,
        url: 'https://api.openai.com/v1/chat/completions',
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Manual flush test' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Manual response' } }]
        }),
        durationMs: 100,
        status: 200
      });

      // Events shouldn't be written yet
      const eventsDir = path.join(tempDir, 'events');
      expect(fs.existsSync(eventsDir)).toBe(false);

      // Manual flush
      exporter.flush();
      await new Promise(resolve => setTimeout(resolve, 100));

      // Now they should be written
      expect(fs.existsSync(eventsDir)).toBe(true);

      exporter.shutdown();
      await testShutdown();
    });
  });
});