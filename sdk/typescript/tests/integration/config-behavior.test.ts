import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

describe('Config Loading Behavior Integration Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-config');
  const configPath = path.join(testDataFolder, 'trainloop.config.yaml');
  
  const testConfig = {
    trainloop: {
      data_folder: 'data',
      host_allowlist: ['api.test1.com', 'api.test2.com'],
      log_level: 'info'
    }
  };

  beforeEach(() => {
    // Clean up test data folder
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }
    fs.mkdirSync(testDataFolder, { recursive: true });

    // Create test config file
    fs.writeFileSync(configPath, yaml.dump(testConfig));

    // Clear all environment variables
    delete process.env.TRAINLOOP_DATA_FOLDER;
    delete process.env.TRAINLOOP_HOST_ALLOWLIST;
    delete process.env.TRAINLOOP_LOG_LEVEL;
    delete process.env.TRAINLOOP_CONFIG_PATH;

    // Clear module cache to ensure fresh initialization
    jest.resetModules();
  });

  afterEach(() => {
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

  it('should load all values from config when no env vars are set', async () => {
    // Set config path to our test config
    process.env.TRAINLOOP_CONFIG_PATH = configPath;
    
    // Import fresh module
    await import('../../src');

    // Check that config values were loaded
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(path.join(testDataFolder, 'data'));
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('api.test1.com,api.test2.com');
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('INFO');
  });

  it('should merge env vars with config, preferring env vars', async () => {
    // Set config path and one env var
    process.env.TRAINLOOP_CONFIG_PATH = configPath;
    process.env.TRAINLOOP_LOG_LEVEL = 'WARN';
    
    // Import fresh module
    await import('../../src');

    // Check that env var takes precedence
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('WARN');
    
    // But other values come from config
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(path.join(testDataFolder, 'data'));
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('api.test1.com,api.test2.com');
  });

  it('should not override any env vars when all are set', async () => {
    // Set all env vars
    process.env.TRAINLOOP_CONFIG_PATH = configPath;
    process.env.TRAINLOOP_DATA_FOLDER = '/custom/path';
    process.env.TRAINLOOP_HOST_ALLOWLIST = 'custom.com';
    process.env.TRAINLOOP_LOG_LEVEL = 'ERROR';
    
    // Import fresh module
    await import('../../src');

    // Check that all env vars remain unchanged
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe('/custom/path');
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('custom.com');
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('ERROR');
  });

  it('should resolve relative data_folder paths relative to config file', async () => {
    // Create config in a subdirectory
    const subDir = path.join(testDataFolder, 'subdir');
    fs.mkdirSync(subDir, { recursive: true });
    const subConfigPath = path.join(subDir, 'trainloop.config.yaml');
    fs.writeFileSync(subConfigPath, yaml.dump(testConfig));
    
    process.env.TRAINLOOP_CONFIG_PATH = subConfigPath;
    
    // Import fresh module
    await import('../../src');

    // data_folder should be resolved relative to the config file location
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBe(path.join(subDir, 'data'));
  });

  it('should use defaults when config file is missing', async () => {
    // Point to non-existent config
    process.env.TRAINLOOP_CONFIG_PATH = path.join(testDataFolder, 'missing.yaml');
    
    // Import fresh module
    await import('../../src');

    // Should use defaults
    expect(process.env.TRAINLOOP_DATA_FOLDER).toBeUndefined();
    expect(process.env.TRAINLOOP_HOST_ALLOWLIST).toBe('api.openai.com,api.anthropic.com');
    expect(process.env.TRAINLOOP_LOG_LEVEL).toBe('WARN');
  });
});