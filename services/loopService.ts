import { LoopJob, LoopJobStatus } from '../types';

export interface LoopCreationOptions {
  trackId: string;
  duration: number; // in seconds
  fadeInOut: boolean;
  format: 'mp3' | 'wav';
}

export interface LoopJobResponse {
  id: string;
  trackId: string;
  status: LoopJobStatus;
  progress: number;
  error?: string;
  resultUrl?: string;
  resultPath?: string;
  completedAt?: string;
}

export const loopService = {
  async createLoopJob(options: LoopCreationOptions): Promise<LoopJob> {
    const response = await fetch('/api/loop/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(options),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Failed to create loop job' }));
      throw new Error(errorData.message || 'Failed to create loop job');
    }

    const data: LoopJobResponse = await response.json();
    return {
      id: data.id,
      trackId: data.trackId,
      status: data.status,
      duration: options.duration,
      fadeInOut: options.fadeInOut,
      format: options.format,
      progress: data.progress,
      error: data.error,
      resultUrl: data.resultUrl,
      resultPath: data.resultPath,
      createdAt: new Date(),
      completedAt: data.completedAt ? new Date(data.completedAt) : undefined,
    };
  },

  async getLoopJobStatus(jobId: string): Promise<Partial<LoopJob>> {
    const response = await fetch(`/api/loop/jobs/${jobId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch loop job status');
    }

    const data: LoopJobResponse = await response.json();
    return {
      id: data.id,
      trackId: data.trackId,
      status: data.status,
      progress: data.progress,
      error: data.error,
      resultUrl: data.resultUrl,
      resultPath: data.resultPath,
      createdAt: new Date(),
      completedAt: data.completedAt ? new Date(data.completedAt) : undefined,
    };
  },

  async pollLoopJobStatus(
    jobId: string,
    onProgress: (job: Partial<LoopJob>) => void,
    onComplete: (job: Partial<LoopJob>) => void,
    onError: (error: Error) => void,
    pollInterval = 2000,
    maxAttempts = 300
  ): Promise<void> {
    let attempts = 0;

    const poll = async () => {
      try {
        const job = await this.getLoopJobStatus(jobId);
        onProgress(job);

        if (job.status === LoopJobStatus.COMPLETED) {
          onComplete(job);
        } else if (job.status === LoopJobStatus.FAILED) {
          throw new Error(job.error || 'Loop job failed');
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, pollInterval);
        } else {
          throw new Error('Loop job polling timeout');
        }
      } catch (error) {
        onError(error instanceof Error ? error : new Error('Unknown error'));
      }
    };

    poll();
  },

  formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
  },

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  },
};
