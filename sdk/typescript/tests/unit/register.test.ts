/**
 * Unit tests for the register/public API functions
 */
import { HEADER_NAME, trainloopTag } from '../../src';

describe('Register Module', () => {
  describe('HEADER_NAME', () => {
    it('should be correctly defined', () => {
      expect(HEADER_NAME).toBe('X-Trainloop-Tag');
    });
  });

  describe('trainloopTag', () => {
    it('should return object with correct header', () => {
      const tag = 'test-tag';
      const result = trainloopTag(tag);

      expect(typeof result).toBe('object');
      expect(result[HEADER_NAME]).toBe(tag);
    });

    it('should handle empty string', () => {
      const result = trainloopTag('');
      
      expect(result).toEqual({ [HEADER_NAME]: '' });
    });

    it('should handle special characters', () => {
      const specialTag = 'test-tag-αβγ-🚀-@#$%';
      const result = trainloopTag(specialTag);

      expect(result[HEADER_NAME]).toBe(specialTag);
    });

    it('should handle very long strings', () => {
      const longTag = 'x'.repeat(1000);
      const result = trainloopTag(longTag);

      expect(result[HEADER_NAME]).toBe(longTag);
      expect(result[HEADER_NAME].length).toBe(1000);
    });

    it('should handle unicode characters', () => {
      const unicodeTag = '测试标签-テストタグ-테스트태그';
      const result = trainloopTag(unicodeTag);

      expect(result[HEADER_NAME]).toBe(unicodeTag);
    });

    it('should create new object each time', () => {
      const tag = 'test';
      const result1 = trainloopTag(tag);
      const result2 = trainloopTag(tag);

      expect(result1).not.toBe(result2); // Different object references
      expect(result1).toEqual(result2);   // But same content
    });
  });
});
