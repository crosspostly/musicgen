// Fix: Create and export enums and interfaces to be used across the application.
export enum GenerationModel {
  DIFFRHYTHM = 'DiffRhythm',
  YUE = 'YuE',
  BARK = 'Bark',
  LYRIA = 'Lyria',
  MAGNET = 'MAGNeT',
}

export enum Screen {
  MODEL_SELECTION = 'ModelSelection',
  DIFFRHYTHM_GENERATOR = 'DiffRhythmGenerator',
  YUE_GENERATOR = 'YueGenerator',
  BARK_GENERATOR = 'BarkGenerator',
  LYRIA_GENERATOR = 'LyriaGenerator',
  MAGNET_GENERATOR = 'MagnetGenerator',
  METADATA_EDITOR = 'MetadataEditor',
  EXPORT = 'Export',
  FREESTYLE = 'Freestyle',
}

export interface ExportFile {
  format: 'mp3' | 'wav';
  fileUrl: string;
  filePath?: string;
  fileSize?: number; // in bytes
  duration: number; // in seconds
}

export interface GeneratedTrack {
  id: string;
  name: string;
  model: GenerationModel;
  audioUrl: string;
  duration: number; // in seconds
  createdAt: Date;
  metadata?: {
    artist?: string;
    album?: string;
    genre?: string;
  };
  exports?: ExportFile[];
}

export enum LoopJobStatus {
  PENDING = 'pending',
  ANALYZING = 'analyzing',
  RENDERING = 'rendering',
  EXPORTING = 'exporting',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface LoopJob {
  id: string;
  trackId: string;
  status: LoopJobStatus;
  duration: number; // in seconds
  fadeInOut: boolean;
  format: 'mp3' | 'wav';
  progress: number; // 0-100
  error?: string;
  resultUrl?: string;
  resultPath?: string;
  createdAt: Date;
  completedAt?: Date;
}
