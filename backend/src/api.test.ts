import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import { StorageService } from '../src/services/storageService.js';
import { DatabaseService } from '../src/db/databaseService.js';
import { JobService } from '../src/services/jobService.js';
import { JobController } from '../src/controllers/jobController.js';
import { TrackController } from '../src/controllers/trackController.js';
import { HealthController } from '../src/controllers/healthController.js';
import { createJobRoutes } from '../src/routes/jobRoutes.js';
import { createTrackRoutes } from '../src/routes/trackRoutes.js';
import { createHealthRoutes } from '../src/routes/healthRoutes.js';
import express from 'express';
import cors from 'cors';
import { promises as fs } from 'fs';

describe('API Integration Tests', () => {
  let app: express.Application;
  let storageService: StorageService;
  let db: DatabaseService;
  let jobService: JobService;
  
  beforeAll(async () => {
    // Set test environment
    process.env.NODE_ENV = 'test';
    process.env.STORAGE_DIR = './test-storage';
    process.env.DATABASE_PATH = './test-storage/test.sqlite';
    
    // Initialize services
    storageService = new StorageService();
    await storageService.initialize();
    
    db = new DatabaseService();
    jobService = new JobService(db);
    
    // Create controllers
    const jobController = new JobController(jobService);
    const trackController = new TrackController(db);
    const healthController = new HealthController(storageService, db);
    
    // Create Express app
    app = express();
    app.use(cors());
    app.use(express.json());
    
    // Routes
    app.use('/api/health', createHealthRoutes(healthController));
    app.use('/api/jobs', createJobRoutes(jobController));
    app.use('/api/tracks', createTrackRoutes(trackController));
  });
  
  afterAll(async () => {
    // Clean up test data
    db.close();
    
    // Remove test storage directory
    try {
      await fs.rm('./test-storage', { recursive: true, force: true });
    } catch (error) {
      // Ignore cleanup errors
    }
  });
  
  describe('Health Endpoints', () => {
    it('GET /api/health should return health status', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);
      
      expect(response.body).toHaveProperty('status');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('checks');
      expect(response.body.checks).toHaveProperty('database');
      expect(response.body.checks).toHaveProperty('storage');
    });
    
    it('GET /api/health/ready should return readiness', async () => {
      const response = await request(app)
        .get('/api/health/ready')
        .expect(200);
      
      expect(response.body).toHaveProperty('status', 'ready');
    });
    
    it('GET /api/health/live should return liveness', async () => {
      const response = await request(app)
        .get('/api/health/live')
        .expect(200);
      
      expect(response.body).toHaveProperty('status', 'alive');
    });
  });
  
  describe('Job Endpoints', () => {
    it('GET /api/jobs should return job list', async () => {
      const response = await request(app)
        .get('/api/jobs')
        .expect(200);
      
      expect(response.body).toHaveProperty('jobs');
      expect(response.body).toHaveProperty('pagination');
      expect(Array.isArray(response.body.jobs)).toBe(true);
      // Jobs may exist from previous tests, just verify the structure
      expect(response.body.jobs.length).toBeGreaterThanOrEqual(0);
    });
    
    it('POST /api/jobs/diffrhythm should create a DiffRhythm job', async () => {
      const jobData = {
        prompt: 'Generate a relaxing piano melody',
        duration: 30,
        tempo: 120,
      };
      
      const response = await request(app)
        .post('/api/jobs/diffrhythm')
        .send(jobData)
        .expect(201);
      
      expect(response.body).toHaveProperty('message');
      expect(response.body).toHaveProperty('job');
      expect(response.body.job).toHaveProperty('id');
      expect(response.body.job).toHaveProperty('type', 'diffrhythm');
      expect(response.body.job).toHaveProperty('status', 'queued');
    });
    
    it('POST /api/jobs/loop should create a loop job', async () => {
      const jobData = {
        sourceUrl: 'https://example.com/audio.mp3',
        startTime: 10,
        endTime: 30,
      };
      
      const response = await request(app)
        .post('/api/jobs/loop')
        .send(jobData)
        .expect(201);
      
      expect(response.body).toHaveProperty('message');
      expect(response.body).toHaveProperty('job');
      expect(response.body.job).toHaveProperty('type', 'loop');
      expect(response.body.job).toHaveProperty('status', 'queued');
    });
    
    it('POST /api/jobs/metadata/batch should create a metadata batch job', async () => {
      const jobData = {
        trackIds: ['550e8400-e29b-41d4-a716-446655440000'],
        metadata: {
          title: 'Test Track',
          artist: 'Test Artist',
          genre: 'Electronic',
        },
      };
      
      const response = await request(app)
        .post('/api/jobs/metadata/batch')
        .send(jobData)
        .expect(201);
      
      expect(response.body).toHaveProperty('message');
      expect(response.body).toHaveProperty('job');
      expect(response.body.job).toHaveProperty('type', 'metadata');
      expect(response.body.job).toHaveProperty('status', 'queued');
    });
    
    it('POST /api/jobs/diffrhythm should validate required fields', async () => {
      const response = await request(app)
        .post('/api/jobs/diffrhythm')
        .send({})
        .expect(400);
      
      expect(response.body).toHaveProperty('error', 'Validation failed');
      expect(response.body).toHaveProperty('details');
      expect(Array.isArray(response.body.details)).toBe(true);
    });
  });
  
  describe('Track Endpoints', () => {
    it('GET /api/tracks should return track list', async () => {
      const response = await request(app)
        .get('/api/tracks')
        .expect(200);
      
      expect(response.body).toHaveProperty('tracks');
      expect(response.body).toHaveProperty('pagination');
      expect(Array.isArray(response.body.tracks)).toBe(true);
      expect(response.body.tracks.length).toBeGreaterThanOrEqual(0);
    });
  });
});