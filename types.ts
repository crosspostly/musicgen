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
}
