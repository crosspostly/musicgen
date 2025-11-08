"""
Integration test for audio export functionality
Tests that WAV and MP3 artifacts are generated correctly
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import soundfile as sf
from pydub import AudioSegment


class AudioExporter:
    """Simple audio exporter for testing WAV/MP3 generation"""
    
    @staticmethod
    def generate_test_audio(duration_seconds: float = 1.0, sample_rate: int = 44100) -> np.ndarray:
        """Generate a simple sine wave test audio"""
        t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
        frequency = 440  # A4 note
        audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        return audio
    
    @staticmethod
    def export_wav(audio_data: np.ndarray, output_path: str, sample_rate: int = 44100) -> None:
        """Export audio data to WAV format"""
        sf.write(output_path, audio_data, sample_rate)
    
    @staticmethod
    def export_mp3(audio_data: np.ndarray, output_path: str, sample_rate: int = 44100) -> None:
        """Export audio data to MP3 format"""
        # First save as WAV temporarily
        temp_wav = output_path.replace('.mp3', '_temp.wav')
        sf.write(temp_wav, audio_data, sample_rate)
        
        # Convert WAV to MP3 using pydub
        audio = AudioSegment.from_wav(temp_wav)
        audio.export(output_path, format="mp3", bitrate="192k")
        
        # Clean up temp WAV
        os.remove(temp_wav)


@pytest.fixture
def audio_exporter():
    """Provide AudioExporter instance"""
    return AudioExporter()


@pytest.fixture
def test_audio_dir():
    """Create a temporary directory for test artifacts"""
    test_dir = Path(__file__).parent / 'artifacts'
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup is optional - artifacts can be inspected


class TestAudioExport:
    """Test audio export functionality"""
    
    def test_generate_test_audio(self, audio_exporter):
        """Test that we can generate test audio data"""
        audio = audio_exporter.generate_test_audio(duration_seconds=1.0)
        
        assert audio is not None
        assert len(audio) > 0
        assert audio.dtype == np.float32
        # Check amplitude is reasonable (sine wave bounded by [-1, 1])
        assert np.max(np.abs(audio)) <= 1.0
    
    def test_export_wav_file(self, audio_exporter, test_audio_dir):
        """Test that WAV files are created with non-zero size"""
        audio = audio_exporter.generate_test_audio(duration_seconds=2.0)
        output_path = test_audio_dir / 'test_output.wav'
        
        audio_exporter.export_wav(audio, str(output_path), sample_rate=44100)
        
        # Verify file exists
        assert output_path.exists(), f"WAV file not created at {output_path}"
        
        # Verify file has content
        file_size = output_path.stat().st_size
        assert file_size > 0, f"WAV file is empty: {file_size} bytes"
        
        # Verify we can read it back
        read_audio, sr = sf.read(str(output_path))
        assert len(read_audio) > 0
        assert sr == 44100
    
    def test_export_mp3_file(self, audio_exporter, test_audio_dir):
        """Test that MP3 files are created with non-zero size"""
        audio = audio_exporter.generate_test_audio(duration_seconds=2.0)
        output_path = test_audio_dir / 'test_output.mp3'
        
        audio_exporter.export_mp3(audio, str(output_path), sample_rate=44100)
        
        # Verify file exists
        assert output_path.exists(), f"MP3 file not created at {output_path}"
        
        # Verify file has content
        file_size = output_path.stat().st_size
        assert file_size > 0, f"MP3 file is empty: {file_size} bytes"
        
        # Verify it's a valid MP3 by checking magic bytes
        with open(output_path, 'rb') as f:
            magic = f.read(3)
            # MP3 files start with "ID3" or "FF FB" or "FF FA"
            assert magic[:2] == b'ID' or magic[0] == 0xFF, "Invalid MP3 magic bytes"
    
    def test_export_both_formats(self, audio_exporter, test_audio_dir):
        """Test exporting the same audio in both WAV and MP3 formats"""
        audio = audio_exporter.generate_test_audio(duration_seconds=1.5)
        
        wav_path = test_audio_dir / 'test_both_formats.wav'
        mp3_path = test_audio_dir / 'test_both_formats.mp3'
        
        # Export both formats
        audio_exporter.export_wav(audio, str(wav_path), sample_rate=44100)
        audio_exporter.export_mp3(audio, str(mp3_path), sample_rate=44100)
        
        # Verify both files exist
        assert wav_path.exists(), f"WAV file not created: {wav_path}"
        assert mp3_path.exists(), f"MP3 file not created: {mp3_path}"
        
        # Verify both have content
        wav_size = wav_path.stat().st_size
        mp3_size = mp3_path.stat().st_size
        
        assert wav_size > 0, f"WAV file is empty"
        assert mp3_size > 0, f"MP3 file is empty"
        
        # MP3 should typically be smaller than WAV due to compression
        # but we just verify both exist and have reasonable sizes
        assert wav_size > 100, "WAV file seems too small"
        assert mp3_size > 100, "MP3 file seems too small"
    
    def test_artifacts_directory_created(self, test_audio_dir):
        """Test that artifacts directory is created"""
        assert test_audio_dir.exists(), f"Artifacts directory not created: {test_audio_dir}"
        assert test_audio_dir.is_dir(), f"Artifacts path is not a directory: {test_audio_dir}"
    
    def test_multiple_exports(self, audio_exporter, test_audio_dir):
        """Test multiple sequential exports"""
        for i in range(3):
            audio = audio_exporter.generate_test_audio(duration_seconds=1.0)
            
            wav_path = test_audio_dir / f'test_multi_{i}.wav'
            mp3_path = test_audio_dir / f'test_multi_{i}.mp3'
            
            audio_exporter.export_wav(audio, str(wav_path))
            audio_exporter.export_mp3(audio, str(mp3_path))
            
            assert wav_path.exists()
            assert mp3_path.exists()
            assert wav_path.stat().st_size > 0
            assert mp3_path.stat().st_size > 0


class TestAudioProperties:
    """Test audio file properties"""
    
    def test_wav_duration(self, audio_exporter, test_audio_dir):
        """Test that WAV file duration matches input"""
        duration_seconds = 3.0
        audio = audio_exporter.generate_test_audio(duration_seconds=duration_seconds)
        output_path = test_audio_dir / 'test_duration.wav'
        
        audio_exporter.export_wav(audio, str(output_path), sample_rate=44100)
        
        # Read back and verify duration
        read_audio, sr = sf.read(str(output_path))
        actual_duration = len(read_audio) / sr
        
        # Allow small tolerance due to float arithmetic
        assert abs(actual_duration - duration_seconds) < 0.01
    
    def test_wav_sample_rate(self, audio_exporter, test_audio_dir):
        """Test that WAV file preserves sample rate"""
        audio = audio_exporter.generate_test_audio(duration_seconds=1.0)
        output_path = test_audio_dir / 'test_sample_rate.wav'
        sample_rate = 48000
        
        audio_exporter.export_wav(audio, str(output_path), sample_rate=sample_rate)
        
        # Read back and verify sample rate
        _, sr = sf.read(str(output_path))
        assert sr == sample_rate


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
