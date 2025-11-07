import { promises as fs } from 'fs';
import { join } from 'path';
import { loadEnv } from '../config/env.js';
import { logger } from '../config/logger.js';

const env = loadEnv();

export class StorageService {
  private readonly storageDir: string;

  constructor() {
    this.storageDir = env.STORAGE_DIR;
  }

  async initialize(): Promise<void> {
    try {
      await fs.mkdir(this.storageDir, { recursive: true });
      await fs.mkdir(this.getRawDir(), { recursive: true });
      await fs.mkdir(this.getProcessedDir(), { recursive: true });
      await fs.mkdir(this.getLoopsDir(), { recursive: true });
      await fs.mkdir(this.getMetadataDir(), { recursive: true });
      
      logger.info(`Storage directories initialized at ${this.storageDir}`);
    } catch (error) {
      logger.error('Failed to initialize storage directories:', error);
      throw error;
    }
  }

  getStorageDir(): string {
    return this.storageDir;
  }

  getRawDir(): string {
    return join(this.storageDir, 'raw');
  }

  getProcessedDir(): string {
    return join(this.storageDir, 'processed');
  }

  getLoopsDir(): string {
    return join(this.storageDir, 'loops');
  }

  getMetadataDir(): string {
    return join(this.storageDir, 'metadata');
  }

  getRawPath(filename: string): string {
    return join(this.getRawDir(), filename);
  }

  getProcessedPath(filename: string): string {
    return join(this.getProcessedDir(), filename);
  }

  getLoopPath(filename: string): string {
    return join(this.getLoopsDir(), filename);
  }

  getMetadataPath(filename: string): string {
    return join(this.getMetadataDir(), filename);
  }

  async ensureDir(dirPath: string): Promise<void> {
    await fs.mkdir(dirPath, { recursive: true });
  }

  async fileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  async deleteFile(filePath: string): Promise<void> {
    try {
      await fs.unlink(filePath);
    } catch (error) {
      logger.warn(`Failed to delete file ${filePath}:`, error);
    }
  }
}