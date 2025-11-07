import { Request, Response } from 'express';
import { logger } from '../config/logger.js';
import { loadEnv } from '../config/env.js';
import { StorageService } from '../services/storageService.js';
import { DatabaseService } from '../db/databaseService.js';

export class HealthController {
  constructor(
    private storageService: StorageService,
    private db: DatabaseService
  ) {}

  async check(req: Request, res: Response): Promise<void> {
    const env = loadEnv();
    const startTime = Date.now();
    
    try {
      // Check database connectivity
      const dbCheck = this.checkDatabase();
      
      // Check storage directories
      const storageCheck = await this.checkStorage();
      
      // Check environment variables
      const envCheck = this.checkEnvironment();
      
      const responseTime = Date.now() - startTime;
      const allChecksPass = dbCheck && storageCheck && envCheck;
      
      const healthData = {
        status: allChecksPass ? 'healthy' : 'unhealthy',
        timestamp: new Date().toISOString(),
        responseTime: `${responseTime}ms`,
        version: process.env.npm_package_version || '0.0.0',
        environment: env.NODE_ENV,
        checks: {
          database: dbCheck ? 'pass' : 'fail',
          storage: storageCheck ? 'pass' : 'fail',
          environment: envCheck ? 'pass' : 'fail',
        },
        services: {
          diffRhythm: {
            url: env.PY_DIFFRHYTHM_URL,
            status: 'unknown', // TODO: Add actual health check
          },
        },
        storage: {
          directory: env.STORAGE_DIR,
          databasePath: env.DATABASE_PATH,
        },
      };
      
      res.status(allChecksPass ? 200 : 503).json(healthData);
      
    } catch (error) {
      logger.error('Health check failed:', error);
      
      res.status(503).json({
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        responseTime: `${Date.now() - startTime}ms`,
        error: 'Health check failed',
      });
    }
  }

  private checkDatabase(): boolean {
    try {
      // Simple query to check database connectivity
      this.db.listJobs(1, 0);
      return true;
    } catch (error) {
      logger.error('Database health check failed:', error);
      return false;
    }
  }

  private async checkStorage(): Promise<boolean> {
    try {
      // Check if storage directory exists and is writable
      await this.storageService.ensureDir(this.storageService.getStorageDir());
      return true;
    } catch (error) {
      logger.error('Storage health check failed:', error);
      return false;
    }
  }

  private checkEnvironment(): boolean {
    try {
      const env = loadEnv();
      // Check critical environment variables
      return !!(env.STORAGE_DIR && env.DATABASE_PATH);
    } catch (error) {
      logger.error('Environment health check failed:', error);
      return false;
    }
  }

  async ready(req: Request, res: Response): Promise<void> {
    // Readiness probe - check if all critical services are ready
    const dbReady = this.checkDatabase();
    const storageReady = await this.checkStorage();
    
    if (dbReady && storageReady) {
      res.status(200).json({
        status: 'ready',
        timestamp: new Date().toISOString(),
      });
    } else {
      res.status(503).json({
        status: 'not ready',
        timestamp: new Date().toISOString(),
        checks: {
          database: dbReady,
          storage: storageReady,
        },
      });
    }
  }

  async live(req: Request, res: Response): Promise<void> {
    // Liveness probe - simple check if the process is running
    res.status(200).json({
      status: 'alive',
      timestamp: new Date().toISOString(),
    });
  }
}