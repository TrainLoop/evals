/**
 * Jest setup file - runs before all tests
 */
import { TextEncoder, TextDecoder } from 'util';
import * as os from 'os';
import * as path from 'path';

// Polyfill for Node.js environments that don't have these globals
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

// Set test environment variables before any modules are imported
process.env.NODE_ENV = 'test';
process.env.TRAINLOOP_DATA_FOLDER = path.join(os.tmpdir(), 'trainloop-test-data');
process.env.TRAINLOOP_HOST_ALLOWLIST = 'api.openai.com,api.anthropic.com';
process.env.TRAINLOOP_LOG_LEVEL = 'ERROR'; // Suppress logs during tests

// Mock the FileExporter to prevent background timer in tests
jest.mock('../src/exporter', () => ({
  FileExporter: jest.fn().mockImplementation(() => ({
    recordLLMCall: jest.fn(),
    shutdown: jest.fn(),
    clear: jest.fn(),
    flush: jest.fn()
  }))
}));

// Suppress console output during tests unless explicitly needed
const originalConsole = { ...console };
beforeAll(() => {
  console.log = jest.fn();
  console.info = jest.fn();
  console.warn = jest.fn();
  console.error = jest.fn();
  console.debug = jest.fn();
});

afterAll(async () => {
  console.log = originalConsole.log;
  console.info = originalConsole.info;
  console.warn = originalConsole.warn;
  console.error = originalConsole.error;
  console.debug = originalConsole.debug;
  
  // Clean up SDK resources
  const { shutdown } = await import('../src/index');
  await shutdown();
});

// Clear all mocks between tests
afterEach(() => {
  jest.clearAllMocks();
  jest.restoreAllMocks();
});

// Increase timeout for async operations
jest.setTimeout(10000);
