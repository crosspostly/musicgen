import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import { join } from 'path';
import { loadEnv } from './config/env.js';
import { logger } from './config/logger.js';
import { DatabaseService } from './db/databaseService.js';
import { StorageService } from './services/storageService.js';
import { JobService } from './services/jobService.js';
import { JobController } from './controllers/jobController.js';
import { TrackController } from './controllers/trackController.js';
import { HealthController } from './controllers/healthController.js';
import { createJobRoutes } from './routes/jobRoutes.js';
import { createTrackRoutes } from './routes/trackRoutes.js';
import { createHealthRoutes } from './routes/healthRoutes.js';
import { errorHandler, notFoundHandler } from './middleware/errorHandler.js';

async function bootstrap(): Promise<void> {
  const env = loadEnv();
  
  // Initialize services
  const storageService = new StorageService();
  const db = new DatabaseService();
  const jobService = new JobService(db);
  
  // Initialize storage directories
  await storageService.initialize();
  
  // Create controllers
  const jobController = new JobController(jobService);
  const trackController = new TrackController(db);
  const healthController = new HealthController(storageService, db);
  
  // Create Express app
  const app = express();
  
  // Trust proxy for proper IP logging behind reverse proxies
  app.set('trust proxy', 1);
  
  // Middleware
  app.use(cors({
    origin: env.NODE_ENV === 'production' ? false : true, // Restrict in production
    credentials: true,
  }));
  
  app.use(morgan('combined', {
    stream: {
      write: (message: string) => logger.info(message.trim()),
    },
  }));
  
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ extended: true, limit: '10mb' }));
  
  // Static file serving for storage directory
  app.use('/storage', express.static(storageService.getStorageDir(), {
    maxAge: '1d',
    etag: true,
    lastModified: true,
  }));
  
  // API Routes
  const apiRouter = express.Router();
  
  // Health routes (no /api prefix for convenience)
  app.use('/api/health', createHealthRoutes(healthController));
  
  // API routes
  apiRouter.use('/jobs', createJobRoutes(jobController));
  apiRouter.use('/tracks', createTrackRoutes(trackController));
  
  // Apply API routes
  app.use('/api', apiRouter);
  
  // Root endpoint
  app.get('/', (req, res) => {
    res.json({
      name: 'AI Music Generator Backend',
      version: process.env.npm_package_version || '0.0.0',
      environment: env.NODE_ENV,
      timestamp: new Date().toISOString(),
      endpoints: {
        health: '/api/health',
        jobs: '/api/jobs',
        tracks: '/api/tracks',
        storage: '/storage',
      },
    });
  });
  
  // Error handling middleware (must be last)
  app.use(notFoundHandler);
  app.use(errorHandler);
  
  // Start server
  const server = app.listen(env.PORT, () => {
    logger.info(`🚀 Server running on port ${env.PORT} in ${env.NODE_ENV} mode`);
    logger.info(`📁 Storage directory: ${storageService.getStorageDir()}`);
    logger.info(`🗄️  Database: ${env.DATABASE_PATH}`);
    logger.info(`🔗 API endpoints available at http://localhost:${env.PORT}/api`);
  });
  
  // Graceful shutdown
  const gracefulShutdown = (signal: string) => {
    logger.info(`Received ${signal}, starting graceful shutdown...`);
    
    server.close(() => {
      logger.info('HTTP server closed');
      
      // Close database connection
      db.close();
      
      // Cleanup DiffRhythm service
      jobService.cleanup();
      
      logger.info('Graceful shutdown completed');
      process.exit(0);
    });
    
    // Force shutdown after 30 seconds
    setTimeout(() => {
      logger.error('Forced shutdown after timeout');
      process.exit(1);
    }, 30000);
  };
  
  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));
  
  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    logger.error('Uncaught Exception:', error);
    process.exit(1);
  });
  
  process.on('unhandledRejection', (reason, promise) => {
    logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
  });
}

// Start the application
bootstrap().catch((error) => {
  logger.error('Failed to start application:', error);
  process.exit(1);
});