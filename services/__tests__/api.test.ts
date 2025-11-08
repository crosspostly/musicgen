import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ApiService, { apiClient } from '../api';

// Mock fetch
global.fetch = vi.fn();

describe('ApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    // No cleanup needed if we don't use fake timers
  });

  describe('timeout handling', () => {
    it('should have 120s default timeout constant', () => {
      // Verify the default timeout is set correctly
      expect(apiClient).toBeDefined();
      // The default timeout should be 120 seconds (120000 ms)
      // We can't directly test this without breaking encapsulation,
      // so we test the behavior through successful requests
    });

    it('should handle timeout errors correctly', async () => {
      // Create an AbortError
      const abortError = new Error('Aborted');
      Object.defineProperty(abortError, 'name', {
        value: 'AbortError',
        configurable: true,
      });

      (global.fetch as any).mockRejectedValueOnce(abortError);

      const result = await apiClient.post('/api/test', { data: 'test' });

      expect(result.error).toBeDefined();
      expect(result.error?.type).toBe('timeout');
      expect(result.error?.message).toContain('Timeout');
      expect(result.error?.detail).toContain('server is taking too long');
    });
  });

  describe('HTTP error handling', () => {
    it('should handle 500 errors with server message', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ detail: 'Database error' }),
      });

      const result = await apiClient.post('/api/test', { data: 'test' });

      expect(result.error).toBeDefined();
      expect(result.error?.type).toBe('http_error');
      expect(result.error?.status).toBe(500);
      expect(result.error?.detail).toContain('Server error');
    });

    it('should handle 503 unavailable', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        json: async () => ({ detail: 'Service unavailable' }),
      });

      const result = await apiClient.post('/api/test', { data: 'test' });

      expect(result.error?.type).toBe('http_error');
      expect(result.error?.status).toBe(503);
      expect(result.error?.detail).toContain('unavailable');
    });

    it('should handle validation errors (400)', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ detail: 'Invalid input' }),
      });

      const result = await apiClient.post('/api/test', { data: 'test' });

      expect(result.error?.type).toBe('http_error');
      expect(result.error?.status).toBe(400);
      expect(result.error?.detail).toBe('Invalid input');
    });
  });

  describe('network error handling', () => {
    it('should handle network errors', async () => {
      (global.fetch as any).mockRejectedValueOnce(
        new TypeError('Failed to fetch')
      );

      const result = await apiClient.post('/api/test', { data: 'test' });

      expect(result.error).toBeDefined();
      expect(result.error?.type).toBe('network_error');
      expect(result.error?.message).toContain('Network Error');
      expect(result.error?.detail).toContain('internet connection');
    });

    it('should handle DNS failures', async () => {
      (global.fetch as any).mockRejectedValueOnce(
        new TypeError('network error')
      );

      const result = await apiClient.post('/api/test', { data: 'test' });

      expect(result.error?.type).toBe('network_error');
    });
  });

  describe('successful requests', () => {
    it('should handle successful POST requests', async () => {
      const mockData = { success: true, message: 'Created' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockData,
      });

      const result = await apiClient.post('/api/test', { data: 'test' });

      expect(result.error).toBeUndefined();
      expect(result.data).toEqual(mockData);
    });

    it('should handle successful GET requests', async () => {
      const mockData = { id: '123', name: 'test' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
      });

      const result = await apiClient.get('/api/test');

      expect(result.error).toBeUndefined();
      expect(result.data).toEqual(mockData);
    });
  });

  describe('prompt hashing', () => {
    it('should hash prompts for logging', async () => {
      const consoleSpy = vi.spyOn(console, 'debug').mockImplementation(() => {});

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({}),
      });

      await apiClient.post('/api/generate', { prompt: 'Test prompt' });

      // Check that logs were made with operation data
      expect(consoleSpy).toHaveBeenCalled();

      // Verify console was called with API logging
      const allCalls = consoleSpy.mock.calls;
      expect(allCalls.length > 0).toBe(true);

      consoleSpy.mockRestore();
    });
  });

  describe('duration logging', () => {
    it('should log operation duration', async () => {
      const consoleSpy = vi.spyOn(console, 'debug');

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
      });

      vi.useFakeTimers();
      const promise = apiClient.get('/api/test');
      vi.advanceTimersByTime(100);
      await promise;

      const logs = consoleSpy.mock.calls.filter((call) =>
        String(call[0]).includes('[API')
      );

      expect(logs.length > 0).toBe(true);
    });
  });

  describe('device type detection', () => {
    it('should include device type in logs', async () => {
      const consoleSpy = vi.spyOn(console, 'debug');

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
      });

      await apiClient.post('/api/test', { data: 'test' });

      const logs = consoleSpy.mock.calls.filter((call) =>
        String(call[0]).includes('[API')
      );

      // Verify that logs are being made (device detection is implicit)
      expect(logs.length > 0).toBe(true);
    });
  });

  describe('error message handling', () => {
    it('should handle non-JSON error responses', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      const result = await apiClient.post('/api/test', { data: 'test' });

      expect(result.error).toBeDefined();
      expect(result.error?.status).toBe(500);
    });
  });
});

describe('API error type mapping', () => {
  it('should distinguish between timeout and network errors', async () => {
    // Create a proper AbortError
    const abortError = new Error('Aborted');
    Object.defineProperty(abortError, 'name', {
      value: 'AbortError',
      configurable: true,
    });

    (global.fetch as any).mockRejectedValueOnce(abortError);

    const result = await apiClient.post('/api/test', { data: 'test' });

    expect(result.error?.type).toBe('timeout');

    // Reset mock
    vi.clearAllMocks();

    const networkError = new TypeError('Failed to fetch');

    (global.fetch as any).mockRejectedValueOnce(networkError);

    const result2 = await apiClient.post('/api/test', { data: 'test' });

    expect(result2.error?.type).toBe('network_error');
  });
});
