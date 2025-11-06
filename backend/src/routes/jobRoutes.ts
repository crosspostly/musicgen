import { Router } from 'express';
import { JobController } from '../controllers/jobController.js';
import { validateBody, validateParams } from '../middleware/validation.js';
import { 
  diffRhythmJobSchema, 
  loopJobSchema, 
  metadataBatchSchema, 
  jobIdSchema,
  paginationSchema 
} from '../types/schemas.js';

export function createJobRoutes(jobController: JobController): Router {
  const router = Router();

  // GET /api/jobs - List all jobs
  router.get('/', 
    (req, res, next) => {
      const parsed = paginationSchema.parse(req.query);
      (req.query as any) = parsed;
      next();
    },
    (req, res) => jobController.listJobs(req, res)
  );

  // GET /api/jobs/:id - Get specific job
  router.get('/:id', 
    validateParams(jobIdSchema),
    (req, res) => jobController.getJob(req, res)
  );

  // POST /api/jobs/diffrhythm - Create DiffRhythm job
  router.post('/diffrhythm', 
    validateBody(diffRhythmJobSchema),
    (req, res) => jobController.createDiffRhythmJob(req, res)
  );

  // POST /api/jobs/loop - Create loop job
  router.post('/loop', 
    validateBody(loopJobSchema),
    (req, res) => jobController.createLoopJob(req, res)
  );

  // POST /api/jobs/metadata/batch - Create metadata batch job
  router.post('/metadata/batch', 
    validateBody(metadataBatchSchema),
    (req, res) => jobController.createMetadataBatchJob(req, res)
  );

  return router;
}