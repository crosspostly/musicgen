import { Request, Response } from 'express';
import { JobService } from '../services/jobService.js';
import { logger } from '../config/logger.js';

export class JobController {
  constructor(private jobService: JobService) {}

  async getJob(req: Request, res: Response): Promise<void> {
    const { id } = req.params as { id: string };
    
    try {
      const job = await this.jobService.getDiffRhythmJob(id);
      res.json(job);
    } catch (error: any) {
      if (error.message === 'Job not found') {
        res.status(404).json({
          error: 'Not Found',
          message: `Job ${id} not found`,
        });
        return;
      }
      
      logger.error('Failed to get job:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to get job',
      });
    }
  }

  async listJobs(req: Request, res: Response): Promise<void> {
    const { limit, offset } = req.query as { limit?: string; offset?: string };
    
    try {
      const limitNum = Math.min(parseInt(limit || '20', 10), 100);
      const offsetNum = parseInt(offset || '0', 10);
      
      const jobs = await this.jobService.listDiffRhythmJobs(limitNum, offsetNum);
      
      res.json({
        jobs,
        pagination: {
          limit: limitNum,
          offset: offsetNum,
          count: jobs.length,
        },
      });
    } catch (error: any) {
      logger.error('Failed to list jobs:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to list jobs',
      });
    }
  }

  async createDiffRhythmJob(req: Request, res: Response): Promise<void> {
    const { prompt, duration, tempo, seed, language, genre, mood } = req.body;
    
    try {
      const result = await this.jobService.createDiffRhythmJob({
        prompt,
        durationSeconds: duration || 30,
        language: language || 'en',
        genre,
        mood
      });
      
      logger.info(`DiffRhythm job ${result.jobId} queued with prompt: ${prompt.substring(0, 50)}...`);
      
      res.status(201).json({
        message: 'DiffRhythm job created successfully',
        job: result,
      });
    } catch (error: any) {
      logger.error('Failed to create DiffRhythm job:', {
        error: error.message,
        stack: error.stack,
      });

      // Map specific error types to user-friendly messages
      let statusCode = 500;
      let detail = 'Failed to create generation job. Please try again.';

      if (error.message && error.message.includes('Prompt is required')) {
        statusCode = 400;
        detail = 'Lyrics/prompt is required.';
      } else if (error.message && error.message.includes('Duration must be between')) {
        statusCode = 400;
        detail = 'Duration must be between 10 and 300 seconds.';
      } else if (error.message && error.message.includes('Language must be')) {
        statusCode = 400;
        detail = 'Language must be either "ru" or "en".';
      } else if (error.message && error.message.includes('Failed to submit to Python service')) {
        statusCode = 503;
        detail = 'Music generation service is currently unavailable. Please try again later.';
      }

      res.status(statusCode).json({
        error: 'Generation Error',
        message: 'Failed to create job',
        detail,
      });
    }
  }

  async createLoopJob(req: Request, res: Response): Promise<void> {
    const { sourceUrl, startTime, endTime, fadeDuration } = req.body;
    
    try {
      const job = await this.jobService.createJob('loop');
      
      // TODO: Implement actual loop processing
      logger.info(`Loop job ${job.id} queued for URL: ${sourceUrl}`);
      
      res.status(201).json({
        message: 'Loop job created successfully',
        job,
      });
    } catch (error) {
      logger.error('Failed to create loop job:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to create job',
      });
    }
  }

  async deleteJob(req: Request, res: Response): Promise<void> {
    const { id } = req.params as { id: string };
    
    try {
      await this.jobService.deleteDiffRhythmJob(id);
      res.json({ message: 'Job deleted successfully' });
    } catch (error) {
      logger.error('Failed to delete job:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to delete job',
      });
    }
  }

  async downloadFile(req: Request, res: Response): Promise<void> {
    try {
      const { jobId, format } = req.params;
      
      // Get job to find track
      const job = await this.jobService.getDiffRhythmJob(jobId);
      if (job.status !== 'completed') {
        return res.status(400).json({ error: 'Job not completed' });
      }

      // Get track - for now, simulate track data
      const track = await this.jobService.getDiffRhythmTrack(jobId);
      
      let filePath: string, mimeType: string, fileName: string;
      
      if (format === 'wav') {
        filePath = job.resultData?.wav_path || '/tmp/audio.wav';
        mimeType = 'audio/wav';
        fileName = `${track?.metadata?.title || 'audio'}.wav`;
      } else if (format === 'mp3') {
        filePath = job.resultData?.mp3_path || '/tmp/audio.mp3';
        mimeType = 'audio/mpeg';
        fileName = `${track?.metadata?.title || 'audio'}.mp3`;
      } else {
        return res.status(400).json({ error: 'Invalid format. Use wav or mp3' });
      }

      if (!filePath) {
        return res.status(404).json({ error: 'File not found' });
      }

      // Set headers for file download
      res.setHeader('Content-Type', mimeType);
      res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
      
      // For now, return a placeholder response
      res.json({
        message: 'File download ready',
        fileName,
        format,
        filePath
      });
    } catch (error) {
      logger.error('Error downloading file:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to download file',
      });
    }
  }
}