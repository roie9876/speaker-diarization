"""
Speaker Diarization Service using pyannote.audio.

Provides speaker diarization functionality to separate different speakers
in audio recordings and identify when each speaker is talking.
"""

import torch
from pyannote.audio import Pipeline
from pathlib import Path
from typing import List, Dict, Union, Optional
from src.config.config_manager import get_config
from src.utils.logger import get_logger
from src.utils.audio_utils import validate_audio_file

logger = get_logger(__name__)


class DiarizationService:
    """
    Service for speaker diarization using pyannote.audio.
    
    Separates audio into segments labeled by speaker.
    """
    
    def __init__(self, use_gpu: Optional[bool] = None):
        """
        Initialize diarization service.
        
        Args:
            use_gpu: Whether to use GPU. If None, uses config setting.
        """
        self.config = get_config()
        
        # Determine device
        if use_gpu is None:
            use_gpu = self.config.use_gpu
        
        self.device = self._get_device(use_gpu)
        logger.info(f"Diarization service using device: {self.device}")
        
        # Load pipeline
        self.pipeline = self._load_pipeline()
    
    def _get_device(self, use_gpu: bool) -> torch.device:
        """
        Determine the best available device.
        
        Args:
            use_gpu: Whether to try using GPU
        
        Returns:
            torch.device instance
        """
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
    
    def _load_pipeline(self) -> Pipeline:
        """
        Load pyannote.audio diarization pipeline.
        
        Returns:
            Loaded pipeline
        
        Raises:
            RuntimeError: If pipeline cannot be loaded
        """
        try:
            logger.info("Loading pyannote.audio diarization pipeline...")
            
            # Load pipeline from Hugging Face
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.config.huggingface_token
            )
            
            # Move to device
            pipeline.to(self.device)
            
            logger.info("Diarization pipeline loaded successfully")
            return pipeline
            
        except Exception as e:
            logger.error(f"Failed to load diarization pipeline: {e}")
            raise RuntimeError(
                f"Cannot load diarization pipeline. "
                f"Make sure you have accepted the user agreements at: "
                f"https://huggingface.co/pyannote/speaker-diarization-3.1 "
                f"and https://huggingface.co/pyannote/segmentation-3.0. "
                f"Error: {e}"
            )
    
    def diarize(
        self,
        audio_file: Union[str, Path],
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None
    ) -> List[Dict]:
        """
        Perform speaker diarization on audio file.
        
        Args:
            audio_file: Path to audio file
            num_speakers: Exact number of speakers (if known)
            min_speakers: Minimum number of speakers
            max_speakers: Maximum number of speakers
        
        Returns:
            List of diarization segments, each containing:
                - 'start': Start time in seconds
                - 'end': End time in seconds
                - 'speaker_label': Speaker identifier (e.g., "SPEAKER_00")
                - 'duration': Segment duration in seconds
        
        Raises:
            ValueError: If audio file is invalid
            RuntimeError: If diarization fails
        """
        audio_file = Path(audio_file)
        
        # Validate audio file
        if not validate_audio_file(audio_file):
            raise ValueError(f"Invalid audio file: {audio_file}")
        
        logger.info(f"Starting diarization for: {audio_file.name}")
        
        try:
            # Prepare parameters
            params = {}
            if num_speakers is not None:
                params["num_speakers"] = num_speakers
            if min_speakers is not None:
                params["min_speakers"] = min_speakers
            if max_speakers is not None:
                params["max_speakers"] = max_speakers
            
            # Run diarization
            diarization = self.pipeline(str(audio_file), **params)
            
            # Convert to list of dictionaries
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segment = {
                    "start": turn.start,
                    "end": turn.end,
                    "speaker_label": speaker,
                    "duration": turn.end - turn.start
                }
                segments.append(segment)
            
            # Log summary
            unique_speakers = len(set(seg["speaker_label"] for seg in segments))
            total_duration = sum(seg["duration"] for seg in segments)
            
            logger.info(
                f"Diarization complete: {len(segments)} segments, "
                f"{unique_speakers} speakers, "
                f"{total_duration:.1f}s total speech"
            )
            
            return segments
            
        except Exception as e:
            logger.error(f"Diarization failed for {audio_file.name}: {e}")
            raise RuntimeError(f"Diarization failed: {e}")
    
    def get_speaker_statistics(self, segments: List[Dict]) -> Dict[str, Dict]:
        """
        Calculate statistics for each speaker from diarization segments.
        
        Args:
            segments: List of diarization segments
        
        Returns:
            Dictionary mapping speaker_label to statistics:
                - 'total_duration': Total speaking time in seconds
                - 'num_segments': Number of speaking segments
                - 'avg_segment_duration': Average segment duration
                - 'percentage': Percentage of total speech time
        """
        if not segments:
            return {}
        
        speaker_stats = {}
        total_duration = sum(seg["duration"] for seg in segments)
        
        for segment in segments:
            speaker = segment["speaker_label"]
            
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    "total_duration": 0.0,
                    "num_segments": 0,
                    "segments": []
                }
            
            speaker_stats[speaker]["total_duration"] += segment["duration"]
            speaker_stats[speaker]["num_segments"] += 1
            speaker_stats[speaker]["segments"].append(segment)
        
        # Calculate derived statistics
        for speaker, stats in speaker_stats.items():
            stats["avg_segment_duration"] = (
                stats["total_duration"] / stats["num_segments"]
            )
            stats["percentage"] = (
                stats["total_duration"] / total_duration * 100
                if total_duration > 0 else 0
            )
            # Remove segments list from final output (too verbose)
            del stats["segments"]
        
        return speaker_stats
    
    def merge_short_segments(
        self,
        segments: List[Dict],
        min_duration: float = 0.5
    ) -> List[Dict]:
        """
        Merge segments shorter than minimum duration with adjacent segments.
        
        Args:
            segments: List of diarization segments
            min_duration: Minimum segment duration in seconds
        
        Returns:
            List of merged segments
        """
        if not segments:
            return []
        
        merged = []
        current = segments[0].copy()
        
        for segment in segments[1:]:
            if current["duration"] < min_duration and \
               segment["speaker_label"] == current["speaker_label"]:
                # Merge with current
                current["end"] = segment["end"]
                current["duration"] = current["end"] - current["start"]
            else:
                merged.append(current)
                current = segment.copy()
        
        merged.append(current)
        
        logger.debug(
            f"Merged segments: {len(segments)} -> {len(merged)} "
            f"(min_duration={min_duration}s)"
        )
        
        return merged
