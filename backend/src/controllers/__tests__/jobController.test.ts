import { describe, it, expect, vi, beforeEach } from 'vitest';
import { JobController } from '../jobController.js';

describe('JobController - Error Handling', () => {
  let controller: JobController;
  let mockJobService: any;

  beforeEach(() => {
    mockJobService = {
      createDiffRhythmJob: vi.fn(),
      getDiffRhythmJob: vi.fn(),
      listDiffRhythmJobs: vi.fn(),
      deleteDiffRhythmJob: vi.fn(),
      getDiffRhythmTrack: vi.fn(),
    };

    controller = new JobController(mockJobService);
  });

  describe('error message mapping', () => {
    it('should return 400 for empty prompt', async () => {
      const req = {
        body: {
          prompt: '',
          duration: 30,
          language: 'en',
        },
      } as any;

      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;

      mockJobService.createDiffRhythmJob.mockRejectedValueOnce(
        new Error('Prompt is required')
      );

      await controller.createDiffRhythmJob(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: 'Lyrics/prompt is required.',
        })
      );
    });

    it('should return 400 for invalid duration', async () => {
      const req = {
        body: {
          prompt: 'Test',
          duration: 5,
          language: 'en',
        },
      } as any;

      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;

      mockJobService.createDiffRhythmJob.mockRejectedValueOnce(
        new Error('Duration must be between 10 and 300 seconds')
      );

      await controller.createDiffRhythmJob(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: 'Duration must be between 10 and 300 seconds.',
        })
      );
    });

    it('should return 400 for invalid language', async () => {
      const req = {
        body: {
          prompt: 'Test',
          duration: 30,
          language: 'de',
        },
      } as any;

      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;

      mockJobService.createDiffRhythmJob.mockRejectedValueOnce(
        new Error('Language must be either "ru" or "en"')
      );

      await controller.createDiffRhythmJob(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: 'Language must be either "ru" or "en".',
        })
      );
    });

    it('should return 503 when Python service is unavailable', async () => {
      const req = {
        body: {
          prompt: 'Test',
          duration: 30,
          language: 'en',
        },
      } as any;

      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;

      mockJobService.createDiffRhythmJob.mockRejectedValueOnce(
        new Error('Failed to submit to Python service: connect ECONNREFUSED')
      );

      await controller.createDiffRhythmJob(req, res);

      expect(res.status).toHaveBeenCalledWith(503);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: 'Music generation service is currently unavailable. Please try again later.',
        })
      );
    });

    it('should return 500 for unknown errors', async () => {
      const req = {
        body: {
          prompt: 'Test',
          duration: 30,
          language: 'en',
        },
      } as any;

      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;

      mockJobService.createDiffRhythmJob.mockRejectedValueOnce(
        new Error('Database connection error')
      );

      await controller.createDiffRhythmJob(req, res);

      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: 'Failed to create generation job. Please try again.',
        })
      );
    });

    it('should include error code and message', async () => {
      const req = {
        body: {
          prompt: 'Test',
          duration: 30,
          language: 'en',
        },
      } as any;

      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;

      mockJobService.createDiffRhythmJob.mockRejectedValueOnce(
        new Error('Prompt is required')
      );

      await controller.createDiffRhythmJob(req, res);

      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Generation Error',
          message: 'Failed to create job',
        })
      );
    });
  });

  describe('successful job creation', () => {
    it('should return 201 on success', async () => {
      const mockJob = {
        jobId: 'job-123',
        status: 'accepted',
      };

      const req = {
        body: {
          prompt: 'Test prompt',
          duration: 30,
          language: 'en',
        },
      } as any;

      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;

      mockJobService.createDiffRhythmJob.mockResolvedValueOnce(mockJob);

      await controller.createDiffRhythmJob(req, res);

      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'DiffRhythm job created successfully',
          job: mockJob,
        })
      );
    });
  });
});
