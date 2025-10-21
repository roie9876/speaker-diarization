"""
Speaker Identification Service using pyannote.audio embeddings.

Provides speaker embedding extraction and comparison for identifying
specific speakers in audio recordings.
"""

import torch
import numpy as np
from pyannote.audio import Inference, Model
from pathlib import Path
from typing import List, Dict, Union, Optional, Tuple
from scipy.spatial.distance import cosine
from src.config.config_manager import get_config
from src.utils.logger import get_logger
from src.utils.audio_utils import validate_audio_file, extract_segment, load_audio

logger = get_logger(__name__)


class IdentificationService:
    """
    Service for speaker identification using embeddings.
    
    Extracts speaker embeddings and compares them to identify specific speakers.
    """
    
    def __init__(self, use_gpu: Optional[bool] = None):
        """
        Initialize identification service.
        
        Args:
            use_gpu: Whether to use GPU. If None, uses config setting.
        """
        self.config = get_config()
        
        # Determine device
        if use_gpu is None:
            use_gpu = self.config.use_gpu
        
        self.device = self._get_device(use_gpu)
        logger.info(f"Identification service using device: {self.device}")
        
        # Load embedding model
        self.inference = self._load_embedding_model()
    
    def _get_device(self, use_gpu: bool) -> torch.device:
        """Determine the best available device."""
        if use_gpu:
            if torch.backends.mps.is_available():
                logger.info("MPS (Apple Silicon GPU) available")
                return torch.device("mps")
            elif torch.cuda.is_available():
                logger.info("CUDA GPU available")
                return torch.device("cuda")
            else:
                logger.warning("GPU requested but not available, using CPU")
                return torch.device("cpu")
        else:
            return torch.device("cpu")
    
    def _load_embedding_model(self) -> Inference:
        """
        Load pyannote.audio embedding model.
        
        Returns:
            Loaded inference model
        
        Raises:
            RuntimeError: If model cannot be loaded
        """
        try:
            logger.info("Loading pyannote.audio embedding model...")
            
            # Load the model from HuggingFace (pyannote.audio 4.0+ API)
            model = Model.from_pretrained(
                "pyannote/embedding",
                token=self.config.huggingface_token
            )
            
            # Create inference object with the loaded model
            inference = Inference(model, device=self.device)
            
            logger.info("Embedding model loaded successfully")
            return inference
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(
                f"Cannot load embedding model. "
                f"Make sure you have accepted the user agreements at: "
                f"https://huggingface.co/pyannote/embedding. "
                f"Error: {e}"
            )
    
    def extract_embedding(
        self,
        audio_file: Union[str, Path],
        start: Optional[float] = None,
        end: Optional[float] = None
    ) -> np.ndarray:
        """
        Extract speaker embedding from audio file or segment.
        
        Args:
            audio_file: Path to audio file
            start: Optional start time in seconds (if extracting segment)
            end: Optional end time in seconds (if extracting segment)
        
        Returns:
            512-dimensional embedding vector as numpy array
        
        Raises:
            ValueError: If audio file is invalid
            RuntimeError: If embedding extraction fails
        """
        audio_file = Path(audio_file)
        
        # Validate audio file
        if not validate_audio_file(audio_file):
            raise ValueError(f"Invalid audio file: {audio_file}")
        
        try:
            # Create segment dict for inference
            if start is not None and end is not None:
                segment = {"start": start, "end": end}
                logger.debug(
                    f"Extracting embedding from {audio_file.name} "
                    f"[{start:.2f}s - {end:.2f}s]"
                )
            else:
                segment = None
                logger.debug(f"Extracting embedding from entire file: {audio_file.name}")
            
            # Extract embedding
            embedding = self.inference({
                "audio": str(audio_file),
                "segment": segment
            })
            
            # Convert to numpy array
            embedding_array = np.array(embedding)
            
            # Handle different embedding shapes
            if embedding_array.ndim > 1:
                # If shape is (1, 512), flatten to (512,)
                if embedding_array.shape[0] == 1:
                    embedding_array = embedding_array.flatten()
                    logger.debug(f"Flattened embedding from (1, 512) to {embedding_array.shape}")
                # If shape is (N, 512) where N > 1 (multiple frames), average them
                elif embedding_array.shape[1] == 512:
                    num_frames = embedding_array.shape[0]
                    embedding_array = np.mean(embedding_array, axis=0)
                    logger.debug(f"Averaged {num_frames} frame embeddings to single (512,) embedding")
                # Otherwise just flatten (shouldn't happen)
                else:
                    embedding_array = embedding_array.flatten()
                    logger.warning(f"Unexpected embedding shape, flattened to {embedding_array.shape}")
            
            # ALWAYS normalize embeddings (L2 normalization) for consistent comparison
            # This is critical - pyannote embeddings need normalization
            norm_before = np.linalg.norm(embedding_array)
            if norm_before > 0:
                embedding_array = embedding_array / norm_before
                norm_after = np.linalg.norm(embedding_array)
                logger.debug(f"Normalized embedding (L2 norm before: {norm_before:.2f}, after: {norm_after:.3f})")
            
            logger.debug(f"Final embedding shape: {embedding_array.shape}, range: [{embedding_array.min():.3f}, {embedding_array.max():.3f}]")
            
            return embedding_array
            
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
            raise RuntimeError(f"Cannot extract embedding: {e}")
    
    def compare_embeddings(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compare two embeddings and return similarity score.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score between 0.0 and 1.0 (higher is more similar)
            Calculated as 1 - cosine_distance
        """
        try:
            # Ensure both embeddings are 1-D
            if embedding1.ndim > 1:
                embedding1 = embedding1.flatten()
            if embedding2.ndim > 1:
                embedding2 = embedding2.flatten()
            
            # Ensure both have same shape
            if embedding1.shape != embedding2.shape:
                logger.error(f"Embedding shape mismatch: {embedding1.shape} vs {embedding2.shape}")
                return 0.0
            
            # Calculate cosine similarity
            # cosine distance is 1 - cosine similarity
            # We return similarity, so: 1 - cosine_distance = cosine_similarity
            distance = cosine(embedding1, embedding2)
            similarity = 1 - distance
            
            logger.debug(f"Embedding similarity: {similarity:.4f}")
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Embedding comparison failed: {e}")
            logger.debug(f"Embedding1 shape: {embedding1.shape if hasattr(embedding1, 'shape') else 'N/A'}")
            logger.debug(f"Embedding2 shape: {embedding2.shape if hasattr(embedding2, 'shape') else 'N/A'}")
            return 0.0
    
    def identify_segments(
        self,
        audio_file: Union[str, Path],
        segments: List[Dict],
        target_embedding: np.ndarray,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Identify which segments contain the target speaker.
        
        Args:
            audio_file: Path to audio file
            segments: List of diarization segments
            target_embedding: Target speaker embedding to match against
            threshold: Similarity threshold (uses config default if None)
        
        Returns:
            List of segments with added fields:
                - 'embedding': Segment embedding vector
                - 'similarity': Similarity score to target
                - 'is_target': Boolean indicating if segment matches target
        
        Raises:
            ValueError: If audio file is invalid
        """
        if threshold is None:
            threshold = self.config.similarity_threshold
        
        audio_file = Path(audio_file)
        
        logger.info(
            f"Identifying target speaker in {len(segments)} segments "
            f"(threshold={threshold:.2f})"
        )
        
        identified_segments = []
        matches = 0
        
        for i, segment in enumerate(segments):
            try:
                # Extract embedding for this segment
                embedding = self.extract_embedding(
                    audio_file,
                    start=segment["start"],
                    end=segment["end"]
                )
                
                # Compare with target
                similarity = self.compare_embeddings(embedding, target_embedding)
                
                # Create enriched segment
                enriched = segment.copy()
                enriched["embedding"] = embedding
                enriched["similarity"] = similarity
                enriched["is_target"] = similarity >= threshold
                
                identified_segments.append(enriched)
                
                if enriched["is_target"]:
                    matches += 1
                    logger.debug(
                        f"Segment {i+1}/{len(segments)}: MATCH "
                        f"({similarity:.3f} >= {threshold:.3f})"
                    )
                else:
                    logger.debug(
                        f"Segment {i+1}/{len(segments)}: no match "
                        f"({similarity:.3f} < {threshold:.3f})"
                    )
                
            except Exception as e:
                logger.warning(f"Failed to process segment {i+1}: {e}")
                # Add segment without identification
                enriched = segment.copy()
                enriched["embedding"] = None
                enriched["similarity"] = 0.0
                enriched["is_target"] = False
                identified_segments.append(enriched)
        
        # Log summary
        match_duration = sum(
            seg["duration"] for seg in identified_segments if seg["is_target"]
        )
        total_duration = sum(seg["duration"] for seg in identified_segments)
        
        logger.info(
            f"Identification complete: {matches}/{len(segments)} segments matched "
            f"({match_duration:.1f}s / {total_duration:.1f}s)"
        )
        
        return identified_segments
    
    def find_best_threshold(
        self,
        similarities: List[float],
        target_precision: float = 0.9
    ) -> float:
        """
        Find optimal threshold for speaker identification.
        
        Args:
            similarities: List of similarity scores
            target_precision: Desired precision level (0.0-1.0)
        
        Returns:
            Suggested threshold value
        """
        if not similarities:
            return self.config.similarity_threshold
        
        sorted_sims = sorted(similarities, reverse=True)
        
        # Find threshold at target precision
        idx = int(len(sorted_sims) * target_precision)
        threshold = sorted_sims[min(idx, len(sorted_sims) - 1)]
        
        logger.info(
            f"Suggested threshold: {threshold:.3f} "
            f"(precision={target_precision:.0%})"
        )
        
        return threshold
    
    def batch_extract_embeddings(
        self,
        audio_file: Union[str, Path],
        segments: List[Dict]
    ) -> List[np.ndarray]:
        """
        Extract embeddings for multiple segments efficiently.
        
        Args:
            audio_file: Path to audio file
            segments: List of segments with 'start' and 'end' times
        
        Returns:
            List of embedding vectors
        """
        logger.info(f"Batch extracting {len(segments)} embeddings...")
        
        embeddings = []
        for i, segment in enumerate(segments):
            try:
                embedding = self.extract_embedding(
                    audio_file,
                    start=segment["start"],
                    end=segment["end"]
                )
                embeddings.append(embedding)
                
                if (i + 1) % 10 == 0:
                    logger.debug(f"Extracted {i+1}/{len(segments)} embeddings")
                    
            except Exception as e:
                logger.warning(f"Failed to extract embedding {i+1}: {e}")
                embeddings.append(None)
        
        logger.info(f"Batch extraction complete: {len(embeddings)} embeddings")
        
        return embeddings
