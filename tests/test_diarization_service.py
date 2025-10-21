"""
Unit tests for DiarizationService.

Tests speaker diarization functionality using pyannote.audio.
"""

import pytest
from pathlib import Path
import numpy as np

from src.services.diarization_service import DiarizationService


class TestDiarizationService:
    """Test cases for DiarizationService."""
    
    @pytest.fixture
    def service(self):
        """Create DiarizationService instance."""
        return DiarizationService(use_gpu=False)  # Use CPU for tests
    
    @pytest.fixture
    def sample_audio(self, tmp_path):
        """Create sample audio file for testing."""
        # TODO: Implement test audio file creation
        # For now, use fixture from fixtures/sample_audio.wav
        fixture_path = Path(__file__).parent / "fixtures" / "sample_audio.wav"
        if fixture_path.exists():
            return fixture_path
        pytest.skip("Sample audio fixture not available")
    
    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service is not None
        assert service.pipeline is not None
    
    def test_diarize_audio_file(self, service, sample_audio):
        """Test diarization of audio file."""
        # TODO: Implement when sample audio is available
        pytest.skip("Requires sample audio file")
        
        # segments = service.diarize(sample_audio)
        # assert isinstance(segments, list)
        # assert len(segments) > 0
        # assert 'start' in segments[0]
        # assert 'end' in segments[0]
        # assert 'speaker_label' in segments[0]
    
    def test_diarize_with_num_speakers(self, service, sample_audio):
        """Test diarization with specified number of speakers."""
        pytest.skip("Requires sample audio file")
        
        # segments = service.diarize(sample_audio, num_speakers=2)
        # speakers = set(seg['speaker_label'] for seg in segments)
        # assert len(speakers) == 2
    
    def test_get_speaker_statistics(self, service):
        """Test speaker statistics calculation."""
        segments = [
            {'start': 0.0, 'end': 1.0, 'speaker_label': 'SPEAKER_00', 'duration': 1.0},
            {'start': 1.5, 'end': 3.0, 'speaker_label': 'SPEAKER_00', 'duration': 1.5},
            {'start': 3.5, 'end': 4.5, 'speaker_label': 'SPEAKER_01', 'duration': 1.0},
        ]
        
        stats = service.get_speaker_statistics(segments)
        
        assert 'SPEAKER_00' in stats
        assert 'SPEAKER_01' in stats
        assert stats['SPEAKER_00']['total_duration'] == 2.5
        assert stats['SPEAKER_00']['segment_count'] == 2
        assert stats['SPEAKER_01']['total_duration'] == 1.0
        assert stats['SPEAKER_01']['segment_count'] == 1
    
    def test_merge_short_segments(self, service):
        """Test merging of short segments."""
        segments = [
            {'start': 0.0, 'end': 0.3, 'speaker_label': 'SPEAKER_00', 'duration': 0.3},
            {'start': 0.5, 'end': 2.0, 'speaker_label': 'SPEAKER_00', 'duration': 1.5},
            {'start': 2.5, 'end': 2.7, 'speaker_label': 'SPEAKER_00', 'duration': 0.2},
        ]
        
        merged = service.merge_short_segments(segments, min_duration=0.5)
        
        # Short segments should be merged with adjacent segments
        assert len(merged) < len(segments)
    
    def test_invalid_audio_file(self, service):
        """Test handling of invalid audio file."""
        with pytest.raises(Exception):
            service.diarize("nonexistent_file.wav")
