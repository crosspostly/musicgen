# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-XX

### BREAKING CHANGES
- Removed all fake models (DiffRhythm, YuE, Lyria, MAGNeT)
- Renamed `DIFFRHYTHM` model to `MUSICGEN` in frontend types
- Updated API endpoints to use MusicGen-specific parameters
- Changed generation API request/response format

### ADDED
- Real MusicGen model integration (facebook/musicgen-small)
- Full parameter support for MusicGen:
  - `guidance_scale` (1.0-15.0, default: 3.0)
  - `temperature` (0.1-2.0, default: 1.0)
  - `top_k` (50-500, default: 250)
  - `top_p` (0.0-1.0, default: 0.9)
- Bark model preparation with Russian voice presets
- New TypeScript interfaces:
  - `MusicGenParams` for MusicGen parameters
  - `BarkParams` for Bark parameters
- Enhanced UI with parameter sliders and real-time validation
- Russian language support for Bark voices (v2/ru_speaker_0-7)
- Improved model selection screen with accurate information

### CHANGED
- Renamed `DiffRhythmService` to `MusicGenService`
- Updated Python backend to use transformers instead of diffusers
- Migrated from DiffRhythm (ASLP-lab) to MusicGen (Meta) model
- Updated frontend to show only real models (MusicGen + Bark)
- Improved generation time estimates based on actual model performance
- Enhanced error handling and user feedback

### REMOVED
- `DiffRhythmGeneratorScreen.tsx` - replaced with `MusicGenGeneratorScreen.tsx`
- `YueGeneratorScreen.tsx` - fake model removed
- `LyriaGeneratorScreen.tsx` - fake model removed
- `MagnetGeneratorScreen.tsx` - fake model removed
- All fake model references from types and enums
- Legacy DiffRhythm service and API endpoints

### FIXED
- Corrected model size information (300MB for MusicGen)
- Fixed parameter validation ranges
- Improved audio export functionality
- Enhanced CORS configuration for local development

### DEPRECATED
- Old generation API format (still supported for backward compatibility)
- Fake model endpoints (will be removed in future versions)

## [1.0.0] - 2024-01-XX

### ADDED
- Initial release with fake models
- Basic generation API
- Audio export functionality
- Database persistence
- Frontend UI with model selection

---

## Migration Guide from 1.x to 2.0

### Frontend Changes
```typescript
// OLD
GenerationModel.DIFFRHYTHM
Screen.DIFFRHYTHM_GENERATOR

// NEW
GenerationModel.MUSICGEN
Screen.MUSICGEN_GENERATOR
```

### API Changes
```python
# OLD API request
{
  "prompt": "lo-fi hip hop",
  "duration": 30
}

# NEW API request
{
  "prompt": "lo-fi hip hop",
  "duration": 30,
  "guidance_scale": 3.0,
  "temperature": 1.0,
  "top_k": 250,
  "top_p": 0.9
}
```

### Backend Changes
```python
# OLD
from .services.diffrhythm import DiffRhythmService
service = DiffRhythmService()

# NEW
from .services.musicgen_service import MusicGenService
service = MusicGenService()
```

### Model Information
- **MusicGen**: Real Meta model, 300MB, instrumental music only
- **Bark**: Real Suno AI model, 1.2GB, speech and vocals
- All fake models have been removed