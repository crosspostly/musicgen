import { Request, Response } from 'express';
import { JobService } from '../services/jobService.js';
import { logger } from '../config/logger.js';

export class JobController {
  constructor(private jobService: JobService) {}

  async getJob(req: Request, res: Response): Promise<void> {
    const { id } = req.params as { id: string };
    
    const job = await this.jobService.getJob(id);
    
    if (!job) {
      res.status(404).json({
        error: 'Not Found',
        message: `Job ${id} not found`,
      });
      return;
    }

    res.json(job);
  }

  async listJobs(req: Request, res: Response): Promise<void> {
    const { limit, offset } = req.query as { limit?: string; offset?: string };
    
    const limitNum = Math.min(parseInt(limit || '20', 10), 100);
    const offsetNum = parseInt(offset || '0', 10);
    
    const jobs = await this.jobService.listJobs(limitNum, offsetNum);
    
    res.json({
      jobs,
      pagination: {
        limit: limitNum,
        offset: offsetNum,
        count: jobs.length,
      },
    });
  }

  async createDiffRhythmJob(req: Request, res: Response): Promise<void> {
    const { prompt, duration, tempo, seed } = req.body;
    
    try {
      const job = await this.jobService.createJob('diffrhythm');
      
      // TODO: Implement actual DiffRhythm processing
      // For now, just return the job as queued
      logger.info(`DiffRhythm job ${job.id} queued with prompt: ${prompt.substring(0, 50)}...`);
      
      res.status(201).json({
        message: 'DiffRhythm job created successfully',
        job,
      });
    } catch (error) {
      logger.error('Failed to create DiffRhythm job:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to create job',
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

  async createMetadataBatchJob(req: Request, res: Response): Promise<void> {
    const { trackIds, metadata } = req.body;
    
    try {
      const job = await this.jobService.createJob('metadata');
      
      // TODO: Implement actual metadata batch processing
      logger.info(`Metadata batch job ${job.id} queued for ${trackIds.length} tracks`);
      
      res.status(201).json({
        message: 'Metadata batch job created successfully',
        job,
      });
    } catch (error) {
      logger.error('Failed to create metadata batch job:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to create job',
      });
    }
  }
}