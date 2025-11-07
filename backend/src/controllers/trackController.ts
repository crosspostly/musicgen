import { Request, Response } from 'express';
import { DatabaseService } from '../db/databaseService.js';
import { logger } from '../config/logger.js';

export class TrackController {
  constructor(private db: DatabaseService) {}

  async getTrack(req: Request, res: Response): Promise<void> {
    const { id } = req.params as { id: string };
    
    const track = this.db.getTrack(id);
    
    if (!track) {
      res.status(404).json({
        error: 'Not Found',
        message: `Track ${id} not found`,
      });
      return;
    }

    res.json(track);
  }

  async listTracks(req: Request, res: Response): Promise<void> {
    const { limit, offset } = req.query as { limit?: string; offset?: string };
    
    const limitNum = Math.min(parseInt(limit || '20', 10), 100);
    const offsetNum = parseInt(offset || '0', 10);
    
    const tracks = this.db.listTracks(limitNum, offsetNum);
    
    res.json({
      tracks,
      pagination: {
        limit: limitNum,
        offset: offsetNum,
        count: tracks.length,
      },
    });
  }
}