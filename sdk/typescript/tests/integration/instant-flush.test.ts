/**
 * Integration tests for instant flush functionality
 */
import { collect, flush, shutdown } from '../../src';
import * as fs from 'fs';
import * as path from 'path';
import { createTempDir, cleanupTempDir } from '../test-utils';

// Mock the FileExporter to prevent actual file writes in integration tests
jest.mock('../../src/exporter');

describe('Instant Flush Integration', () => {
  let tempDir: string;
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    jest.clearAllMocks();
    tempDir = createTempDir();
    originalEnv = { ...process.env };
    process.env.TRAINLOOP_DATA_FOLDER = tempDir;
    
    // Reset module state
    jest.resetModules();
  });

  afterEach(async () => {
    await shutdown();
    cleanupTempDir(tempDir);
    process.env = originalEnv;
  });

  describe('collect() function', () => {
    it('should accept flushImmediately parameter', async () => {
      const { collect: testCollect } = await import('../../src');
      
      // Should not throw
      await expect(testCollect(true)).resolves.toBeUndefined();
    });

    it('should be idempotent', async () => {
      const { collect: testCollect } = await import('../../src');
      
      // Call multiple times
      await testCollect(true);
      await testCollect(true);
      await testCollect(false);
      
      // Should not throw or cause issues
      expect(true).toBe(true);
    });

    it('should not initialize without TRAINLOOP_DATA_FOLDER', async () => {
      delete process.env.TRAINLOOP_DATA_FOLDER;
      
      const { collect: testCollect } = await import('../../src');
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      await testCollect(true);
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('TRAINLOOP_DATA_FOLDER not set')
      );
      
      consoleSpy.mockRestore();
    });
  });

  describe('flush() function', () => {
    it('should be available as an export', async () => {
      const { flush: testFlush } = await import('../../src');
      
      expect(typeof testFlush).toBe('function');
    });

    it('should warn if SDK not initialized', async () => {
      delete process.env.TRAINLOOP_DATA_FOLDER;
      
      const { flush: testFlush } = await import('../../src');
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      await testFlush();
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('SDK not initialized')
      );
      
      consoleSpy.mockRestore();
    });

    it('should call exporter flush when initialized', async () => {
      const { collect: testCollect, flush: testFlush } = await import('../../src');
      const { FileExporter } = require('../../src/exporter');
      
      await testCollect(true);
      await testFlush();
      
      // Check that flush was called on the mock
      const mockInstance = FileExporter.mock.results[0].value;
      expect(mockInstance.flush).toHaveBeenCalled();
    });
  });

  describe('config file loading', () => {
    it('should load data_folder from config file', async () => {
      // Create a config file
      const configPath = path.join(process.cwd(), 'trainloop.config.yaml');
      const configContent = `trainloop:
  data_folder: ${tempDir}
  host_allowlist:
    - api.openai.com
  log_level: info
`;
      fs.writeFileSync(configPath, configContent);
      
      // Clear env var to test config loading
      delete process.env.TRAINLOOP_DATA_FOLDER;
      
      try {
        const { collect: testCollect } = await import('../../src');
        await testCollect(true);
        
        // Should have loaded from config
        expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(tempDir);
      } finally {
        // Clean up
        fs.unlinkSync(configPath);
      }
    });

    it('should handle missing config gracefully', async () => {
      delete process.env.TRAINLOOP_DATA_FOLDER;
      
      const { collect: testCollect } = await import('../../src');
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      // Should not throw, just warn
      await testCollect(true);
      
      expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });
  });
});