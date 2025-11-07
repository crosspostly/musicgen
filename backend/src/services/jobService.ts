import { v4 as uuidv4 } from 'uuid';
import { DatabaseService } from '../db/databaseService.js';
import { logger } from '../config/logger.js';
import { DiffRhythmJobService } from './diffRhythmService.js';
import { Job } from '../types/index.js';

export class JobService {
  private db: DatabaseService;
  private activeJobs = new Map<string, Promise<any>>();
  private diffRhythmService: DiffRhythmJobService;

  constructor(db: DatabaseService) {
    this.db = db;
    this.diffRhythmService = new DiffRhythmJobService(db);
  }

  async createJob(type: Job['type']): Promise<Job> {
    const job: Omit<Job, 'createdAt' | 'updatedAt'> = {
      id: uuidv4(),
      type,
      status: 'queued',
      progress: 0,
    };

    const createdJob = this.db.createJob(job);
    this.db.addJobEvent(createdJob.id, 'created', `Job of type ${type} created`);
    
    logger.info(`Created job ${createdJob.id} of type ${type}`);
    return createdJob;
  }

  async getJob(id: string): Promise<Job | undefined> {
    return this.db.getJob(id);
  }

  async updateJobProgress(id: string, progress: number): Promise<void> {
    const job = await this.getJob(id);
    if (!job) {
      throw new Error(`Job ${id} not found`);
    }

    if (progress < 0 || progress > 1) {
      throw new Error('Progress must be between 0 and 1');
    }

    this.db.updateJob(id, { progress });
    
    if (Math.floor(progress * 100) % 25 === 0) {
      logger.debug(`Job ${id} progress: ${Math.round(progress * 100)}%`);
    }
  }

  async startJob(id: string): Promise<void> {
    const job = await this.getJob(id);
    if (!job) {
      throw new Error(`Job ${id} not found`);
    }

    if (job.status !== 'queued') {
      throw new Error(`Job ${id} is not queued (current status: ${job.status})`);
    }

    this.db.updateJob(id, {
      status: 'processing',
      startedAt: new Date(),
      progress: 0.01,
    });
    
    this.db.addJobEvent(id, 'started', 'Job processing started');
    logger.info(`Started processing job ${id}`);
  }

  async completeJob(id: string, result?: any): Promise<void> {
    const job = await this.getJob(id);
    if (!job) {
      throw new Error(`Job ${id} not found`);
    }

    this.db.updateJob(id, {
      status: 'completed',
      progress: 1,
      result,
      completedAt: new Date(),
    });
    
    this.db.addJobEvent(id, 'completed', result ? 'Job completed with result' : 'Job completed');
    logger.info(`Completed job ${id}`);
    
    // Clean up from active jobs
    this.activeJobs.delete(id);
  }

  async failJob(id: string, error: string): Promise<void> {
    const job = await this.getJob(id);
    if (!job) {
      throw new Error(`Job ${id} not found`);
    }

    this.db.updateJob(id, {
      status: 'failed',
      error,
      completedAt: new Date(),
    });
    
    this.db.addJobEvent(id, 'failed', `Job failed: ${error}`);
    logger.error(`Failed job ${id}: ${error}`);
    
    // Clean up from active jobs
    this.activeJobs.delete(id);
  }

  async listJobs(limit = 50, offset = 0): Promise<Job[]> {
    return this.db.listJobs(limit, offset);
  }

  async executeAsync<T>(jobId: string, fn: (updateProgress: (progress: number) => Promise<void>) => Promise<T>): Promise<T> {
    // Check if job is already running
    if (this.activeJobs.has(jobId)) {
      throw new Error(`Job ${jobId} is already running`);
    }

    // Start the job
    await this.startJob(jobId);

    // Create the execution promise
    const executionPromise = this.wrapExecutionWithProgress(jobId, fn);
    
    // Store the promise to prevent concurrent execution
    this.activeJobs.set(jobId, executionPromise);

    try {
      const result = await executionPromise;
      await this.completeJob(jobId, result);
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      await this.failJob(jobId, errorMessage);
      throw error;
    }
  }

  private async wrapExecutionWithProgress<T>(
    jobId: string, 
    fn: (updateProgress: (progress: number) => Promise<void>) => Promise<T>
  ): Promise<T> {
    const updateProgress = async (progress: number) => {
      await this.updateJobProgress(jobId, progress);
    };

    return fn(updateProgress);
  }

  getActiveJobCount(): number {
    return this.activeJobs.size;
  }

  async createDiffRhythmJob(requestData: any): Promise<{ jobId: string; status: string; message: string }> {
    return this.diffRhythmService.createJob(requestData);
  }

  async getDiffRhythmJob(jobId: string) {
    return this.diffRhythmService.getJob(jobId);
  }

  async getDiffRhythmTrack(trackId: string) {
    return this.diffRhythmService.getTrack(trackId);
  }

  async listDiffRhythmJobs(limit = 50, offset = 0): Promise<any[]> {
    return this.diffRhythmService.listJobs(limit, offset);
  }

  async listDiffRhythmTracks(limit = 50, offset = 0): Promise<any[]> {
    return this.diffRhythmService.listTracks(limit, offset);
  }

  async deleteDiffRhythmJob(jobId: string): Promise<void> {
    return this.diffRhythmService.deleteJob(jobId);
  }

  async cleanup(): Promise<void> {
    await this.diffRhythmService.cleanup();
  }
}