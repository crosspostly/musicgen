// Fix: Create and export enums and interfaces to be used across the application.
export enum GenerationModel {
  MUSICGEN = 'MusicGen',
  BARK = 'Bark',
}

export enum Screen {
  MODEL_SELECTION = 'ModelSelection',
  MUSICGEN_GENERATOR = 'MusicGenGenerator',
  BARK_GENERATOR = 'BarkGenerator',
  METADATA_EDITOR = 'MetadataEditor',
  EXPORT = 'Export',
  FREESTYLE = 'Freestyle',
}

export interface MusicGenParams {
  prompt: string;
  duration: number;              // 5-60 сек (default: 30)
  guidance_scale?: number;       // 1.0-15.0 (default: 3.0)
  temperature?: number;          // 0.1-2.0 (default: 1.0)
  top_k?: number;                // 50-500 (default: 250)
  top_p?: number;                // 0.0-1.0 (default: 0.9)
}

export interface BarkParams {
  text: string;                  // макс ~150 символов
  voice_preset: string;          // "v2/[lang]_speaker_[0-9]"
  language?: string;             // "ru", "en", "de", "es", etc
  text_temp?: number;            // 0.7 (default)
  waveform_temp?: number;        // 0.7 (default)
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
