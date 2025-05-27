/**
 * Unit tests for HTTP/HTTPS instrumentation
 */
import http from 'http';
import https from 'https';
import { PassThrough } from 'stream';
import { patchHttp } from '../../src/instrumentation/http';
import { FileExporter } from '../../src/exporter';
import * as utils from '../../src/instrumentation/utils';

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

// Store original methods
const originalHttpRequest = http.request;
const originalHttpsRequest = https.request;

describe('http instrumentation', () => {
  let mockExporter: jest.Mocked<FileExporter>;
  let mockRequest: jest.MockedFunction<typeof http.request>;
  let mockClientRequest: any;
  let mockIncomingMessage: any;

  beforeEach(() => {
    jest.clearAllMocks();

    // Create mock exporter
    mockExporter = {
      recordLLMCall: jest.fn(),
      shutdown: jest.fn(),
    } as any;

    // Create mock ClientRequest
    mockClientRequest = {
      on: jest.fn(),
      write: jest.fn(),
      end: jest.fn(),
    };

    // Create mock IncomingMessage
    mockIncomingMessage = {
      statusCode: 200,
      headers: { 'content-type': 'application/json' },
      pipe: jest.fn().mockImplementation(() => new PassThrough()),
    };

    // Mock the request method
    mockRequest = jest.fn().mockImplementation((opts, callback) => {
      // Simulate async response
      if (callback) {
        setImmediate(() => callback(mockIncomingMessage));
      }
      return mockClientRequest;
    });

    // Replace http/https request
    http.request = mockRequest as any;
    https.request = mockRequest as any;
  });


  describe('patchHttp', () => {
    it('should patch http module', () => {
      patchHttp(http as any, mockExporter);

      expect(http.request).not.toBe(mockRequest);
      expect(typeof http.request).toBe('function');
    });

    it('should patch https module', () => {
      patchHttp(https as any, mockExporter);

      expect(https.request).not.toBe(mockRequest);
      expect(typeof https.request).toBe('function');
    });

    it('should intercept requests to LLM providers', (done) => {
      patchHttp(http as any, mockExporter);

      const opts = {
        host: 'api.openai.com',
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'x-trainloop-tag': 'test-tag'
        }
      };

      // Mock drain to return response body
      jest.spyOn(utils, 'drain').mockResolvedValue('{"choices":[{"message":{"content":"Hello"}}]}');

      const req = http.request(opts, (res) => {
        // Wait for async processing
        setTimeout(() => {
          try {
            expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
              expect.objectContaining({
                isLLMRequest: true,
                url: 'http://api.openai.com/v1/chat/completions',
                tag: 'test-tag',
                status: 200,
              })
            );
          } catch (error) {
            done(error);
          }
          done();
        }, 10);
      });

      req.write('{"messages":[{"role":"user","content":"Hi"}],"model":"gpt-4"}');
      req.end();
    });

    it('should skip non-LLM provider requests', (done) => {
      patchHttp(http as any, mockExporter);

      const opts = {
        host: 'example.com',
        path: '/api/data',
        method: 'GET'
      };

      const req = http.request(opts, () => {
        setTimeout(() => {
          try {
            expect(mockExporter.recordLLMCall).not.toHaveBeenCalled();
          } catch (error) {
            done(error);
          }
          done();
        }, 10);
      });

      req.end();
    });

    it('should handle string URL format', () => {
      patchHttp(http as any, mockExporter);

      http.request('https://api.openai.com/v1/models');

      expect(mockRequest).toHaveBeenCalledWith(
        'https://api.openai.com/v1/models',
        expect.any(Function)
      );
    });

    it('should preserve original callback', (done) => {
      patchHttp(http as any, mockExporter);

      const userCallback = jest.fn((res: any) => {
        expect(res).toBe(mockIncomingMessage);
        done();
      });

      http.request({ host: 'example.com' }, userCallback);
    });

    it('should handle requests without callback', () => {
      patchHttp(http as any, mockExporter);

      const req = http.request({ host: 'example.com' });

      expect(req).toBeDefined();
      expect(mockRequest).toHaveBeenCalled();
    });

    it('should remove x-trainloop-tag header', () => {
      patchHttp(http as any, mockExporter);

      const headers = {
        'content-type': 'application/json',
        'x-trainloop-tag': 'my-tag'
      };

      const opts = { host: 'api.openai.com', headers };

      http.request(opts);

      // Header should be removed from the actual request
      expect(headers['x-trainloop-tag']).toBeUndefined();
    });

    it('should capture request body', () => {
      patchHttp(http as any, mockExporter);

      const req = http.request({ host: 'api.openai.com' });

      const chunks = ['{"test":', '"data"}'];
      chunks.forEach(chunk => req.write(chunk));
      req.end();

      const reqBody = utils.reqBodies.get(mockClientRequest);
      expect(reqBody?.toString()).toBe('{"test":"data"}');
    });

    it('should handle request errors', () => {
      patchHttp(http as any, mockExporter);

      // Make the request emit an error
      mockClientRequest.on.mockImplementation((event: string, handler: (...args: any[]) => void) => {
        if (event === 'error') {
          setImmediate(() => handler(new Error('Connection failed')));
        }
      });

      const req = http.request({ host: 'api.openai.com' });

      expect(() => req.end()).not.toThrow();
    });

    it('should track timing', (done) => {
      patchHttp(http as any, mockExporter);

      // Mock drain to return response body after a delay to ensure measurable time
      jest.spyOn(utils, 'drain').mockImplementation(() => {
        return new Promise((resolve) => {
          setTimeout(() => resolve('{}'), 5); // 5ms delay to ensure durationMs > 0
        });
      });

      const req = http.request({ host: 'api.openai.com' }, () => {
        setTimeout(() => {
          try {
            expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
              expect.objectContaining({
                durationMs: expect.any(Number)
              })
            );
            expect(mockExporter.recordLLMCall.mock.calls[0][0].durationMs).toBeGreaterThan(0);
            done();
          } catch (error) {
            done(error);
          }
        }, 10);
      });
      
      req.end(); // Actually send the request to ensure timing measurement works
    });

    it('should handle streaming responses', (done) => {
      patchHttp(http as any, mockExporter);

      // Mock streaming response
      const streamContent = `data: {"delta":{"content":"Hello"}}\ndata: {"delta":{"content":" World"}}\ndata: [DONE]`;
      jest.spyOn(utils, 'drain').mockResolvedValue(streamContent);
      jest.spyOn(utils, 'formatStreamedContent').mockReturnValue('Hello World [Stream Complete]');

      const req = http.request({ host: 'api.openai.com' }, () => {
        setTimeout(() => {
          try {
            expect(utils.formatStreamedContent).toHaveBeenCalledWith(streamContent);
            expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
              expect.objectContaining({
                responseBodyStr: 'Hello World [Stream Complete]' // Use correct property name
              })
            );
            done();
          } catch (error) {
            done(error);
          }
        }, 10);
      });

      req.end();
    });

    it('should capture caller location', () => {
      patchHttp(http as any, mockExporter);

      const mockLocation = { file: '/test/file.ts', lineNumber: '42' };
      jest.spyOn(utils, 'getCallerSite').mockReturnValue(mockLocation);
      jest.spyOn(utils, 'getCallerStack').mockReturnValue('mock stack trace');

      http.request({ host: 'api.openai.com' });

      expect(utils.getCallerSite).toHaveBeenCalled();
      expect(utils.getCallerStack).toHaveBeenCalled();
    });

    it('should use default tag when not provided', (done) => {
      patchHttp(http as any, mockExporter);

      jest.spyOn(utils, 'drain').mockResolvedValue('{}');

      http.request({ host: 'api.openai.com' }, () => {
        setTimeout(() => {
          try {
            expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
              expect.objectContaining({
                tag: undefined
              })
            );
            done();
          } catch (error) {
            done(error);
          }
        }, 10);
      });
    });

    it('should handle various header formats', () => {
      patchHttp(http as any, mockExporter);

      // Test with array
      const headers = ['x-trainloop-tag', 'tag2'];
      http.request({ host: 'api.openai.com', headers });

      // Test with plain object
      const headers2 = { 'x-trainloop-tag': 'tag3' };
      http.request({ host: 'api.openai.com', headers: headers2 });

      expect(mockRequest).toHaveBeenCalledTimes(2);
    });

    it('should handle body parsing errors', (done) => {
      patchHttp(http as any, mockExporter);

      jest.spyOn(utils, 'drain').mockResolvedValue('not json');

      const req = http.request({ host: 'api.openai.com' }, (res) => {
        // The response callback should be called by our mock
        setTimeout(() => {
          try {
            expect(mockExporter.recordLLMCall).toHaveBeenCalledWith(
              expect.objectContaining({
                requestBodyStr: '',
                responseBodyStr: 'not json'
              })
            );
          } catch (error) {
            done(error);
          }
          done();
        }, 10);
      });

      // Trigger the request end to simulate completion
      req.end();
    });
  });
});
