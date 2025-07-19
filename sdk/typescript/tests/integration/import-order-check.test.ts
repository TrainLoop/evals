import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

describe('Import Order Check Integration Test', () => {
  const testDataFolder = path.join(__dirname, 'test-data-import-order');
  const fixturesDir = path.join(__dirname, 'fixtures');

  beforeEach(() => {
    // Clean up test data folder
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }
    if (fs.existsSync(fixturesDir)) {
      fs.rmSync(fixturesDir, { recursive: true, force: true });
    }
    fs.mkdirSync(fixturesDir, { recursive: true });
  });

  afterEach(() => {
    // Clean up
    if (fs.existsSync(testDataFolder)) {
      fs.rmSync(testDataFolder, { recursive: true, force: true });
    }
    if (fs.existsSync(fixturesDir)) {
      fs.rmSync(fixturesDir, { recursive: true, force: true });
    }
  });

  it('should throw error when HTTP client is imported before SDK initialization', () => {
    // Create a test script that imports OpenAI before TrainLoop
    const wrongOrderScript = `
process.env.TRAINLOOP_DISABLE_AUTO_INIT = 'true';
process.env.TRAINLOOP_DATA_FOLDER = '${testDataFolder}';

// Wrong: Import HTTP client first
const OpenAI = require('openai');

// Then try to initialize TrainLoop
const { collect } = require('${path.resolve(__dirname, '../../dist/index.js')}');

try {
  collect(true);
  console.log('ERROR: This should not be reached');
  process.exit(1);
} catch (error) {
  if (error.message.includes('TrainLoop SDK must be initialized before importing')) {
    console.log('SUCCESS: Error caught as expected');
    process.exit(0);
  } else {
    console.error('UNEXPECTED ERROR:', error.message);
    process.exit(1);
  }
}
`;

    const scriptPath = path.join(fixturesDir, 'wrong-order.js');
    fs.writeFileSync(scriptPath, wrongOrderScript);

    // Run the script and check it exits with success (0)
    const result = execSync(`node ${scriptPath}`, { 
      encoding: 'utf8',
      stdio: 'pipe'
    });
    
    expect(result).toContain('SUCCESS: Error caught as expected');
  });

  it('should work correctly when SDK is initialized before HTTP client', () => {
    // Create a test script with correct import order
    const correctOrderScript = `
process.env.TRAINLOOP_DISABLE_AUTO_INIT = 'true';
process.env.TRAINLOOP_DATA_FOLDER = '${testDataFolder}';
process.env.TRAINLOOP_LOG_LEVEL = 'error'; // Reduce noise

// Correct: Initialize TrainLoop first
const { collect } = require('${path.resolve(__dirname, '../../dist/index.js')}');
collect(true);

// Then import HTTP client
const OpenAI = require('openai');

console.log('SUCCESS: No errors with correct import order');
`;

    const scriptPath = path.join(fixturesDir, 'correct-order.js');
    fs.writeFileSync(scriptPath, correctOrderScript);

    // Run the script
    const result = execSync(`node ${scriptPath}`, { 
      encoding: 'utf8',
      stdio: 'pipe'
    });
    
    expect(result).toContain('SUCCESS: No errors with correct import order');
  });

  it('should detect multiple HTTP client libraries', () => {
    // Create a test script that imports multiple libraries
    const multipleLibsScript = `
process.env.TRAINLOOP_DISABLE_AUTO_INIT = 'true';
process.env.TRAINLOOP_DATA_FOLDER = '${testDataFolder}';

// Import multiple HTTP clients
try {
  require('openai');
} catch (e) {}
try {
  require('axios');
} catch (e) {}

const { collect } = require('${path.resolve(__dirname, '../../dist/index.js')}');

try {
  collect(true);
  console.log('ERROR: This should not be reached');
  process.exit(1);
} catch (error) {
  if (error.message.includes('openai')) {
    console.log('SUCCESS: Detected openai import');
    process.exit(0);
  } else {
    console.error('UNEXPECTED ERROR:', error.message);
    process.exit(1);
  }
}
`;

    const scriptPath = path.join(fixturesDir, 'multiple-libs.js');
    fs.writeFileSync(scriptPath, multipleLibsScript);

    // Run the script
    const result = execSync(`node ${scriptPath}`, { 
      encoding: 'utf8',
      stdio: 'pipe'
    });
    
    expect(result).toContain('SUCCESS: Detected openai import');
  });
});