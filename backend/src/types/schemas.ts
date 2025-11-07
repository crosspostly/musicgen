import { z } from 'zod';

export const diffRhythmJobSchema = z.object({
  prompt: z.string().min(1, 'Prompt is required').max(1000, 'Prompt too long'),
  duration: z.number().min(1).max(300).optional(),
  tempo: z.number().min(60).max(200).optional(),
  seed: z.number().int().min(0).max(4294967295).optional(),
});

export const loopJobSchema = z.object({
  sourceUrl: z.string().url('Valid URL required'),
  startTime: z.number().min(0).optional(),
  endTime: z.number().min(0).optional(),
  fadeDuration: z.number().min(0).max(10).optional(),
});

export const metadataBatchSchema = z.object({
  trackIds: z.array(z.string().uuid()).min(1, 'At least one track ID required'),
  metadata: z.object({
    title: z.string().max(200).optional(),
    artist: z.string().max(200).optional(),
    genre: z.string().max(100).optional(),
    tempo: z.number().min(60).max(200).optional(),
    key: z.string().max(10).optional(),
    description: z.string().max(1000).optional(),
    tags: z.array(z.string().max(50)).optional(),
  }).passthrough(),
});

export const jobIdSchema = z.object({
  id: z.string().uuid('Invalid job ID format'),
});

export const trackIdSchema = z.object({
  id: z.string().uuid('Invalid track ID format'),
});

export const paginationSchema = z.object({
  limit: z.coerce.number().min(1).max(100).default(20),
  offset: z.coerce.number().min(0).default(0),
});

export type DiffRhythmJobRequest = z.infer<typeof diffRhythmJobSchema>;
export type LoopJobRequest = z.infer<typeof loopJobSchema>;
export type MetadataBatchRequest = z.infer<typeof metadataBatchSchema>;
export type JobIdParams = z.infer<typeof jobIdSchema>;
export type TrackIdParams = z.infer<typeof trackIdSchema>;
export type PaginationQuery = z.infer<typeof paginationSchema>;