import { Router } from 'express';
import { HealthController } from '../controllers/healthController.js';

export function createHealthRoutes(healthController: HealthController): Router {
  const router = Router();

  // GET /api/health - Comprehensive health check
  router.get('/', 
    (req, res) => healthController.check(req, res)
  );

  // GET /api/health/ready - Readiness probe
  router.get('/ready', 
    (req, res) => healthController.ready(req, res)
  );

  // GET /api/health/live - Liveness probe
  router.get('/live', 
    (req, res) => healthController.live(req, res)
  );

  return router;
}