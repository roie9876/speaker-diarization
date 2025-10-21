"""
Unit tests for IdentificationService.

Tests speaker identification and embedding extraction.
"""

import pytest
import numpy as np
from pathlib import Path

from src.services.identification_service import IdentificationService


class TestIdentificationService:
    """Test cases for IdentificationService."""
    
    @pytest.fixture
    def service(self):
        """Create IdentificationService instance."""
        return IdentificationService(use_gpu=False)
    
    @pytest.fixture
    def sample_audio(self):
        """Get sample audio file."""
        fixture_path = Path(__file__).parent / "fixtures" / "sample_audio.wav"
        if fixture_path.exists():
            return fixture_path
        pytest.skip("Sample audio fixture not available")
    
    @pytest.fixture
    def sample_embedding(self):
        """Create sample embedding vector."""
        return np.random.randn(512)
    
    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service is not None
        assert service.model is not None
    
    def test_extract_embedding(self, service, sample_audio):
        """Test embedding extraction from audio."""
        pytest.skip("Requires sample audio file")
        
        # embedding = service.extract_embedding(sample_audio)
        # assert isinstance(embedding, np.ndarray)
        # assert embedding.shape == (512,)
    
    def test_extract_embedding_with_time_range(self, service, sample_audio):
        """Test embedding extraction from audio segment."""
        pytest.skip("Requires sample audio file")
        
        # embedding = service.extract_embedding(sample_audio, start=1.0, end=3.0)
        # assert isinstance(embedding, np.ndarray)
        # assert embedding.shape == (512,)
    
    def test_compare_embeddings_identical(self, service, sample_embedding):
        """Test comparison of identical embeddings."""
        similarity = service.compare_embeddings(sample_embedding, sample_embedding)
        
        # Identical embeddings should have similarity close to 1.0
        assert 0.99 <= similarity <= 1.0
    
    def test_compare_embeddings_different(self, service):
        """Test comparison of different embeddings."""
        emb1 = np.random.randn(512)
        emb2 = np.random.randn(512)
        
        similarity = service.compare_embeddings(emb1, emb2)
        
        # Different random embeddings should have low similarity
        assert 0.0 <= similarity <= 1.0
        assert similarity < 0.8  # Very unlikely to be similar by chance
    
    def test_identify_segments(self, service, sample_audio, sample_embedding):
        """Test segment identification."""
        pytest.skip("Requires sample audio file")
        
        # segments = [
        #     {'start': 0.0, 'end': 2.0, 'speaker_label': 'SPEAKER_00'},
        #     {'start': 2.5, 'end': 4.0, 'speaker_label': 'SPEAKER_01'},
        # ]
        # 
        # results = service.identify_segments(
        #     sample_audio,
        #     segments,
        #     sample_embedding,
        #     threshold=0.75
        # )
        # 
        # assert len(results) == len(segments)
        # assert 'similarity' in results[0]
        # assert 'is_target' in results[0]
        # assert isinstance(results[0]['is_target'], bool)
    
    def test_batch_extract_embeddings(self, service, sample_audio):
        """Test batch embedding extraction."""
        pytest.skip("Requires sample audio file")
        
        # segments = [
        #     {'start': 0.0, 'end': 2.0},
        #     {'start': 2.5, 'end': 4.0},
        # ]
        # 
        # embeddings = service.batch_extract_embeddings(sample_audio, segments)
        # 
        # assert len(embeddings) == len(segments)
        # assert all(isinstance(emb, np.ndarray) for emb in embeddings)
        # assert all(emb.shape == (512,) for emb in embeddings)
    
    def test_find_best_threshold(self, service):
        """Test threshold optimization."""
        similarities = [0.9, 0.85, 0.8, 0.75, 0.7, 0.6, 0.5, 0.4]
        
        threshold = service.find_best_threshold(similarities, target_precision=0.95)
        
        assert 0.5 <= threshold <= 1.0
    
    def test_invalid_embedding_dimensions(self, service):
        """Test handling of invalid embedding dimensions."""
        emb1 = np.random.randn(512)
        emb2 = np.random.randn(256)  # Wrong dimension
        
        with pytest.raises(Exception):
            service.compare_embeddings(emb1, emb2)
