# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2025-11-09] - MusicGen/Transformers Migration

### Added
- **Transformers-based MusicGen implementation** using `MusicgenForConditionalGeneration` from transformers library
- **Cross-platform support** - Works on Windows, macOS, and Linux without system dependencies
- **Multiple model sizes** - Small (300MB), Medium (1.5GB), and Large (3GB) models
- **Simplified dependencies** - Only requires transformers, torch, and basic audio libraries
- **AutoProcessor integration** for tokenization and audio processing
- **Device selection** - CPU and CUDA support with automatic configuration
- **Model preload functionality** for faster first-request latency
- **Structured logging** for model loading and generation process
- **Enhanced error handling** with detailed logging and graceful failures

### Changed
- **Replaced audiocraft with transformers** - Complete migration from audiocraft to transformers library
- **Updated audio export** - Now uses soundfile for WAV and pydub for MP3 conversion
- **Sample rate standardized** - Fixed at 32kHz for all MusicGen models
- **Service initialization** - Added model size parameter and preload capability
- **Job type updated** - Changed from "diffrhythm" to "musicgen" in database records
- **Metadata enhancement** - Added model_size and sample_rate to track metadata

### Removed
- **audiocraft dependency** - No longer required for music generation
- **av dependency** - Removed audio/video processing library
- **ffmpeg requirement** - No system dependency needed for audio processing
- **librosa dependency** - Replaced with soundfile for audio operations
- **diffusers dependency** - Not needed for MusicGen implementation
- **accelerate dependency** - Simplified device handling without accelerate

### Fixed
- **Windows compatibility** - Resolved installation issues on Windows by removing system dependencies
- **Cross-platform audio processing** - Now works consistently across all operating systems
- **Simplified installation** - Reduced dependency conflicts and installation complexity
- **Memory management** - Better handling of model loading and unloading
- **Device detection** - Improved CPU/CUDA detection and configuration

### Technical Details
- **Model loading**: Uses `MusicgenForConditionalGeneration.from_pretrained()`
- **Tokenization**: Integrated `AutoProcessor` for text-to-audio conversion
- **Generation parameters**: Configurable guidance_scale, temperature, and max_new_tokens
- **Audio format**: 32kHz sample rate, mono output, WAV/MP3 export
- **Model sizes**: facebook/musicgen-small, facebook/musicgen-medium, facebook/musicgen-large

---

## Previous Versions

For changes prior to the transformers migration, please refer to the git history.