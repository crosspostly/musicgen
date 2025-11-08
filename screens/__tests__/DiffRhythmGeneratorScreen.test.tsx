import { describe, it, expect, vi, beforeEach } from 'vitest';

// Test error message mapping
function getErrorMessage(errorType: string, detail?: string): string {
  switch (errorType) {
    case 'timeout':
      return 'The generation took too long (over 2 minutes). Please try with shorter lyrics or try again.';
    case 'network_error':
      return 'Cannot reach the server. Please check your internet connection and try again.';
    case 'http_error':
      return detail || 'The server encountered an error. Please try again in a moment.';
    default:
      return detail || 'An unexpected error occurred. Please try again.';
  }
}

describe('Error message mapping', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('error handling and display', () => {
    it('should map timeout error type to user-friendly message', () => {
      const message = getErrorMessage('timeout');
      expect(message).toContain('took too long');
      expect(message).toContain('over 2 minutes');
      expect(message).toContain('try with shorter lyrics');
    });

    it('should map network error type to user-friendly message', () => {
      const message = getErrorMessage('network_error');
      expect(message).toContain('Cannot reach the server');
      expect(message).toContain('internet connection');
    });

    it('should map http error type using detail', () => {
      const message = getErrorMessage('http_error', 'Server error occurred');
      expect(message).toBe('Server error occurred');
    });

    it('should provide default http error message', () => {
      const message = getErrorMessage('http_error');
      expect(message).toContain('server encountered an error');
    });

    it('should map unknown error type', () => {
      const message = getErrorMessage('unknown_error', 'Something went wrong');
      expect(message).toBe('Something went wrong');
    });

    it('should provide default unknown error message', () => {
      const message = getErrorMessage('unknown_error');
      expect(message).toContain('unexpected error');
      expect(message).toContain('try again');
    });
  });

  describe('timeout messaging', () => {
    it('should encourage retries with shorter content for timeout', () => {
      const message = getErrorMessage('timeout');
      expect(message).toContain('Please try with shorter lyrics or try again');
    });
  });

  describe('network error messaging', () => {
    it('should suggest checking internet connection', () => {
      const message = getErrorMessage('network_error');
      expect(message).toContain('check your internet connection');
    });
  });
});
