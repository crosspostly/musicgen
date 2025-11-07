export interface Job {
  id: string;
  type: 'diffrhythm' | 'loop' | 'metadata';
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-1
  result?: any;
  error?: string;
  createdAt: Date;
  updatedAt: Date;
  startedAt?: Date;
  completedAt?: Date;
}

export interface Track {
  id: string;
  jobId: string;
  model: string;
  duration: number;
  filePath: string;
  metadata: TrackMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export interface TrackMetadata {
  title?: string;
  artist?: string;
  genre?: string;
  tempo?: number;
  key?: string;
  description?: string;
  tags?: string[];
  [key: string]: any;
}

export interface DiffRhythmJobRequest {
  prompt: string;
  duration?: number;
  tempo?: number;
  seed?: number;
}

export interface LoopJobRequest {
  sourceUrl: string;
  startTime?: number;
  endTime?: number;
  fadeDuration?: number;
}

export interface MetadataBatchRequest {
  trackIds: string[];
  metadata: Partial<TrackMetadata>;
}