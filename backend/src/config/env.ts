import { z } from 'zod';

export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().transform(Number).default('3001'),
  PY_DIFFRHYTHM_URL: z.string().url().default('http://localhost:8001'),
  STORAGE_DIR: z.string().default('./storage'),
  DATABASE_PATH: z.string().default('./storage/database.sqlite'),
  FFMPEG_PATH: z.string().default('ffmpeg'),
  MAX_CONCURRENT_JOBS: z.string().transform(Number).default('3'),
  JOB_TIMEOUT: z.string().transform(Number).default('600'),
});

export type Env = z.infer<typeof envSchema>;

export function loadEnv(): Env {
  const result = envSchema.safeParse(process.env);
  
  if (!result.success) {
    console.error('❌ Invalid environment variables:', result.error.format());
    process.exit(1);
  }
  
  return result.data;
}