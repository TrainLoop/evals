/**
 * Tests for config loading precedence and behavior
 */
import { loadConfig } from '../../src/config';
import * as fs from 'fs';
import * as path from 'path';
import { jest } from '@jest/globals';
import { createTempDir, cleanupTempDir, createMockConfig } from '../test-utils';

describe('Config Precedence', () => {
  let tempDir: string;
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    tempDir = createTempDir();
    originalEnv = { ...process.env };
    
    // Clear all TrainLoop env vars
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;
    delete process.env.TRAINLOOP_CONFIG_PATH;
  });

  afterEach(() => {
    process.env = originalEnv;
    cleanupTempDir(tempDir);
  });

  it('should load config values when only some env vars are set', () => {
    // Set only log level in env
    process.env.TRAINLOOP_LOG_LEVEL = 'ERROR';
    
    // Create config with all values
    const configPath = createMockConfig(tempDir, {
      trainloop: {
        data_folder: './config-data',
        host_allowlist: ['api.openai.com', 'api.custom.com'],
        log_level: 'debug'
      }
    });
    process.env.TRAINLOOP_CONFIG_PATH = configPath;

    const consoleSpy = jest.spyOn(console, 'debug').mockImplementation();

    loadConfig();

    // Log level should come from env (ERROR)
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('ERROR');
    
    // Data folder should come from config
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(
      path.resolve(tempDir, './config-data')
    );
    
    // Host allowlist should come from config
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('api.openai.com,api.custom.com');

    // Should log what came from where
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Using config values for: data_folder, host_allowlist')
    );
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Using environment variables for: log_level')
    );

    consoleSpy.mockRestore();
  });

  it('should use all config values when no env vars are set', () => {
    const configPath = createMockConfig(tempDir, {
      trainloop: {
        data_folder: './all-from-config',
        host_allowlist: ['api.test.com'],
        log_level: 'info'
      }
    });
    process.env.TRAINLOOP_CONFIG_PATH = configPath;

    const consoleSpy = jest.spyOn(console, 'debug').mockImplementation();

    loadConfig();

    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(
      path.resolve(tempDir, './all-from-config')
    );
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('api.test.com');
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('INFO');

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Using config values for: data_folder, host_allowlist, log_level')
    );

    consoleSpy.mockRestore();
  });

  it('should use all env vars when all are set', () => {
    // Set all env vars
    process.env.TRAINLOOP_DATA_FOLDER = '/env/data';
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'env.api.com';
    process.env.TRAINLOOP_LOG_LEVEL = 'WARN';

    // Create config with different values
    const configPath = createMockConfig(tempDir, {
      trainloop: {
        data_folder: './config-data',
        host_allowlist: ['config.api.com'],
        log_level: 'debug'
      }
    });
    process.env.TRAINLOOP_CONFIG_PATH = configPath;

    const consoleSpy = jest.spyOn(console, 'debug').mockImplementation();

    loadConfig();

    // All values should come from env, not config
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe('/env/data');
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('env.api.com');
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('WARN');

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Using environment variables for: data_folder, host_allowlist, log_level')
    );

    consoleSpy.mockRestore();
  });

  it('should uppercase log level from config', () => {
    const configPath = createMockConfig(tempDir, {
      trainloop: {
        data_folder: './data',
        log_level: 'debug' // lowercase in config
      }
    });
    process.env.TRAINLOOP_CONFIG_PATH = configPath;

    loadConfig();

    // Should be uppercase
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('DEBUG');
  });

  it('should handle mixed case scenarios', () => {
    // Set data folder and host allowlist in env
    process.env.TRAINLOOP_DATA_FOLDER = '/env/data';
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'env.api.com';
    
    // Config has all three, but only log_level should be used
    const configPath = createMockConfig(tempDir, {
      trainloop: {
        data_folder: './config-data',
        host_allowlist: ['config.api.com'],
        log_level: 'info'
      }
    });
    process.env.TRAINLOOP_CONFIG_PATH = configPath;

    loadConfig();

    // Data folder and host allowlist from env
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe('/env/data');
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('env.api.com');
    
    // Log level from config
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('INFO');
  });
});