import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

import DiffRhythmController from './controllers/DiffRhythmController.js';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Static file serving for generated audio files
const storageDir = process.env.STORAGE_DIR || path.join(__dirname, '../output');
app.use('/files', express.static(storageDir));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        services: {
            python: process.env.PY_DIFFRHYTHM_URL || 'http://localhost:8000',
            storage: storageDir
        }
    });
});

// Initialize DiffRhythm controller
const diffrhythmController = new DiffRhythmController();

// DiffRhythm routes
app.post('/api/diffrhythm/jobs', (req, res) => diffrhythmController.createJob(req, res));
app.get('/api/jobs/:id', (req, res) => diffrhythmController.getJobStatus(req, res));
app.get('/api/tracks/:id', (req, res) => diffrhythmController.getTrack(req, res));
app.get('/api/jobs', (req, res) => diffrhythmController.listJobs(req, res));
app.get('/api/tracks', (req, res) => diffrhythmController.listTracks(req, res));
app.delete('/api/jobs/:id', (req, res) => diffrhythmController.deleteJob(req, res));
app.get('/api/download/:jobId/:format', (req, res) => diffrhythmController.downloadFile(req, res));

// Legacy compatibility routes for frontend
app.post('/api/generate', async (req, res) => {
    try {
        // Map frontend request to DiffRhythm format
        const { prompt, model, duration, language, genre, mood } = req.body;
        
        if (model !== 'diffrhythm') {
            return res.status(400).json({ error: 'Only DiffRhythm model is currently supported' });
        }

        const result = await diffrhythmController.jobService.createJob({
            prompt,
            durationSeconds: duration || 30,
            language: language || 'en',
            genre,
            mood
        });

        res.status(202).json({
            trackId: result.jobId,
            status: 'processing',
            message: 'Generation started'
        });
    } catch (error) {
        console.error('Error in legacy generate endpoint:', error);
        res.status(400).json({
            error: 'Failed to start generation',
            message: error.message
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
    });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        error: 'Not found',
        message: `Route ${req.method} ${req.originalUrl} not found`
    });
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('SIGTERM received, shutting down gracefully');
    await diffrhythmController.jobService.cleanup();
    process.exit(0);
});

process.on('SIGINT', async () => {
    console.log('SIGINT received, shutting down gracefully');
    await diffrhythmController.jobService.cleanup();
    process.exit(0);
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 AI Music Generator Backend running on port ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
    console.log(`🎵 DiffRhythm API: http://localhost:${PORT}/api/diffrhythm/jobs`);
    console.log(`📁 Storage directory: ${storageDir}`);
    console.log(`🐍 Python service: ${process.env.PY_DIFFRHYTHM_URL || 'http://localhost:8000'}`);
});

export default app;