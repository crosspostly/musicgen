import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { DatabaseService } from '../db/databaseService.js';
import { logger } from '../config/logger.js';
import type { Job, Track, TrackMetadata } from '../types/index.js';

export interface DiffRhythmJobRequest {
    prompt: string;
    durationSeconds: number;
    language: 'ru' | 'en';
    genre?: string;
    mood?: string;
}

export interface DiffRhythmJobStatus {
    job_id: string;
    status: 'pending' | 'loading_model' | 'preparing_prompt' | 'generating_audio' | 'exporting' | 'completed' | 'failed';
    progress: number;
    message?: string;
    error?: string;
    result_url?: string;
    wav_path?: string;
    mp3_path?: string;
    duration?: number;
}

export class DiffRhythmJobService {
    private readonly pythonServiceUrl: string;
    private readonly pollingIntervals = new Map<string, NodeJS.Timeout>();

    constructor(
        private readonly db: DatabaseService,
        private readonly storageService: any // StorageService type
    ) {
        this.pythonServiceUrl = process.env.PY_DIFFRHYTHM_URL || 'http://localhost:8000';
    }

    async createJob(requestData: DiffRhythmJobRequest): Promise<{ jobId: string; status: string; message: string }> {
        const jobId = uuidv4();
        
        // Validate request data
        const { prompt, durationSeconds, language, genre, mood } = requestData;
        
        if (!prompt || prompt.trim().length === 0) {
            throw new Error('Prompt is required');
        }
        
        if (durationSeconds < 10 || durationSeconds > 300) {
            throw new Error('Duration must be between 10 and 300 seconds');
        }
        
        if (!['ru', 'en'].includes(language)) {
            throw new Error('Language must be either "ru" or "en"');
        }

        // Store job in database
        await this.db.createJob({
            id: jobId,
            type: 'diffrhythm',
            status: 'pending',
            progress: 0,
            request_data: JSON.stringify(requestData)
        });

        try {
            // Submit job to Python service
            const response = await axios.post(`${this.pythonServiceUrl}/generate`, requestData);
            
            if (response.data.job_id) {
                // Update job with external job ID
                await this.db.updateJob(jobId, {
                    status: 'processing',
                    message: 'Job submitted to DiffRhythm service'
                });

                // Start polling for status updates
                this.startPolling(jobId, response.data.job_id);
            }

            return {
                jobId,
                status: 'accepted',
                message: 'DiffRhythm generation job created successfully'
            };
        } catch (error: any) {
            // Update job status to failed
            await this.db.updateJob(jobId, {
                status: 'failed',
                error: `Failed to submit to Python service: ${error.message}`
            });
            throw error;
        }
    }

    private startPolling(localJobId: string, pythonJobId: string): void {
        // Clear any existing polling for this job
        if (this.pollingIntervals.has(localJobId)) {
            clearInterval(this.pollingIntervals.get(localJobId)!);
        }

        const pollInterval = setInterval(async () => {
            try {
                const response = await axios.get<DiffRhythmJobStatus>(`${this.pythonServiceUrl}/status/${pythonJobId}`);
                const { status, progress, message, error } = response.data;

                // Update job in database
                await this.db.updateJob(localJobId, {
                    status: status,
                    progress: progress,
                    message,
                    error
                });

                // If job is completed or failed, get the full result and stop polling
                if (status === 'completed' || status === 'failed') {
                    clearInterval(pollInterval);
                    this.pollingIntervals.delete(localJobId);

                    if (status === 'completed') {
                        await this.handleJobCompletion(localJobId, pythonJobId);
                    }
                }
            } catch (error: any) {
                logger.error(`Error polling job ${pythonJobId}:`, error.message);
                
                // Don't stop polling on network errors, but update job with warning
                await this.db.updateJob(localJobId, {
                    message: `Warning: Polling error - ${error.message}`
                });
            }
        }, 2000); // Poll every 2 seconds

        this.pollingIntervals.set(localJobId, pollInterval);
    }

    private async handleJobCompletion(localJobId: string, pythonJobId: string): Promise<void> {
        try {
            // Get full result from Python service
            const response = await axios.get(`${this.pythonServiceUrl}/result/${pythonJobId}`);
            const result = response.data;

            // Create track record
            const trackId = uuidv4();
            const requestData = JSON.parse(
                (await this.db.getJob(localJobId))!.request_data
            ) as DiffRhythmJobRequest;

            await this.db.createTrack({
                id: trackId,
                job_id: localJobId,
                model: 'diffrhythm',
                duration: result.duration || requestData.durationSeconds,
                file_path: result.mp3_path || result.wav_path,
                metadata: {
                    title: `Generated Track - ${requestData.prompt.substring(0, 50)}...`,
                    artist: 'AI Generated',
                    album: 'DiffRhythm Collection',
                    genre: requestData.genre || 'Unknown',
                    mood: requestData.mood || 'Unknown',
                    language: requestData.language,
                    prompt: requestData.prompt,
                    created_at: result.metadata?.created_at,
                    completed_at: result.metadata?.completed_at
                }
            });

            // Update job with result data
            await this.db.updateJob(localJobId, {
                status: 'completed',
                result_data: JSON.stringify(result)
            });

            logger.info(`Job ${localJobId} completed successfully, track created: ${trackId}`);
        } catch (error: any) {
            logger.error(`Error handling job completion for ${localJobId}:`, error.message);
            
            await this.db.updateJob(localJobId, {
                status: 'failed',
                error: `Failed to process completion: ${error.message}`
            });
        }
    }

    async getJob(jobId: string): Promise<Job | null> {
        const job = await this.db.getJob(jobId);
        
        if (!job) {
            throw new Error('Job not found');
        }

        // Parse JSON fields
        const requestData = job.request_data ? JSON.parse(job.request_data) : null;
        const resultData = job.result_data ? JSON.parse(job.result_data) : null;

        return {
            ...job,
            requestData,
            resultData
        };
    }

    async getTrack(trackId: string): Promise<Track | null> {
        const track = await this.db.getTrack(trackId);
        
        if (!track) {
            throw new Error('Track not found');
        }

        // Parse JSON fields
        const metadata = track.metadata ? JSON.parse(track.metadata) : {};

        return {
            ...track,
            metadata
        };
    }

    async listJobs(limit: number = 50, offset: number = 0): Promise<Job[]> {
        const jobs = await this.db.listJobs(limit, offset);
        
        return jobs.map(job => ({
            id: job.id,
            type: job.type,
            status: job.status,
            progress: job.progress || 0,
            message: job.message,
            error: job.error,
            createdAt: job.created_at,
            updatedAt: job.updated_at
        }));
    }

    async listTracks(limit: number = 50, offset: number = 0): Promise<Track[]> {
        const tracks = await this.db.listTracks(limit, offset);
        
        return tracks.map(track => ({
            id: track.id,
            jobId: track.job_id,
            model: track.model,
            duration: track.duration,
            filePath: track.file_path,
            metadata: track.metadata ? JSON.parse(track.metadata) : {},
            createdAt: track.created_at,
            updatedAt: track.updated_at
        }));
    }

    async deleteJob(jobId: string): Promise<void> {
        // Stop polling if active
        if (this.pollingIntervals.has(jobId)) {
            clearInterval(this.pollingIntervals.get(jobId)!);
            this.pollingIntervals.delete(jobId);
        }

        // Delete job and related records
        await this.db.deleteTrackByJobId(jobId);
        await this.db.deleteJob(jobId);
    }

    async cleanup(): Promise<void> {
        // Stop all polling intervals
        for (const [jobId, interval] of this.pollingIntervals) {
            clearInterval(interval);
        }
        this.pollingIntervals.clear();
    }
}