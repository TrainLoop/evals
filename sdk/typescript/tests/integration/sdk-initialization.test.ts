/**
 * Integration test to verify SDK initialization behavior
 */
import { shutdown } from '../../src';

describe('SDK Initialization', () => {
  it('should allow multiple shutdown calls without error', async () => {
    // First shutdown
    await expect(shutdown()).resolves.toBeUndefined();
    
    // Second shutdown should also work
    await expect(shutdown()).resolves.toBeUndefined();
  });

  it('should not have real FileExporter due to mocking', () => {
    // Verify that the FileExporter is mocked
    const { FileExporter } = require('../../src/exporter');
    expect(jest.isMockFunction(FileExporter)).toBe(true);
  });

  it('should have mocked exporter methods', () => {
    const { FileExporter } = require('../../src/exporter');
    const mockInstance = new FileExporter();
    
    expect(mockInstance.recordLLMCall).toBeDefined();
    expect(mockInstance.shutdown).toBeDefined();
    expect(mockInstance.clear).toBeDefined();
    
    // Verify they are mock functions
    expect(jest.isMockFunction(mockInstance.recordLLMCall)).toBe(true);
    expect(jest.isMockFunction(mockInstance.shutdown)).toBe(true);
    expect(jest.isMockFunction(mockInstance.clear)).toBe(true);
  });
});
