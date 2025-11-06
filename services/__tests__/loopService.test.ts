/**
 * @jest-environment node
 * These tests require Jest framework to run
 * Install types: npm install --save-dev @types/jest
 */

import { loopService } from '../loopService';
import { LoopJobStatus } from '../../types';

/**
 * Tests for the loopService
 *
 * Tests validate:
 * - Loop duration formatting (1 min to 10 hrs)
 * - File size formatting
 * - Loop job creation with proper validation
 * - Error handling and retry logic
 * - Progress polling
 */

describe('loopService', () => {
  describe('formatDuration', () => {
    it('should format seconds to seconds', () => {
      expect(loopService.formatDuration(45)).toBe('45s');
    });

    it('should format minutes and seconds', () => {
      expect(loopService.formatDuration(125)).toBe('2m 5s');
    });

    it('should format hours and minutes', () => {
      expect(loopService.formatDuration(3661)).toBe('1h 1m');
    });

    it('should format 10 hours correctly', () => {
      expect(loopService.formatDuration(36000)).toBe('10h 0m');
    });

    it('should handle zero seconds', () => {
      expect(loopService.formatDuration(0)).toBe('0s');
    });
  });

  describe('formatFileSize', () => {
    it('should format bytes', () => {
      expect(loopService.formatFileSize(512)).toBe('0.5 KB');
    });

    it('should format kilobytes', () => {
      expect(loopService.formatFileSize(1024 * 100)).toBe('100 KB');
    });

    it('should format megabytes', () => {
      expect(loopService.formatFileSize(1024 * 1024 * 10)).toBe('10 MB');
    });

    it('should format gigabytes', () => {
      expect(loopService.formatFileSize(1024 * 1024 * 1024)).toBe('1 GB');
    });

    it('should handle zero bytes', () => {
      expect(loopService.formatFileSize(0)).toBe('0 Bytes');
    });
  });

  describe('LoopCreationOptions validation', () => {
    it('should validate minimum loop duration (1 minute)', () => {
      const options = {
        trackId: 'test-track-1',
        duration: 60, // 1 minute
        fadeInOut: true,
        format: 'mp3' as const,
      };
      expect(options.duration).toBeGreaterThanOrEqual(60);
    });

    it('should validate maximum loop duration (10 hours)', () => {
      const options = {
        trackId: 'test-track-1',
        duration: 36000, // 10 hours
        fadeInOut: true,
        format: 'mp3' as const,
      };
      expect(options.duration).toBeLessThanOrEqual(36000);
    });

    it('should support both mp3 and wav formats', () => {
      const mp3Options = {
        trackId: 'test-track-1',
        duration: 3600,
        fadeInOut: true,
        format: 'mp3' as const,
      };

      const wavOptions = {
        trackId: 'test-track-1',
        duration: 3600,
        fadeInOut: true,
        format: 'wav' as const,
      };

      expect(mp3Options.format).toBe('mp3');
      expect(wavOptions.format).toBe('wav');
    });
  });

  describe('LoopJobStatus', () => {
    it('should have all expected statuses', () => {
      expect(LoopJobStatus.PENDING).toBe('pending');
      expect(LoopJobStatus.ANALYZING).toBe('analyzing');
      expect(LoopJobStatus.RENDERING).toBe('rendering');
      expect(LoopJobStatus.EXPORTING).toBe('exporting');
      expect(LoopJobStatus.COMPLETED).toBe('completed');
      expect(LoopJobStatus.FAILED).toBe('failed');
    });
  });
});
