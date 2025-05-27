/**
 * Unit tests for Fetch API instrumentation
 */
import { patchFetch } from '../../src/instrumentation/fetch';
import { FileExporter } from '../../src/exporter';
import * as utils from '../../src/instrumentation/utils';
import { EXPECTED_LLM_PROVIDER_URLS } from '../../src/index';

// Mock dependencies
jest.mock('../../src/exporter');
jest.mock('../../src/logger', () => ({
  createLogger: () => ({
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  }),
}));

describe('fetch instrumentation', () => {
  let mockExporter: jest.Mocked<FileExporter>;
  let originalFetch: typeof globalThis.fetch;
  let mockFetch: jest.MockedFunction<typeof fetch>;
  let mockResponse: Partial<Response>;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Save original fetch
    originalFetch = globalThis.fetch;
    
    // Create mock exporter
    mockExporter = {
      recordLLMCall: jest.fn(),
      shutdown: jest.fn(),
    } as any;

    // Create mock response
    mockResponse = {
      status: 200,
      statusText: 'OK',
      headers: new Headers({ 'content-type': 'application/json' }),
      ok: true,
      clone: jest.fn().mockReturnThis(),
      text: jest.fn().mockResolvedValue('{"choices":[{"message":{"content":"Hello"}}]}'),
      json: jest.fn().mockResolvedValue({ choices: [{ message: { content: 'Hello' } }] }),
    };

    // Create mock fetch
    mockFetch = jest.fn().mockResolvedValue(mockResponse as Response);
    globalThis.fetch = mockFetch;
  });

  afterEach(() => {
    // Restore original fetch
    globalThis.fetch = originalFetch;
  });

  describe('patchFetch', () => {
    it('should patch global fetch', () => {
      patchFetch(mockExporter);
      
      expect(globalThis.fetch).not.toBe(mockFetch);
      expect(typeof globalThis.fetch).toBe('function');
    });

    it('should intercept requests to LLM providers', async () => {
      patchFetch(mockExporter);
      
      jest.spyOn(utils, 'cloneResponseForLogging').mockResolvedValue('{"choices":[{"message":{"content":"Hello"}}]}');
      
      await globalThis.fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-trainloop-tag': 'test-tag'
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: 'Hi' }],
          model: 'gpt-4'
        })
      });

      // Wait for async logging
      await new Promise(resolve => setTimeout(resolve, 10));

      expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
        expect.objectContaining({
          isLLMRequest: true,
          url: 'https://api.openai.com/v1/chat/completions',
          tag: 'test-tag',
          status: 200,
          requestBodyStr: expect.stringContaining('"model":"gpt-4"'),
          responseBodyStr: '{"choices":[{"message":{"content":"Hello"}}]}'
        })
      );
    });

    it('should skip non-LLM provider requests', async () => {
      patchFetch(mockExporter);
      
      await globalThis.fetch('https://example.com/api/data');

      // Wait for any async operations
      await new Promise(resolve => setTimeout(resolve, 10));

      // Non-LLM requests should not call recordLLMCall at all
      expect(mockExporter.recordLLMCall).not.toHaveBeenCalled();
    });

    it('should handle URL object', async () => {
      patchFetch(mockExporter);
      
      const url = new URL('https://api.anthropic.com/v1/messages');
      await globalThis.fetch(url);

      expect(mockFetch).toHaveBeenCalledWith(url, {});
    });

    it('should handle Request object', async () => {
      patchFetch(mockExporter);
      
      const request = new Request('https://api.openai.com/v1/models');
      await globalThis.fetch(request);

      expect(mockFetch).toHaveBeenCalledWith(request, {});
    });

    it('should preserve response', async () => {
      patchFetch(mockExporter);
      
      const response = await globalThis.fetch('https://api.openai.com/v1/models');
      
      expect(response).toBe(mockResponse);
      expect(response.status).toBe(200);
    });

    it('should remove x-trainloop-tag header', async () => {
      patchFetch(mockExporter);
      
      const headers = new Headers({
        'Content-Type': 'application/json',
        'x-trainloop-tag': 'my-tag'
      });
      
      await globalThis.fetch('https://api.openai.com/v1/chat/completions', {
        headers
      });

      // Header should be removed
      expect(headers.has('x-trainloop-tag')).toBe(false);
    });

    it('should handle various header formats', async () => {
      patchFetch(mockExporter);
      
      // Headers object
      await globalThis.fetch('https://api.openai.com/v1/chat', {
        headers: new Headers({ 'x-trainloop-tag': 'tag1' })
      });
      
      // Plain object
      await globalThis.fetch('https://api.openai.com/v1/chat', {
        headers: { 'x-trainloop-tag': 'tag2' }
      });
      
      // Array of tuples
      await globalThis.fetch('https://api.openai.com/v1/chat', {
        headers: [['x-trainloop-tag', 'tag3']]
      });
      
      expect(mockFetch).toHaveBeenCalledTimes(3);
    });

    it('should handle streaming request body', async () => {
      patchFetch(mockExporter);
      
      const stream = new ReadableStream();
      await globalThis.fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        body: stream
      });

      await new Promise(resolve => setTimeout(resolve, 10));

      expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
        expect.objectContaining({
          requestBodyStr: '[stream]'
        })
      );
    });

    it('should handle missing init parameter', async () => {
      patchFetch(mockExporter);
      
      await globalThis.fetch('https://api.openai.com/v1/models');
      
      expect(mockFetch).toHaveBeenCalledWith('https://api.openai.com/v1/models', {});
    });

    it('should track timing', async () => {
      patchFetch(mockExporter);
      
      await globalThis.fetch('https://api.openai.com/v1/models');

      await new Promise(resolve => setTimeout(resolve, 10));

      expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
        expect.objectContaining({
          durationMs: expect.any(Number)
        })
      );
    });

    it('should capture caller location', async () => {
      patchFetch(mockExporter);
      
      const mockLocation = { file: '/test/file.ts', lineNumber: '42' };
      jest.spyOn(utils, 'getCallerSite').mockReturnValue(mockLocation);
      jest.spyOn(utils, 'getCallerStack').mockReturnValue('mock stack trace');

      await globalThis.fetch('https://api.openai.com/v1/models');

      expect(utils.getCallerSite).toHaveBeenCalled();
      expect(utils.getCallerStack).toHaveBeenCalled();
    });

    it('should handle errors in fetch', async () => {
      patchFetch(mockExporter);
      
      const fetchError = new Error('Network error');
      mockFetch.mockRejectedValue(fetchError);

      await expect(
        globalThis.fetch('https://api.openai.com/v1/models')
      ).rejects.toThrow('Network error');

      // When fetch throws an error, recordLLMCall should not be called
      await new Promise(resolve => setTimeout(resolve, 10));
      expect(mockExporter.recordLLMCall).not.toHaveBeenCalled();
    });

    it('should handle errors in response cloning', async () => {
      patchFetch(mockExporter);
      
      jest.spyOn(utils, 'cloneResponseForLogging').mockRejectedValue(new Error('Clone failed'));

      await globalThis.fetch('https://api.openai.com/v1/models');

      await new Promise(resolve => setTimeout(resolve, 10));

      // When response cloning fails, the error is swallowed and recordLLMCall is not called
      expect(mockExporter.recordLLMCall).not.toHaveBeenCalled();
    });

    it('should handle default method', async () => {
      patchFetch(mockExporter);
      
      await globalThis.fetch('https://api.openai.com/v1/models');

      await new Promise(resolve => setTimeout(resolve, 10));

      // Just verify that the call was made for an LLM provider
      expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
        expect.objectContaining({
          isLLMRequest: true,
          url: 'https://api.openai.com/v1/models'
        })
      );
    });

    it('should handle all LLM provider URLs', async () => {
      patchFetch(mockExporter);
      
      for (const host of EXPECTED_LLM_PROVIDER_URLS) {
        await globalThis.fetch(`https://${host}/test`);
      }

      await new Promise(resolve => setTimeout(resolve, 50));

      // Should have recorded calls for each provider
      const llmCalls = mockExporter.recordLLMCall.mock.calls.filter(
        call => call[0].isLLMRequest
      );
      
      expect(llmCalls).toHaveLength(EXPECTED_LLM_PROVIDER_URLS.length);
    });

    it('should handle non-string request body', async () => {
      patchFetch(mockExporter);
      
      const formData = new FormData();
      formData.append('key', 'value');

      await globalThis.fetch('https://api.openai.com/v1/files', {
        method: 'POST',
        body: formData
      });

      await new Promise(resolve => setTimeout(resolve, 10));

      expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
        expect.objectContaining({
          requestBodyStr: '[stream]'
        })
      );
    });

    it('should handle undefined tag', async () => {
      patchFetch(mockExporter);
      
      await globalThis.fetch('https://api.openai.com/v1/models', {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      await new Promise(resolve => setTimeout(resolve, 10));

      expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
        expect.objectContaining({
          tag: undefined
        })
      );
    });

    it('should not patch if fetch is not available', () => {
      const tempFetch = globalThis.fetch;
      (globalThis as any).fetch = undefined;

      expect(() => patchFetch(mockExporter)).not.toThrow();

      globalThis.fetch = tempFetch;
    });

    it('should handle response without clone method', async () => {
      patchFetch(mockExporter);
      
      const responseWithoutClone = {
        ...mockResponse,
        clone: undefined
      };
      
      mockFetch.mockResolvedValue(responseWithoutClone as unknown as Response);
      jest.spyOn(utils, 'cloneResponseForLogging').mockImplementation(async (res) => {
        if (!res.clone) {
          throw new Error('Clone not supported');
        }
        return 'cloned';
      });

      await globalThis.fetch('https://api.openai.com/v1/models');

      await new Promise(resolve => setTimeout(resolve, 10));

      // When response cloning fails due to missing clone method, recordLLMCall is not called
      expect(mockExporter.recordLLMCall).not.toHaveBeenCalled();
    });
  });
});
