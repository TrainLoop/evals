/**
 * Unit tests for config loading functionality
 */
import { loadConfig } from '../../src/config';
import * as fs from 'fs';
import * as path from 'path';
import { createTempDir, cleanupTempDir, createMockConfig, mockEnvVars } from '../test-utils';
import { describe, it, beforeEach, afterEach, expect, jest } from '@jest/globals';

describe('Config Loading', () => {
  let tempDir: string;
  let cleanupEnv: () => void;

  beforeEach(() => {
    tempDir = createTempDir();
    cleanupEnv = mockEnvVars({});
  });

  afterEach(() => {
    cleanupEnv();
    cleanupTempDir(tempDir);
  });

  describe('loadConfig', () => {
    it('should load config from YAML file', () => {
      const configPath = createMockConfig(tempDir);
      process.env.TRAINLOOP_CONFIG_PATH = configPath;

      loadConfig();

      expect(process.env.TRAINLOOP_DATA_FOLDER).toContain('data');
      expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toContain('api.openai.com');
      expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toContain('api.anthropic.com');
      expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toContain('generativelanguage.googleapis.com');
      expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('DEBUG');
    });

    it('should not override existing environment variables', () => {
      process.env.TRAINLOOP_DATA_FOLDER = '/custom/path';
      process.env.TRAINLOOP_HOST_ALLOWLIST = 'custom.api.com';
      process.env.TRAINLOOP_LOG_LEVEL = 'INFO';

      const configPath = createMockConfig(tempDir);
      process.env.TRAINLOOP_CONFIG_PATH = configPath;

      loadConfig();

      expect(process.env.TRAINLOOP_DATA_FOLDER).toBe('/custom/path');
      expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('custom.api.com');
      expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('INFO');
    });

    it('should handle missing config file gracefully', () => {
      // Set TRAINLOOP_DATA_FOLDER to prevent error
      process.env.TRAINLOOP_DATA_FOLDER = tempDir;
      process.env.TRAINLOOP_CONFIG_PATH = path.join(tempDir, 'nonexistent.yaml');

      // Should not throw when config file is missing but env var is set
      expect(() => loadConfig()).not.toThrow();
      
      // Data folder should remain as set
      expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(tempDir);
    });

    it('should auto-discover config in trainloop directory', () => {
      const originalCwd = process.cwd();
      const projectDir = path.join(tempDir, 'project');
      const trainloopDir = path.join(projectDir, 'trainloop');
      
      fs.mkdirSync(projectDir, { recursive: true });
      fs.mkdirSync(trainloopDir, { recursive: true });
      
      const yaml = require('js-yaml');
      fs.writeFileSync(
        path.join(trainloopDir, 'trainloop.config.yaml'),
        yaml.dump({
          trainloop: {
            data_folder: './test-data',
            log_level: 'warn'
          }
        })
      );

      try {
        process.chdir(projectDir);
        loadConfig();

        expect(process.env.TRAINLOOP_DATA_FOLDER).toContain('test-data');
        expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('WARN');
      } finally {
        process.chdir(originalCwd);
      }
    });

    it('should handle malformed YAML gracefully', () => {
      // Set TRAINLOOP_DATA_FOLDER to prevent error
      process.env.TRAINLOOP_DATA_FOLDER = tempDir;
      
      const configPath = path.join(tempDir, 'bad.yaml');
      fs.writeFileSync(configPath, '{ invalid: yaml: content');
      process.env.TRAINLOOP_CONFIG_PATH = configPath;

      // Should not throw when YAML is malformed but env var is set
      expect(() => loadConfig()).not.toThrow();
      
      // Data folder should remain as set
      expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(tempDir);
    });

    it('should resolve absolute paths correctly', () => {
      const configPath = createMockConfig(tempDir, {
        trainloop: {
          data_folder: '/absolute/path/to/data'
        }
      });
      process.env.TRAINLOOP_CONFIG_PATH = configPath;

      loadConfig();

      expect(process.env.TRAINLOOP_DATA_FOLDER).toBe('/absolute/path/to/data');
    });

    it('should resolve relative paths relative to config directory', () => {
      const configDir = path.join(tempDir, 'config');
      fs.mkdirSync(configDir);
      
      const configPath = createMockConfig(configDir, {
        trainloop: {
          data_folder: './data'
        }
      });
      process.env.TRAINLOOP_CONFIG_PATH = configPath;

      loadConfig();

      expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(path.join(configDir, 'data'));
    });

    it('should handle empty data folder path', () => {
      const configPath = createMockConfig(tempDir, {
        trainloop: {
          data_folder: ''
        }
      });
      process.env.TRAINLOOP_CONFIG_PATH = configPath;

      // Should warn when data_folder is empty (no longer throws)
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
      loadConfig();
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('TRAINLOOP_DATA_FOLDER not set')
      );
      consoleSpy.mockRestore();
    });

    it('should set default host allowlist if not specified', () => {
      const configPath = createMockConfig(tempDir, {
        trainloop: {
          data_folder: './data'
          // No host_allowlist specified
        }
      });
      process.env.TRAINLOOP_CONFIG_PATH = configPath;

      loadConfig();

      expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toContain('api.openai.com');
      expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toContain('api.anthropic.com');
      expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toContain('generativelanguage.googleapis.com');
    });

    it('should set default log level if not specified', () => {
      const configPath = createMockConfig(tempDir, {
        trainloop: {
          data_folder: './data'
          // No log_level specified
        }
      });
      process.env.TRAINLOOP_CONFIG_PATH = configPath;

      loadConfig();

      expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('WARN');
    });
  });
});
