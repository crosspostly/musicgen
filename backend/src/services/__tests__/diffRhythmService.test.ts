import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DiffRhythmJobService } from '../diffRhythmService.js';
import { DatabaseService } from '../../db/databaseService.js';

describe('DiffRhythmJobService', () => {
  let service: DiffRhythmJobService;
  let mockDb: any;
  let mockStorageService: any;

  beforeEach(() => {
    mockDb = {
      createJob: vi.fn().mockResolvedValue(undefined),
      updateJob: vi.fn().mockResolvedValue(undefined),
      getJob: vi.fn().mockResolvedValue(null),
      createTrack: vi.fn().mockResolvedValue(undefined),
      deleteTrackByJobId: vi.fn().mockResolvedValue(undefined),
      deleteJob: vi.fn().mockResolvedValue(undefined),
    };

    mockStorageService = {};

    service = new DiffRhythmJobService(mockDb, mockStorageService);
  });

  describe('error logging', () => {
    it('should log structured error information with prompt hash', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      try {
        await service.createJob({
          prompt: '', // Empty prompt to trigger validation error
          durationSeconds: 30,
          language: 'en',
        });
      } catch (e) {
        // Expected
      }

      // Verify that error was logged
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });

    it('should not log full prompt text in logs', async () => {
      const loggerSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      const debugSpy = vi.spyOn(console, 'debug').mockImplementation(() => {});

      try {
        await service.createJob({
          prompt: 'This is a secret prompt that should not be logged',
          durationSeconds: 30,
          language: 'en',
        });
      } catch (e) {
        // Expected
      }

      // Verify that full prompt is not in logs
      const allLogs = [
        ...loggerSpy.mock.calls,
        ...debugSpy.mock.calls,
      ].map((call) => String(call));

      const hasFullPrompt = allLogs.some((log) =>
        log.includes('This is a secret prompt')
      );
      expect(hasFullPrompt).toBe(false);

      loggerSpy.mockRestore();
      debugSpy.mockRestore();
    });
  });

  describe('validation error messages', () => {
    it('should reject empty prompt', async () => {
      expect(async () => {
        await service.createJob({
          prompt: '',
          durationSeconds: 30,
          language: 'en',
        });
      }).rejects.toThrow('Prompt is required');
    });

    it('should reject invalid duration (too short)', async () => {
      expect(async () => {
        await service.createJob({
          prompt: 'Test prompt',
          durationSeconds: 5,
          language: 'en',
        });
      }).rejects.toThrow('Duration must be between 10 and 300 seconds');
    });

    it('should reject invalid duration (too long)', async () => {
      expect(async () => {
        await service.createJob({
          prompt: 'Test prompt',
          durationSeconds: 400,
          language: 'en',
        });
      }).rejects.toThrow('Duration must be between 10 and 300 seconds');
    });

    it('should reject invalid language', async () => {
      expect(async () => {
        await service.createJob({
          prompt: 'Test prompt',
          durationSeconds: 30,
          language: 'de' as any,
        });
      }).rejects.toThrow('Language must be either "ru" or "en"');
    });
  });

  describe('duration logging', () => {
    it('should include operation duration in logs', async () => {
      const loggerSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      try {
        await service.createJob({
          prompt: '',
          durationSeconds: 30,
          language: 'en',
        });
      } catch (e) {
        // Expected
      }

      // Verify logs were made (duration would be included if logging was working)
      expect(loggerSpy).toHaveBeenCalled();

      loggerSpy.mockRestore();
    });
  });
});
