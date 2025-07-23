/**
 * Shared test utilities and fixtures for TrainLoop SDK tests
 */
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { LLMCallData, CollectedSample } from '../src/types/shared';
import { patchFetch } from '../src/instrumentation/fetch';
import { patchHttp } from '../src/instrumentation/http';
import http from "http";
import https from "https";
import { FileExporter } from '../src/exporter';
import { resetConfigState } from '../src/config';
/**
 * Create a temporary directory for tests
 */
export function createTempDir(prefix: string = 'trainloop-test-'): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), prefix));
}

export function instrumentAll(exporter: FileExporter) {
  patchHttp(http, exporter);
  patchHttp(https, exporter);
  patchFetch(exporter);
}

/**
 * Clean up a temporary directory
 */
export function cleanupTempDir(dir: string): void {
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

/**
 * Create a mock config file
 */
export function createMockConfig(dir: string, config?: any): string {
  const configPath = path.join(dir, 'trainloop.config.yaml');
  const defaultConfig = {
    trainloop: {
      data_folder: './data',
      host_allowlist: [
        'api.openai.com',
        'api.anthropic.com',
        'generativelanguage.googleapis.com',
        'api.cohere.ai',
        'api.groq.com',
        'api.mistral.ai',
        'api.together.xyz',
        'api.endpoints.anyscale.com',
        'api.perplexity.ai',
        'api.deepinfra.com',
        'api.replicate.com',
        'api-inference.huggingface.co',
        'openai.azure.com'
      ],
      log_level: 'debug'
    }
  };

  const yaml = require('js-yaml');
  fs.writeFileSync(configPath, yaml.dump(config || defaultConfig));
  return configPath;
}

/**
 * Sample OpenAI request
 */
export const sampleOpenAIRequest = {
  model: 'gpt-4',
  messages: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Hello, how are you?' }
  ],
  temperature: 0.7,
  max_tokens: 100
};

/**
 * Sample OpenAI response
 */
export const sampleOpenAIResponse = {
  id: 'chatcmpl-123',
  object: 'chat.completion',
  created: 1677652288,
  model: 'gpt-4',
  choices: [{
    index: 0,
    message: {
      role: 'assistant',
      content: "I'm doing well, thank you! How can I help you today?"
    },
    finish_reason: 'stop'
  }],
  usage: {
    prompt_tokens: 20,
    completion_tokens: 15,
    total_tokens: 35
  }
};

/**
 * Sample Anthropic request
 */
export const sampleAnthropicRequest = {
  model: 'claude-3-opus-20240229',
  messages: [
    { role: 'user', content: 'Hello, Claude!' }
  ],
  max_tokens: 100
};

/**
 * Sample Anthropic response  
 */
export const sampleAnthropicResponse = {
  id: 'msg_123',
  type: 'message',
  role: 'assistant',
  content: [
    {
      type: 'text',
      text: "Hello! It's nice to meet you."
    }
  ],
  model: 'claude-3-opus-20240229',
  stop_reason: 'end_turn',
  stop_sequence: null,
  usage: {
    input_tokens: 10,
    output_tokens: 8
  }
};

/**
 * Create sample LLM call data
 */
export function createLLMCallData(overrides?: Partial<LLMCallData>): LLMCallData {
  return {
    isLLMRequest: true,
    tag: 'test-tag',
    url: 'https://api.openai.com/v1/chat/completions',
    requestBodyStr: JSON.stringify(sampleOpenAIRequest),
    responseBodyStr: JSON.stringify(sampleOpenAIResponse),
    startTimeMs: 1000000,
    endTimeMs: 1001234,
    durationMs: 1234,
    location: {
      file: 'test.ts',
      lineNumber: '42'
    },
    ...overrides
  };
}

/**
 * Create sample collected data
 */
export function createCollectedSample(overrides?: Partial<CollectedSample>): CollectedSample {
  return {
    durationMs: 1234,
    tag: 'test-tag',
    input: [
      { role: 'user', content: 'Hello!' }
    ],
    output: {
      content: 'Hi there!'
    },
    model: 'gpt-4',
    modelParams: { temperature: 0.7 },
    startTimeMs: 1000000,
    endTimeMs: 1001234,
    url: 'https://api.openai.com/v1/chat/completions',
    location: {
      file: 'test.ts',
      lineNumber: '42'
    },
    ...overrides
  };
}

/**
 * Create a corrupt registry file
 */
export function createCorruptRegistry(dir: string): string {
  const registryPath = path.join(dir, '_registry.json');
  fs.writeFileSync(registryPath, '{ invalid json');
  return registryPath;
}

/**
 * Create a valid registry file
 */
export function createValidRegistry(dir: string): string {
  const registryPath = path.join(dir, '_registry.json');
  const registryData = {
    schema: 1,
    files: {
      'test.ts': {
        '42': {
          lineNumber: '42',
          tag: 'existing-tag',
          firstSeen: '2024-01-01T00:00:00Z',
          lastSeen: '2024-01-01T00:00:00Z',
          count: 1
        }
      }
    }
  };
  fs.writeFileSync(registryPath, JSON.stringify(registryData, null, 2));
  return registryPath;
}

/**
 * Mock environment variables
 */
export function mockEnvVars(vars: Record<string, string>): () => void {
  const originalEnv = { ...process.env };

  // Clear existing TRAINLOOP_ vars
  Object.keys(process.env).forEach(key => {
    if (key.startsWith('TRAINLOOP_')) {
      delete process.env[key];
    }
  });

  // Set new vars
  Object.assign(process.env, vars);

  // Reset config state
  resetConfigState();

  // Return cleanup function
  return () => {
    Object.keys(process.env).forEach(key => {
      if (key.startsWith('TRAINLOOP_')) {
        delete process.env[key];
      }
    });
    Object.assign(process.env, originalEnv);
    resetConfigState(); // Reset config state on cleanup
  };
}

/**
 * Wait for a condition to be true
 */
export async function waitFor(
  condition: () => boolean | Promise<boolean>,
  timeout: number = 5000,
  interval: number = 100
): Promise<void> {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }

  throw new Error(`Timeout waiting for condition after ${timeout}ms`);
}

/**
 * Create test event files
 */
export function createEventFiles(dir: string, count: number = 1): string[] {
  const eventDir = path.join(dir, 'events');
  fs.mkdirSync(eventDir, { recursive: true });

  const files: string[] = [];
  const baseTime = Date.now();

  for (let i = 0; i < count; i++) {
    const timestamp = baseTime - (i * 10 * 60 * 1000); // 10 minutes apart
    const filePath = path.join(eventDir, `${timestamp}.jsonl`);
    const sample = createCollectedSample({ tag: `test-tag-${i}` });
    fs.writeFileSync(filePath, JSON.stringify(sample) + '\n');
    files.push(filePath);
  }

  return files;
}
