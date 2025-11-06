import { Router } from 'express';
import { TrackController } from '../controllers/trackController.js';
import { validateParams } from '../middleware/validation.js';
import { trackIdSchema, paginationSchema } from '../types/schemas.js';

export function createTrackRoutes(trackController: TrackController): Router {
  const router = Router();

  // GET /api/tracks - List all tracks
  router.get('/', 
    (req, res, next) => {
      const parsed = paginationSchema.parse(req.query);
      (req.query as any) = parsed;
      next();
    },
    (req, res) => trackController.listTracks(req, res)
  );

  // GET /api/tracks/:id - Get specific track
  router.get('/:id', 
    validateParams(trackIdSchema),
    (req, res) => trackController.getTrack(req, res)
  );

  return router;
}