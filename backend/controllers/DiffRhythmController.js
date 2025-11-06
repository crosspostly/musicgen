import DiffRhythmJobService from '../services/DiffRhythmJobService.js';

class DiffRhythmController {
    constructor() {
        this.jobService = new DiffRhythmJobService();
        this.initialize();
    }

    async initialize() {
        await this.jobService.initialize();
    }

    async createJob(req, res) {
        try {
            const { prompt, durationSeconds, language, genre, mood } = req.body;

            const result = await this.jobService.createJob({
                prompt,
                durationSeconds,
                language,
                genre,
                mood
            });

            res.status(202).json(result);
        } catch (error) {
            console.error('Error creating DiffRhythm job:', error);
            res.status(400).json({
                error: 'Failed to create generation job',
                message: error.message
            });
        }
    }

    async getJobStatus(req, res) {
        try {
            const { id } = req.params;
            const job = await this.jobService.getJobStatus(id);
            res.json(job);
        } catch (error) {
            if (error.message === 'Job not found') {
                return res.status(404).json({ error: 'Job not found' });
            }
            console.error('Error getting job status:', error);
            res.status(500).json({
                error: 'Failed to get job status',
                message: error.message
            });
        }
    }

    async getTrack(req, res) {
        try {
            const { id } = req.params;
            const track = await this.jobService.getTrack(id);
            res.json(track);
        } catch (error) {
            if (error.message === 'Track not found') {
                return res.status(404).json({ error: 'Track not found' });
            }
            console.error('Error getting track:', error);
            res.status(500).json({
                error: 'Failed to get track',
                message: error.message
            });
        }
    }

    async listJobs(req, res) {
        try {
            const limit = parseInt(req.query.limit) || 50;
            const offset = parseInt(req.query.offset) || 0;
            
            const jobs = await this.jobService.listJobs(limit, offset);
            res.json({ jobs });
        } catch (error) {
            console.error('Error listing jobs:', error);
            res.status(500).json({
                error: 'Failed to list jobs',
                message: error.message
            });
        }
    }

    async listTracks(req, res) {
        try {
            const limit = parseInt(req.query.limit) || 50;
            const offset = parseInt(req.query.offset) || 0;
            
            const tracks = await this.jobService.listTracks(limit, offset);
            res.json({ tracks });
        } catch (error) {
            console.error('Error listing tracks:', error);
            res.status(500).json({
                error: 'Failed to list tracks',
                message: error.message
            });
        }
    }

    async deleteJob(req, res) {
        try {
            const { id } = req.params;
            await this.jobService.deleteJob(id);
            res.json({ message: 'Job deleted successfully' });
        } catch (error) {
            console.error('Error deleting job:', error);
            res.status(500).json({
                error: 'Failed to delete job',
                message: error.message
            });
        }
    }

    async downloadFile(req, res) {
        try {
            const { jobId, format } = req.params;
            
            // Get job to find track
            const job = await this.jobService.getJobStatus(jobId);
            if (job.status !== 'completed') {
                return res.status(400).json({ error: 'Job not completed' });
            }

            // Get track
            const track = await this.jobService.getTrack(job.resultData.metadata?.trackId || jobId);
            
            let filePath, mimeType, fileName;
            if (format === 'wav') {
                filePath = track.wavPath;
                mimeType = 'audio/wav';
                fileName = `${track.title.replace(/[^a-zA-Z0-9]/g, '_')}.wav`;
            } else if (format === 'mp3') {
                filePath = track.mp3Path;
                mimeType = 'audio/mpeg';
                fileName = `${track.title.replace(/[^a-zA-Z0-9]/g, '_')}.mp3`;
            } else {
                return res.status(400).json({ error: 'Invalid format. Use wav or mp3' });
            }

            if (!filePath) {
                return res.status(404).json({ error: 'File not found' });
            }

            const fs = require('fs');
            const path = require('path');
            
            if (!fs.existsSync(filePath)) {
                return res.status(404).json({ error: 'File not found on disk' });
            }

            // Set headers for file download
            res.setHeader('Content-Type', mimeType);
            res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
            
            // Stream file
            const fileStream = fs.createReadStream(filePath);
            fileStream.pipe(res);
            
        } catch (error) {
            console.error('Error downloading file:', error);
            res.status(500).json({
                error: 'Failed to download file',
                message: error.message
            });
        }
    }
}

export default DiffRhythmController;