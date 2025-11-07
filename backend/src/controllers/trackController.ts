import { Request, Response } from 'express';
import { DatabaseService } from '../db/databaseService.js';
import { logger } from '../config/logger.js';

export class TrackController {
  constructor(private db: DatabaseService) {}

  async getTrack(req: Request, res: Response): Promise<void> {
    const { id } = req.params as { id: string };
    
    try {
      const track = await this.db.getTrack(id);
      
      if (!track) {
        res.status(404).json({
          error: 'Not Found',
          message: `Track ${id} not found`,
        });
        return;
      }

      // Parse JSON fields
      const metadata = track.metadata ? JSON.parse(track.metadata) : {};

      res.json({
        ...track,
        metadata
      });
    } catch (error) {
      logger.error('Failed to get track:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to get track',
      });
    }
  }

  async listTracks(req: Request, res: Response): Promise<void> {
    const { limit, offset } = req.query as { limit?: string; offset?: string };
    
    try {
      const limitNum = Math.min(parseInt(limit || '20', 10), 100);
      const offsetNum = parseInt(offset || '0', 10);
      
      const tracks = await this.db.listTracks(limitNum, offsetNum);
      
      res.json({
        tracks: tracks.map(track => {
          const metadata = track.metadata ? JSON.parse(track.metadata) : {};
          return {
            ...track,
            metadata
          };
        }),
        pagination: {
          limit: limitNum,
          offset: offsetNum,
          count: tracks.length,
        },
      });
    } catch (error) {
      logger.error('Failed to list tracks:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to list tracks',
      });
    }
  }

  async getDiffRhythmTrack(req: Request, res: Response): Promise<void> {
    const { id } = req.params as { id: string };
    
    try {
      const track = await this.db.getTrack(id);
      
      if (!track) {
        res.status(404).json({
          error: 'Not Found',
          message: `Track ${id} not found`,
        });
        return;
      }

      // Parse JSON fields
      const metadata = track.metadata ? JSON.parse(track.metadata) : {};

      res.json({
        ...track,
        metadata
      });
    } catch (error) {
      logger.error('Failed to get DiffRhythm track:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to get track',
      });
    }
  }

  async listDiffRhythmTracks(req: Request, res: Response): Promise<void> {
    const { limit, offset } = req.query as { limit?: string; offset?: string };
    
    try {
      const limitNum = Math.min(parseInt(limit || '20', 10), 100);
      const offsetNum = parseInt(offset || '0', 10);
      
      const tracks = await this.db.listTracks(limitNum, offsetNum);
      
      res.json({
        tracks: tracks.map(track => {
          const metadata = track.metadata ? JSON.parse(track.metadata) : {};
          return {
            ...track,
            metadata
          };
        }),
        pagination: {
          limit: limitNum,
          offset: offsetNum,
          count: tracks.length,
        },
      });
    } catch (error) {
      logger.error('Failed to list DiffRhythm tracks:', error);
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'Failed to list tracks',
      });
    }
  }
}