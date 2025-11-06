import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import Database from '../models/Database.js';

class DiffRhythmJobService {
    constructor() {
        this.pythonServiceUrl = process.env.PY_DIFFRHYTHM_URL || 'http://localhost:8000';
        this.db = new Database();
        this.pollingIntervals = new Map(); // Track active polling jobs
    }

    async initialize() {
        await this.db.connect();
        await this.db.initialize();
    }

    async createJob(requestData) {
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
        await this.db.run(
            `INSERT INTO jobs (id, type, status, request_data) VALUES (?, ?, ?, ?)`,
            [jobId, 'diffrhythm', 'pending', JSON.stringify(requestData)]
        );

        try {
            // Submit job to Python service
            const response = await axios.post(`${this.pythonServiceUrl}/generate`, requestData);
            
            if (response.data.job_id) {
                // Update job with external job ID
                await this.db.run(
                    `UPDATE jobs SET status = ?, message = ? WHERE id = ?`,
                    ['processing', 'Job submitted to DiffRhythm service', jobId]
                );

                // Start polling for status updates
                this.startPolling(jobId, response.data.job_id);
            }

            return {
                jobId,
                status: 'accepted',
                message: 'DiffRhythm generation job created successfully'
            };
        } catch (error) {
            // Update job status to failed
            await this.db.run(
                `UPDATE jobs SET status = ?, error = ? WHERE id = ?`,
                ['failed', `Failed to submit to Python service: ${error.message}`, jobId]
            );
            throw error;
        }
    }

    startPolling(localJobId, pythonJobId) {
        // Clear any existing polling for this job
        if (this.pollingIntervals.has(localJobId)) {
            clearInterval(this.pollingIntervals.get(localJobId));
        }

        const pollInterval = setInterval(async () => {
            try {
                const response = await axios.get(`${this.pythonServiceUrl}/status/${pythonJobId}`);
                const { status, progress, message, error } = response.data;

                // Update job in database
                await this.db.run(
                    `UPDATE jobs SET status = ?, progress = ?, message = ?, error = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
                    [status, progress, message, error, localJobId]
                );

                // If job is completed or failed, get the full result and stop polling
                if (status === 'completed' || status === 'failed') {
                    clearInterval(pollInterval);
                    this.pollingIntervals.delete(localJobId);

                    if (status === 'completed') {
                        await this.handleJobCompletion(localJobId, pythonJobId);
                    }
                }
            } catch (error) {
                console.error(`Error polling job ${pythonJobId}:`, error.message);
                
                // Don't stop polling on network errors, but update job with warning
                await this.db.run(
                    `UPDATE jobs SET message = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
                    [`Warning: Polling error - ${error.message}`, localJobId]
                );
            }
        }, 2000); // Poll every 2 seconds

        this.pollingIntervals.set(localJobId, pollInterval);
    }

    async handleJobCompletion(localJobId, pythonJobId) {
        try {
            // Get full result from Python service
            const response = await axios.get(`${this.pythonServiceUrl}/result/${pythonJobId}`);
            const result = response.data;

            // Create track record
            const trackId = uuidv4();
            const requestData = JSON.parse(
                (await this.db.get(`SELECT request_data FROM jobs WHERE id = ?`, [localJobId])).request_data
            );

            await this.db.run(`
                INSERT INTO tracks (
                    id, job_id, title, artist, album, genre, mood, language, 
                    duration, wav_path, mp3_path, file_size_wav, file_size_mp3, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `, [
                trackId,
                localJobId,
                `Generated Track - ${requestData.prompt.substring(0, 50)}...`,
                'AI Generated',
                'DiffRhythm Collection',
                requestData.genre || 'Unknown',
                requestData.mood || 'Unknown',
                requestData.language,
                result.duration,
                result.wav_file.file_path,
                result.mp3_file.file_path,
                result.wav_file.file_size,
                result.mp3_file.file_size,
                JSON.stringify(result.metadata)
            ]);

            // Update job with result data
            await this.db.run(
                `UPDATE jobs SET status = ?, result_data = ? WHERE id = ?`,
                ['completed', JSON.stringify(result), localJobId]
            );

            console.log(`Job ${localJobId} completed successfully, track created: ${trackId}`);
        } catch (error) {
            console.error(`Error handling job completion for ${localJobId}:`, error.message);
            
            await this.db.run(
                `UPDATE jobs SET status = ?, error = ? WHERE id = ?`,
                ['failed', `Failed to process completion: ${error.message}`, localJobId]
            );
        }
    }

    async getJobStatus(jobId) {
        const job = await this.db.get(
            `SELECT * FROM jobs WHERE id = ?`,
            [jobId]
        );

        if (!job) {
            throw new Error('Job not found');
        }

        // Parse JSON fields
        const requestData = job.request_data ? JSON.parse(job.request_data) : null;
        const resultData = job.result_data ? JSON.parse(job.result_data) : null;

        return {
            jobId: job.id,
            type: job.type,
            status: job.status,
            progress: job.progress || 0,
            message: job.message,
            error: job.error,
            requestData,
            resultData,
            createdAt: job.created_at,
            updatedAt: job.updated_at
        };
    }

    async getTrack(trackId) {
        const track = await this.db.get(
            `SELECT * FROM tracks WHERE id = ?`,
            [trackId]
        );

        if (!track) {
            throw new Error('Track not found');
        }

        // Parse JSON fields
        const metadata = track.metadata ? JSON.parse(track.metadata) : {};

        return {
            id: track.id,
            jobId: track.job_id,
            title: track.title,
            artist: track.artist,
            album: track.album,
            genre: track.genre,
            mood: track.mood,
            language: track.language,
            duration: track.duration,
            wavPath: track.wav_path,
            mp3Path: track.mp3_path,
            fileSizeWav: track.file_size_wav,
            fileSizeMp3: track.file_size_mp3,
            metadata,
            createdAt: track.created_at,
            updatedAt: track.updated_at
        };
    }

    async listJobs(limit = 50, offset = 0) {
        const jobs = await this.db.all(
            `SELECT id, type, status, progress, message, created_at, updated_at 
             FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?`,
            [limit, offset]
        );

        return jobs.map(job => ({
            jobId: job.id,
            type: job.type,
            status: job.status,
            progress: job.progress || 0,
            message: job.message,
            createdAt: job.created_at,
            updatedAt: job.updated_at
        }));
    }

    async listTracks(limit = 50, offset = 0) {
        const tracks = await this.db.all(
            `SELECT id, job_id, title, artist, album, genre, mood, language, 
                    duration, file_size_wav, file_size_mp3, created_at 
             FROM tracks ORDER BY created_at DESC LIMIT ? OFFSET ?`,
            [limit, offset]
        );

        return tracks.map(track => ({
            id: track.id,
            jobId: track.job_id,
            title: track.title,
            artist: track.artist,
            album: track.album,
            genre: track.genre,
            mood: track.mood,
            language: track.language,
            duration: track.duration,
            fileSizeWav: track.file_size_wav,
            fileSizeMp3: track.file_size_mp3,
            createdAt: track.created_at
        }));
    }

    async deleteJob(jobId) {
        // Stop polling if active
        if (this.pollingIntervals.has(jobId)) {
            clearInterval(this.pollingIntervals.get(jobId));
            this.pollingIntervals.delete(jobId);
        }

        // Delete job and related records
        await this.db.run(`DELETE FROM exports WHERE track_id IN (SELECT id FROM tracks WHERE job_id = ?)`, [jobId]);
        await this.db.run(`DELETE FROM tracks WHERE job_id = ?`, [jobId]);
        await this.db.run(`DELETE FROM jobs WHERE id = ?`, [jobId]);
    }

    async cleanup() {
        // Stop all polling intervals
        for (const [jobId, interval] of this.pollingIntervals) {
            clearInterval(interval);
        }
        this.pollingIntervals.clear();

        // Close database connection
        await this.db.close();
    }
}

export default DiffRhythmJobService;