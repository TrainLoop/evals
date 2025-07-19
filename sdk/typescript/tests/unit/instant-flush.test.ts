/**
 * Unit tests for instant flush functionality
 */
import { FileExporter } from '../../src/exporter';
import * as store from '../../src/store';
import { LLMCallData } from '../../src/types/shared';

// Unmock FileExporter for this test file
jest.unmock('../../src/exporter');

// Mock dependencies
jest.mock('../../src/store');
jest.mock('../../src/instrumentation/utils', () => ({
  getCallerSite: jest.fn(() => ({ file: 'test.ts', lineNumber: '10' })),
  getCallerStack: jest.fn(() => []),
  parseRequestBody: jest.fn((body) => {
    try {
      const parsed = JSON.parse(body);
      return {
        messages: parsed.messages || [],
        model: parsed.model,
        modelParams: {},
      };
    } catch {
      return null;
    }
  }),
  parseResponseBody: jest.fn((body) => {
    try {
      const parsed = JSON.parse(body);
      // Handle both pre-formatted and raw responses
      if (parsed.content) {
        return { content: parsed.content };
      }
      // Extract from OpenAI format
      const content = parsed.choices?.[0]?.message?.content;
      return content ? { content } : null;
    } catch {
      return null;
    }
  }),
}));
jest.mock('../../src/logger', () => ({
  createLogger: () => ({
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  }),
}));

describe('Instant Flush Feature', () => {
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    originalEnv = { ...process.env };
    process.env.TRAINLOOP_DATA_FOLDER = '/tmp/test';
  });

  afterEach(() => {
    jest.useRealTimers();
    process.env = originalEnv;
  });

  describe('when instant flush is enabled', () => {
    it('should export immediately after recording a call', () => {
      const exporter = new FileExporter(undefined, undefined, true);
      const saveSamplesSpy = jest.spyOn(store, 'saveSamples');

      const callData: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test instant flush' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Instant response' } }]
        }),
      };

      exporter.recordLLMCall(callData);

      // Should export immediately without waiting
      expect(saveSamplesSpy).toHaveBeenCalledTimes(1);
      expect(saveSamplesSpy).toHaveBeenCalledWith(
        '/tmp/test',
        expect.arrayContaining([
          expect.objectContaining({
            output: { content: 'Instant response' },
          })
        ])
      );

      exporter.shutdown();
    });

    it('should not set up interval timer', () => {
      const setIntervalSpy = jest.spyOn(global, 'setInterval');
      
      const exporter = new FileExporter(5000, 10, true);
      
      expect(setIntervalSpy).not.toHaveBeenCalled();
      
      exporter.shutdown();
    });

    it('should handle multiple rapid calls', () => {
      const exporter = new FileExporter(undefined, undefined, true);
      const saveSamplesSpy = jest.spyOn(store, 'saveSamples');

      // Record 3 calls rapidly
      for (let i = 0; i < 3; i++) {
        exporter.recordLLMCall({
          url: 'https://api.openai.com/v1/chat/completions',
          isLLMRequest: true,
          requestBodyStr: JSON.stringify({
            model: 'gpt-4',
            messages: [{ role: 'user', content: `Test ${i}` }]
          }),
          responseBodyStr: JSON.stringify({
            choices: [{ message: { content: `Response ${i}` } }]
          }),
        });
      }

      // Each call should trigger an immediate export
      expect(saveSamplesSpy).toHaveBeenCalledTimes(3);

      exporter.shutdown();
    });
  });

  describe('when instant flush is disabled', () => {
    it('should batch calls and export on interval', () => {
      const exporter = new FileExporter(5000, 10, false);
      const saveSamplesSpy = jest.spyOn(store, 'saveSamples');

      // Record a call
      exporter.recordLLMCall({
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test batched' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Batched response' } }]
        }),
      });

      // Should not export immediately
      expect(saveSamplesSpy).not.toHaveBeenCalled();

      // Advance timers to trigger interval export
      jest.advanceTimersByTime(5000);

      // Now it should have exported
      expect(saveSamplesSpy).toHaveBeenCalledTimes(1);

      exporter.shutdown();
    });
  });

  describe('manual flush', () => {
    it('should work with instant flush enabled', () => {
      const exporter = new FileExporter(undefined, undefined, true);
      const saveSamplesSpy = jest.spyOn(store, 'saveSamples');

      // Record but don't wait for auto-export
      exporter.recordLLMCall({
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test manual flush' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Manual flush response' } }]
        }),
      });

      // Clear the spy to test manual flush
      saveSamplesSpy.mockClear();

      // Manual flush should work even with instant flush
      exporter.flush();

      // Should not double-export since buffer was already cleared
      expect(saveSamplesSpy).not.toHaveBeenCalled();

      exporter.shutdown();
    });

    it('should work with instant flush disabled', () => {
      const exporter = new FileExporter(10000, 10, false);
      const saveSamplesSpy = jest.spyOn(store, 'saveSamples');

      exporter.recordLLMCall({
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test manual' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Manual response' } }]
        }),
      });

      // Should not auto-export
      expect(saveSamplesSpy).not.toHaveBeenCalled();

      // Manual flush
      exporter.flush();

      // Should export
      expect(saveSamplesSpy).toHaveBeenCalledTimes(1);

      exporter.shutdown();
    });
  });
});