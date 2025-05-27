/**
 * Unit tests for logger.ts - Logging utilities with log levels
 */
import { createLogger } from '../../src/logger';

describe('logger', () => {
  let consoleErrorSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;
  let consoleInfoSpy: jest.SpyInstance;
  let consoleDebugSpy: jest.SpyInstance;
  let originalEnv: string | undefined;

  beforeEach(() => {
    // Save original env
    originalEnv = process.env.TRAINLOOP_LOG_LEVEL;
    
    // Mock console methods
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    consoleInfoSpy = jest.spyOn(console, 'info').mockImplementation();
    consoleDebugSpy = jest.spyOn(console, 'debug').mockImplementation();
  });

  afterEach(() => {
    // Restore original env
    if (originalEnv) {
      process.env.TRAINLOOP_LOG_LEVEL = originalEnv;
    } else {
      delete process.env.TRAINLOOP_LOG_LEVEL;
    }
    
    // Restore console methods
    consoleErrorSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleInfoSpy.mockRestore();
    consoleDebugSpy.mockRestore();
  });

  describe('log levels', () => {
    it('should default to warn level when TRAINLOOP_LOG_LEVEL is not set', () => {
      delete process.env.TRAINLOOP_LOG_LEVEL;
      const logger = createLogger('test-scope');

      logger.error('error message');
      logger.warn('warn message');
      logger.info('info message');
      logger.debug('debug message');

      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
      expect(consoleWarnSpy).toHaveBeenCalledTimes(1);
      expect(consoleInfoSpy).not.toHaveBeenCalled();
      expect(consoleDebugSpy).not.toHaveBeenCalled();
    });

    it('should respect error log level', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'error';
      const logger = createLogger('test-scope');

      logger.error('error message');
      logger.warn('warn message');
      logger.info('info message');
      logger.debug('debug message');

      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
      expect(consoleWarnSpy).not.toHaveBeenCalled();
      expect(consoleInfoSpy).not.toHaveBeenCalled();
      expect(consoleDebugSpy).not.toHaveBeenCalled();
    });

    it('should respect warn log level', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'warn';
      const logger = createLogger('test-scope');

      logger.error('error message');
      logger.warn('warn message');
      logger.info('info message');
      logger.debug('debug message');

      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
      expect(consoleWarnSpy).toHaveBeenCalledTimes(1);
      expect(consoleInfoSpy).not.toHaveBeenCalled();
      expect(consoleDebugSpy).not.toHaveBeenCalled();
    });

    it('should respect info log level', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'info';
      const logger = createLogger('test-scope');

      logger.error('error message');
      logger.warn('warn message');
      logger.info('info message');
      logger.debug('debug message');

      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
      expect(consoleWarnSpy).toHaveBeenCalledTimes(1);
      expect(consoleInfoSpy).toHaveBeenCalledTimes(1);
      expect(consoleDebugSpy).not.toHaveBeenCalled();
    });

    it('should respect debug log level', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'debug';
      const logger = createLogger('test-scope');

      logger.error('error message');
      logger.warn('warn message');
      logger.info('info message');
      logger.debug('debug message');

      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
      expect(consoleWarnSpy).toHaveBeenCalledTimes(1);
      expect(consoleInfoSpy).toHaveBeenCalledTimes(1);
      expect(consoleDebugSpy).toHaveBeenCalledTimes(1);
    });

    it('should handle case-insensitive log levels', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'DEBUG';
      const logger = createLogger('test-scope');

      logger.debug('debug message');

      expect(consoleDebugSpy).toHaveBeenCalledTimes(1);
    });

    it('should default to info for invalid log level', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'invalid';
      const logger = createLogger('test-scope');

      logger.error('error message');
      logger.warn('warn message');
      logger.info('info message');
      logger.debug('debug message');

      // Falls back to info level
      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
      expect(consoleWarnSpy).toHaveBeenCalledTimes(1);
      expect(consoleInfoSpy).toHaveBeenCalledTimes(1);
      expect(consoleDebugSpy).not.toHaveBeenCalled();
    });
  });

  describe('log format', () => {
    beforeEach(() => {
      process.env.TRAINLOOP_LOG_LEVEL = 'debug';
    });

    it('should include log level in uppercase', () => {
      const logger = createLogger('test-scope');

      logger.error('test message');
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining('[ERROR]')
      );
    });

    it('should include timestamp in ISO format', () => {
      const logger = createLogger('test-scope');

      logger.warn('test message');
      
      const call = consoleWarnSpy.mock.calls[0][0];
      const timestampMatch = call.match(/\[([\d-:.TZ]+)\]/);
      
      expect(timestampMatch).toBeTruthy();
      expect(() => new Date(timestampMatch[1])).not.toThrow();
    });

    it('should include scope', () => {
      const logger = createLogger('my-test-scope');

      logger.info('test message');
      
      expect(consoleInfoSpy).toHaveBeenCalledWith(
        expect.stringContaining('[my-test-scope]')
      );
    });

    it('should include the message', () => {
      const logger = createLogger('test-scope');

      logger.debug('this is my test message');
      
      expect(consoleDebugSpy).toHaveBeenCalledWith(
        expect.stringContaining('this is my test message')
      );
    });

    it('should format messages consistently', () => {
      const logger = createLogger('test-scope');

      logger.error('error msg');
      
      const call = consoleErrorSpy.mock.calls[0][0];
      const pattern = /^\[ERROR\] \[[\d-:.TZ]+\] \[test-scope\] error msg$/;
      
      expect(call).toMatch(pattern);
    });
  });

  describe('logger methods', () => {
    it('should provide all log methods', () => {
      const logger = createLogger('test-scope');

      expect(logger.error).toBeDefined();
      expect(logger.warn).toBeDefined();
      expect(logger.info).toBeDefined();
      expect(logger.debug).toBeDefined();

      expect(typeof logger.error).toBe('function');
      expect(typeof logger.warn).toBe('function');
      expect(typeof logger.info).toBe('function');
      expect(typeof logger.debug).toBe('function');
    });

    it('should handle empty messages', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'debug';
      const logger = createLogger('test-scope');

      logger.error('');
      logger.warn('');
      logger.info('');
      logger.debug('');

      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
      expect(consoleWarnSpy).toHaveBeenCalledTimes(1);
      expect(consoleInfoSpy).toHaveBeenCalledTimes(1);
      expect(consoleDebugSpy).toHaveBeenCalledTimes(1);
    });

    it('should handle special characters in messages', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'debug';
      const logger = createLogger('test-scope');

      const specialMessage = 'Message with \n newline \t tab and "quotes"';
      logger.info(specialMessage);

      expect(consoleInfoSpy).toHaveBeenCalledWith(
        expect.stringContaining(specialMessage)
      );
    });
  });

  describe('multiple loggers', () => {
    it('should create independent loggers with different scopes', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'info';
      
      const logger1 = createLogger('scope-1');
      const logger2 = createLogger('scope-2');

      logger1.info('message from logger1');
      logger2.info('message from logger2');

      expect(consoleInfoSpy).toHaveBeenCalledTimes(2);
      expect(consoleInfoSpy).toHaveBeenCalledWith(
        expect.stringContaining('[scope-1]')
      );
      expect(consoleInfoSpy).toHaveBeenCalledWith(
        expect.stringContaining('[scope-2]')
      );
    });

    it('should share the same log level', () => {
      process.env.TRAINLOOP_LOG_LEVEL = 'warn';
      
      const logger1 = createLogger('scope-1');
      const logger2 = createLogger('scope-2');

      logger1.info('should not appear');
      logger2.info('should not appear');
      logger1.warn('should appear');
      logger2.warn('should appear');

      expect(consoleInfoSpy).not.toHaveBeenCalled();
      expect(consoleWarnSpy).toHaveBeenCalledTimes(2);
    });
  });
});
