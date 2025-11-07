import { z } from 'zod';

// Job-related schemas
export const diffRhythmJobSchema = z.object({
  prompt: z.string().min(1, 'Prompt is required'),
  durationSeconds: z.number().min(10).max(300).optional(),
  language: z.enum(['ru', 'en']).optional(),
  genre: z.string().optional(),
  mood: z.string().optional(),
  tempo: z.number().optional(),
  seed: z.number().optional()
});

export const loopJobSchema = z.object({
  sourceUrl: z.string().url('Valid URL required'),
  startTime: z.number().optional(),
  endTime: z.number().optional(),
  fadeDuration: z.number().min(0).max(10).optional()
});

export const metadataBatchSchema = z.object({
  trackIds: z.array(z.string()).min(1, 'At least one track ID required'),
  metadata: z.object({
    title: z.string().optional(),
    artist: z.string().optional(),
    genre: z.string().optional(),
    mood: z.string().optional(),
    tempo: z.number().optional(),
    key: z.string().optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).optional()
  }).partial()
});

// Parameter schemas
export const jobIdSchema = z.object({
  id: z.string().uuid('Invalid job ID')
});

export const trackIdSchema = z.object({
  id: z.string().uuid('Invalid track ID')
});

// Pagination schema
export const paginationSchema = z.object({
  limit: z.string().transform(Number).refine(n => n >= 1 && n <= 100, 'Limit must be between 1 and 100').optional(),
  offset: z.string().transform(Number).refine(n => n >= 0, 'Offset must be non-negative').optional()
});