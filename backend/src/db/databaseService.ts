import Database from 'better-sqlite3';
import { promises as fs } from 'fs';
import { dirname } from 'path';
import { loadEnv } from '../config/env.js';
import { logger } from '../config/logger.js';
import { Job, Track } from '../types/index.js';

const env = loadEnv();

export class DatabaseService {
  private db: Database.Database;

  constructor() {
    // Ensure database directory exists
    const dbDir = dirname(env.DATABASE_PATH);
    fs.mkdir(dbDir, { recursive: true }).catch(err => {
      if (err.code !== 'EEXIST') {
        throw err;
      }
    });

    this.db = new Database(env.DATABASE_PATH);
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('foreign_keys = ON');
    this.initialize();
  }

  private initialize(): void {
    try {
      // Create jobs table
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS jobs (
          id TEXT PRIMARY KEY,
          type TEXT NOT NULL CHECK (type IN ('diffrhythm', 'loop', 'metadata')),
          status TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
          progress REAL NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 1),
          result TEXT,
          error TEXT,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          started_at DATETIME,
          completed_at DATETIME
        )
      `);

      // Create tracks table
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS tracks (
          id TEXT PRIMARY KEY,
          job_id TEXT NOT NULL,
          model TEXT NOT NULL,
          duration REAL NOT NULL,
          file_path TEXT NOT NULL,
          metadata TEXT NOT NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
        )
      `);

      // Create job_events table for auditing
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS job_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          job_id TEXT NOT NULL,
          event_type TEXT NOT NULL,
          message TEXT,
          timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
        )
      `);

      // Create indexes
      this.db.exec(`
        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (status);
        CREATE INDEX IF NOT EXISTS idx_jobs_type ON jobs (type);
        CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs (created_at);
        CREATE INDEX IF NOT EXISTS idx_tracks_job_id ON tracks (job_id);
        CREATE INDEX IF NOT EXISTS idx_job_events_job_id ON job_events (job_id);
      `);

      logger.info('Database initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize database:', error);
      throw error;
    }
  }

  // Job operations
  createJob(job: Omit<Job, 'createdAt' | 'updatedAt'>): Job {
    const stmt = this.db.prepare(`
      INSERT INTO jobs (id, type, status, progress, result, error, started_at, completed_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      job.id,
      job.type,
      job.status,
      job.progress,
      job.result ? JSON.stringify(job.result) : null,
      job.error || null,
      job.startedAt?.toISOString() || null,
      job.completedAt?.toISOString() || null
    );

    return this.getJob(job.id)!;
  }

  getJob(id: string): Job | undefined {
    const stmt = this.db.prepare('SELECT * FROM jobs WHERE id = ?');
    const row = stmt.get(id) as any;
    
    if (!row) return undefined;

    return {
      id: row.id,
      type: row.type,
      status: row.status,
      progress: row.progress,
      result: row.result ? JSON.parse(row.result) : undefined,
      error: row.error,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
      startedAt: row.started_at ? new Date(row.started_at) : undefined,
      completedAt: row.completed_at ? new Date(row.completed_at) : undefined,
    };
  }

  updateJob(id: string, updates: Partial<Job>): Job | undefined {
    const fields = [];
    const values = [];

    if (updates.status !== undefined) {
      fields.push('status = ?');
      values.push(updates.status);
    }
    if (updates.progress !== undefined) {
      fields.push('progress = ?');
      values.push(updates.progress);
    }
    if (updates.result !== undefined) {
      fields.push('result = ?');
      values.push(updates.result ? JSON.stringify(updates.result) : null);
    }
    if (updates.error !== undefined) {
      fields.push('error = ?');
      values.push(updates.error);
    }
    if (updates.startedAt !== undefined) {
      fields.push('started_at = ?');
      values.push(updates.startedAt.toISOString());
    }
    if (updates.completedAt !== undefined) {
      fields.push('completed_at = ?');
      values.push(updates.completedAt.toISOString());
    }

    fields.push('updated_at = CURRENT_TIMESTAMP');
    values.push(id);

    const stmt = this.db.prepare(`
      UPDATE jobs SET ${fields.join(', ')} WHERE id = ?
    `);
    
    stmt.run(...values);
    return this.getJob(id);
  }

  listJobs(limit = 50, offset = 0): Job[] {
    const stmt = this.db.prepare(`
      SELECT * FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?
    `);
    const rows = stmt.all(limit, offset) as any[];
    
    return rows.map(row => ({
      id: row.id,
      type: row.type,
      status: row.status,
      progress: row.progress,
      result: row.result ? JSON.parse(row.result) : undefined,
      error: row.error,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
      startedAt: row.started_at ? new Date(row.started_at) : undefined,
      completedAt: row.completed_at ? new Date(row.completed_at) : undefined,
    }));
  }

  // Track operations
  createTrack(track: Omit<Track, 'createdAt' | 'updatedAt'>): Track {
    const stmt = this.db.prepare(`
      INSERT INTO tracks (id, job_id, model, duration, file_path, metadata)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      track.id,
      track.jobId,
      track.model,
      track.duration,
      track.filePath,
      JSON.stringify(track.metadata)
    );

    return this.getTrack(track.id)!;
  }

  getTrack(id: string): Track | undefined {
    const stmt = this.db.prepare('SELECT * FROM tracks WHERE id = ?');
    const row = stmt.get(id) as any;
    
    if (!row) return undefined;

    return {
      id: row.id,
      jobId: row.job_id,
      model: row.model,
      duration: row.duration,
      filePath: row.file_path,
      metadata: JSON.parse(row.metadata),
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
    };
  }

  listTracks(limit = 50, offset = 0): Track[] {
    const stmt = this.db.prepare(`
      SELECT * FROM tracks ORDER BY created_at DESC LIMIT ? OFFSET ?
    `);
    const rows = stmt.all(limit, offset) as any[];
    
    return rows.map(row => ({
      id: row.id,
      jobId: row.job_id,
      model: row.model,
      duration: row.duration,
      filePath: row.file_path,
      metadata: JSON.parse(row.metadata),
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
    }));
  }

  // Job events
  addJobEvent(jobId: string, eventType: string, message?: string): void {
    const stmt = this.db.prepare(`
      INSERT INTO job_events (job_id, event_type, message) VALUES (?, ?, ?)
    `);
    stmt.run(jobId, eventType, message);
  }

  close(): void {
    this.db.close();
    logger.info('Database connection closed');
  }
}