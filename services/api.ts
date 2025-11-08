/**
 * API Service with enhanced error handling and timeout support
 */

const DEFAULT_TIMEOUT_MS = 120000; // 120 seconds

export type ErrorType = 'timeout' | 'http_error' | 'network_error' | 'unknown_error';

export interface ApiError {
  type: ErrorType;
  message: string;
  detail?: string;
  status?: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

class ApiService {
  private timeout: number;

  constructor(timeoutMs: number = DEFAULT_TIMEOUT_MS) {
    this.timeout = timeoutMs;
  }

  /**
   * Make a fetch request with timeout handling
   */
  private async fetchWithTimeout<T>(
    url: string,
    options?: RequestInit,
    customTimeout?: number
  ): Promise<Response> {
    const timeoutMs = customTimeout || this.timeout;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error: any) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * Determine device type for logging
   */
  private getDeviceType(): string {
    const ua = navigator.userAgent;
    if (/Mobile|Android|iPhone|iPad|iPod/.test(ua)) {
      return 'mobile';
    } else if (/Tablet|iPad/.test(ua)) {
      return 'tablet';
    }
    return 'desktop';
  }

  /**
   * Calculate hash of a string
   */
  private hashString(str: string): string {
    let hash = 0;
    if (str.length === 0) return '0';
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16);
  }

  /**
   * Log operation details
   */
  private logOperation(
    method: string,
    url: string,
    status: 'start' | 'success' | 'error',
    details?: Record<string, any>
  ): void {
    const device = this.getDeviceType();
    const timestamp = new Date().toISOString();

    const logEntry = {
      timestamp,
      method,
      url,
      device,
      status,
      ...details,
    };

    if (status === 'error') {
      console.error('[API Error]', logEntry);
    } else if (status === 'start') {
      console.debug('[API Request]', logEntry);
    } else {
      console.debug('[API Success]', logEntry);
    }
  }

  /**
   * Handle API errors and convert to user-friendly messages
   */
  private handleError(error: any, url: string): ApiError {
    // Timeout error
    if (error.name === 'AbortError') {
      this.logOperation('GET', url, 'error', {
        errorType: 'timeout',
        message: 'Request timeout',
      });
      return {
        type: 'timeout',
        message: 'Timeout: The request took too long to complete (120s limit)',
        detail:
          'The server is taking too long to respond. Please try again or check your connection.',
      };
    }

    // Network error (no internet, DNS failure, etc.)
    if (
      error instanceof TypeError &&
      (error.message === 'Failed to fetch' ||
        error.message.includes('fetch') ||
        error.message.includes('network'))
    ) {
      this.logOperation('GET', url, 'error', {
        errorType: 'network_error',
        message: error.message,
      });
      return {
        type: 'network_error',
        message: 'Network Error: Unable to connect to the server',
        detail:
          'Please check your internet connection and try again.',
      };
    }

    // Unknown error
    this.logOperation('GET', url, 'error', {
      errorType: 'unknown_error',
      message: error.message,
    });
    return {
      type: 'unknown_error',
      message: 'An unexpected error occurred',
      detail: 'Please try again later.',
    };
  }

  /**
   * Generic POST request with error handling
   */
  async post<T>(
    url: string,
    body: Record<string, any>,
    timeoutMs?: number
  ): Promise<ApiResponse<T>> {
    const startTime = performance.now();
    const device = this.getDeviceType();

    // Log prompt hash if present in body
    const promptHash = body.prompt
      ? `#${this.hashString(body.prompt)}`
      : 'N/A';

    this.logOperation('POST', url, 'start', {
      promptHash,
      device,
      bodyKeys: Object.keys(body),
    });

    try {
      const response = await this.fetchWithTimeout(
        url,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
        timeoutMs
      );

      const duration = performance.now() - startTime;

      // Handle HTTP errors
      if (!response.ok) {
        let errorDetail = 'Unknown error';
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorData.message || errorDetail;
        } catch {
          // If response body is not JSON, use status text
          errorDetail = response.statusText;
        }

        const apiError: ApiError = {
          type: 'http_error',
          message: `HTTP Error ${response.status}`,
          detail:
            response.status === 500
              ? 'Server error. Please try again later.'
              : response.status === 503
                ? 'Backend service is unavailable. Please try again later.'
                : errorDetail,
          status: response.status,
        };

        this.logOperation('POST', url, 'error', {
          status: response.status,
          errorType: 'http_error',
          duration: duration.toFixed(2),
          promptHash,
        });

        return { error: apiError };
      }

      // Success
      const data = await response.json();

      this.logOperation('POST', url, 'success', {
        status: response.status,
        duration: duration.toFixed(2),
        promptHash,
        device,
      });

      return { data };
    } catch (error: any) {
      const duration = performance.now() - startTime;
      const apiError = this.handleError(error, url);

      this.logOperation('POST', url, 'error', {
        duration: duration.toFixed(2),
        promptHash,
      });

      return { error: apiError };
    }
  }

  /**
   * Generic GET request with error handling
   */
  async get<T>(
    url: string,
    timeoutMs?: number
  ): Promise<ApiResponse<T>> {
    const startTime = performance.now();
    const device = this.getDeviceType();

    this.logOperation('GET', url, 'start', { device });

    try {
      const response = await this.fetchWithTimeout(url, undefined, timeoutMs);

      const duration = performance.now() - startTime;

      // Handle HTTP errors
      if (!response.ok) {
        let errorDetail = 'Unknown error';
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorData.message || errorDetail;
        } catch {
          errorDetail = response.statusText;
        }

        const apiError: ApiError = {
          type: 'http_error',
          message: `HTTP Error ${response.status}`,
          detail:
            response.status === 500
              ? 'Server error. Please try again later.'
              : response.status === 503
                ? 'Backend service is unavailable. Please try again later.'
                : errorDetail,
          status: response.status,
        };

        this.logOperation('GET', url, 'error', {
          status: response.status,
          errorType: 'http_error',
          duration: duration.toFixed(2),
        });

        return { error: apiError };
      }

      // Success
      const data = await response.json();

      this.logOperation('GET', url, 'success', {
        status: response.status,
        duration: duration.toFixed(2),
        device,
      });

      return { data };
    } catch (error: any) {
      const duration = performance.now() - startTime;
      const apiError = this.handleError(error, url);

      this.logOperation('GET', url, 'error', {
        duration: duration.toFixed(2),
      });

      return { error: apiError };
    }
  }
}

// Export singleton instance with 120s timeout
export const apiClient = new ApiService(DEFAULT_TIMEOUT_MS);

// Export class for testing purposes
export default ApiService;
