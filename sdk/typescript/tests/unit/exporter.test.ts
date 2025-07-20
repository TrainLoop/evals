/**
 * Unit tests for FileExporter class
 */
import { FileExporter } from '../../src/exporter';
import * as store from '../../src/store';
import { LLMCallData } from '../../src/types/shared';

// Unmock FileExporter for this test file to test the real implementation
jest.unmock('../../src/exporter');

// Mock dependencies
jest.mock('../../src/store', () => ({
  saveSamples: jest.fn(),
  updateRegistry: jest.fn(),
}));
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
      return parsed.choices?.[0]?.message?.content || 'response';
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

describe('FileExporter', () => {
  let exporter: FileExporter;
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    // Mock timers need to be set up before creating FileExporter
    jest.spyOn(global, 'setInterval');
    jest.spyOn(global, 'clearInterval');

    originalEnv = { ...process.env };
    process.env.TRAINLOOP_DATA_FOLDER = '/tmp/test';
  });

  afterEach(() => {
    if (exporter) {
      exporter.shutdown();
    }
    jest.useRealTimers();
    process.env = originalEnv;
  });

  describe('constructor', () => {
    it('should initialize with default values', () => {
      exporter = new FileExporter();
      expect(exporter).toBeDefined();
      expect(exporter['exportAtLength']).toBe(5);
      expect(exporter['exportAtInterval']).toBe(10000);
    });

    it('should accept custom export interval and length', () => {
      exporter = new FileExporter(5000, 10);
      expect(exporter['exportAtLength']).toBe(10);
      expect(exporter['exportAtInterval']).toBe(5000);
    });

    it('should start the export interval', () => {
      exporter = new FileExporter();
      expect(setInterval).toHaveBeenCalledWith(expect.any(Function), 10000);
    });

    it('should accept flushImmediately parameter', () => {
      exporter = new FileExporter(undefined, undefined, true);
      expect(exporter['flushImmediately']).toBe(true);
    });

    it('should not start interval when flushImmediately is true', () => {
      jest.clearAllMocks();
      exporter = new FileExporter(undefined, undefined, true);
      expect(setInterval).not.toHaveBeenCalled();
    });
  });

  describe('recordLLMCall', () => {
    beforeEach(() => {
      exporter = new FileExporter(10000, 2); // Lower threshold for testing
    });

    it('should record LLM calls to the buffer', () => {
      const callData: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        durationMs: 100,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Hello' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Hi there!' } }]
        }),
      };

      exporter.recordLLMCall(callData);
      expect(exporter['callBuffer'].length).toBe(1);
    });

    it('should ignore non-LLM requests', () => {
      const callData: LLMCallData = {
        url: 'https://example.com/api',
        isLLMRequest: false,
        status: 200,
        durationMs: 50,
      };

      exporter.recordLLMCall(callData);
      expect(exporter['callBuffer'].length).toBe(0);
    });

    it('should trigger export when buffer reaches exportAtLength', () => {
      const exportSpy = jest.spyOn(exporter as any, 'export');

      const callData1: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test 1' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response 1' } }]
        }),
      };

      const callData2: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test 2' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response 2' } }]
        }),
      };

      exporter.recordLLMCall(callData1);
      expect(exportSpy).not.toHaveBeenCalled();

      exporter.recordLLMCall(callData2);
      expect(exportSpy).toHaveBeenCalledTimes(1);
    });

    it('should export immediately when flushImmediately is true', () => {
      exporter = new FileExporter(undefined, undefined, true);
      const exportSpy = jest.spyOn(exporter as any, 'export');

      const callData: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test immediate' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response immediate' } }]
        }),
      };

      exporter.recordLLMCall(callData);
      expect(exportSpy).toHaveBeenCalledTimes(1);
    });
  });

  describe('export behavior', () => {
    beforeEach(() => {
      exporter = new FileExporter();
    });

    it('should export calls with proper tag grouping', () => {
      const call1: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        tag: 'tag1',
        status: 200,
        location: { file: 'test.ts', lineNumber: '10' },
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Hello from tag1' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response for tag1' } }]
        }),
      };

      const call2: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        tag: 'tag2',
        status: 200,
        location: { file: 'test.ts', lineNumber: '20' },
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Hello from tag2' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response for tag2' } }]
        }),
      };

      exporter.recordLLMCall(call1);
      exporter.recordLLMCall(call2);

      // @ts-ignore
      console.log("callBuffer", exporter.callBuffer)

      // Manually trigger export
      // @ts-ignore
      exporter.export();

      // Should have been called once with all samples (batched)
      expect(store.saveSamples).toHaveBeenCalledTimes(1);
      expect(store.updateRegistry).toHaveBeenCalledTimes(2);
    });

    it('should handle missing TRAINLOOP_DATA_FOLDER', () => {
      delete process.env.TRAINLOOP_DATA_FOLDER;

      const call: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response' } }]
        }),
      };

      exporter.recordLLMCall(call);
      (exporter as any).export();

      expect(store.saveSamples).not.toHaveBeenCalled();
    });

    it('should prevent concurrent exports', async () => {
      // Mock export to take some time
      let exportResolve: () => void;
      const exportPromise = new Promise<void>(resolve => {
        exportResolve = resolve;
      });

      jest.spyOn(store, 'saveSamples').mockImplementation(async () => {
        await exportPromise;
      });

      const call: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response' } }]
        }),
      };

      exporter.recordLLMCall(call);

      // Start first export
      // @ts-ignore private method
      const export1 = exporter.export();

      expect(export1).toBe(true); // Should succeed

      // Set the exportingFlag to true to simulate a concurrent export
      exporter['exportingFlag'] = true;

      // Try to start second export while first is running
      // @ts-ignore private method
      const export2 = exporter.export();

      expect(export2).toBe(false); // Should fail

      // Complete the first export
      exportResolve!();

      expect(store.saveSamples).toHaveBeenCalledTimes(1);
    });
  });

  describe('timer behavior', () => {
    it('should export on interval', () => {
      exporter = new FileExporter(5000, 10);
      const exportSpy = jest.spyOn(exporter as any, 'export');

      const call: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response' } }]
        }),
      };

      exporter.recordLLMCall(call);

      // Advance time to trigger interval
      jest.advanceTimersByTime(5000);

      expect(exportSpy).toHaveBeenCalledTimes(1);
    });

    it('should not export on interval when flushImmediately is true', () => {
      exporter = new FileExporter(5000, 10, true);
      const exportSpy = jest.spyOn(exporter as any, 'export');

      const call: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Test' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Response' } }]
        }),
      };

      exporter.recordLLMCall(call);
      expect(exportSpy).toHaveBeenCalledTimes(1); // Should export immediately

      exportSpy.mockClear();

      // Advance time - should NOT trigger another export
      jest.advanceTimersByTime(5000);
      expect(exportSpy).not.toHaveBeenCalled();
    });

    it('should clear interval on shutdown', () => {
      exporter = new FileExporter();

      exporter.shutdown();

      expect(clearInterval).toHaveBeenCalled();

      // Advance time - should not trigger export after shutdown
      jest.advanceTimersByTime(10000);
      expect(store.saveSamples).not.toHaveBeenCalled();
    });
  });

  describe('shutdown', () => {
    beforeEach(() => {
      exporter = new FileExporter();
    });

    it('should export remaining calls on shutdown', () => {
      const call: LLMCallData = {
        url: 'https://api.openai.com/v1/chat/completions',
        isLLMRequest: true,
        status: 200,
        tag: 'shutdown-test',
        requestBodyStr: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: 'Shutdown test' }]
        }),
        responseBodyStr: JSON.stringify({
          choices: [{ message: { content: 'Shutdown response' } }]
        }),
      };

      exporter.recordLLMCall(call);
      exporter.shutdown();

      expect(store.saveSamples).toHaveBeenCalledTimes(1);
      expect(store.saveSamples).toHaveBeenCalledWith(
        '/tmp/test',
        expect.arrayContaining([
          expect.objectContaining({
            tag: 'shutdown-test',
          })
        ])
      );
    });

    it('should handle empty buffer on shutdown', () => {
      exporter.shutdown();
      expect(store.saveSamples).not.toHaveBeenCalled();
    });

    it('should clear the export interval', () => {
      exporter = new FileExporter();

      exporter.shutdown();

      expect(clearInterval).toHaveBeenCalled();
    });
  });

  describe('batch processing', () => {
    beforeEach(() => {
      exporter = new FileExporter();
    });

    it('should process calls in batches by tag', () => {
      const calls = [
        {
          url: 'https://api.openai.com/v1/chat',
          isLLMRequest: true,
          tag: 'tag1',
          requestBodyStr: JSON.stringify({
            model: 'gpt-4',
            messages: [{ role: 'user', content: 'Test 1' }]
          }),
          responseBodyStr: JSON.stringify({
            choices: [{ message: { content: 'Response 1' } }]
          }),
        },
        {
          url: 'https://api.openai.com/v1/chat',
          isLLMRequest: true,
          tag: 'tag2',
          requestBodyStr: JSON.stringify({
            model: 'gpt-4',
            messages: [{ role: 'user', content: 'Test 2' }]
          }),
          responseBodyStr: JSON.stringify({
            choices: [{ message: { content: 'Response 2' } }]
          }),
        },
        {
          url: 'https://api.openai.com/v1/chat',
          isLLMRequest: true,
          tag: 'tag1',
          requestBodyStr: JSON.stringify({
            model: 'gpt-4',
            messages: [{ role: 'user', content: 'Test 3' }]
          }),
          responseBodyStr: JSON.stringify({
            choices: [{ message: { content: 'Response 3' } }]
          }),
        },
        {
          url: 'https://api.openai.com/v1/chat',
          isLLMRequest: true,
          tag: 'tag3',
          requestBodyStr: JSON.stringify({
            model: 'gpt-4',
            messages: [{ role: 'user', content: 'Test 4' }]
          }),
          responseBodyStr: JSON.stringify({
            choices: [{ message: { content: 'Response 4' } }]
          }),
        },
      ] as LLMCallData[];

      calls.forEach(call => exporter.recordLLMCall(call));
      (exporter as any).export();

      // Should have been called once with all samples (batched)
      expect(store.saveSamples).toHaveBeenCalledTimes(1);
      expect(store.updateRegistry).toHaveBeenCalledTimes(calls.length);
    });

    it('should handle calls without tags', () => {
      // Record calls without tags
      for (let i = 0; i < 3; i++) {
        const call: LLMCallData = {
          url: 'https://api.openai.com/v1/chat/completions',
          isLLMRequest: true,
          status: 200,
          requestBodyStr: JSON.stringify({
            model: 'gpt-4',
            messages: [{ role: 'user', content: `Test ${i}` }]
          }),
          responseBodyStr: JSON.stringify({
            choices: [{ message: { content: `Response ${i}` } }]
          }),
        };
        exporter.recordLLMCall(call);
      }

      (exporter as any).export();

      expect(store.saveSamples).toHaveBeenCalledTimes(1);

      // Should be called with "<empty>" tag
      const saveSamplesCalls = (store.saveSamples as jest.Mock).mock.calls;
      expect(saveSamplesCalls[0][1][0].tag).toBe('');
    });
  });
});
