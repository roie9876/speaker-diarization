"""
Audio utilities for Speaker Diarization System.

Provides functions for audio file validation, format conversion, and processing.
"""

import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Union
from src.utils.logger import get_logger

logger = get_logger(__name__)


def validate_audio_file(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file is a supported audio file.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        True if file is valid audio, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        # Check file extension
        supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg']
        if file_path.suffix.lower() not in supported_formats:
            logger.error(f"Unsupported format: {file_path.suffix}")
            return False
        
        # Try to load audio info
        info = sf.info(str(file_path))
        
        # Check minimum duration (1 second)
        if info.duration < 1.0:
            logger.error(f"Audio too short: {info.duration}s (minimum 1s required)")
            return False
        
        logger.debug(f"Valid audio file: {file_path} ({info.duration:.1f}s, {info.samplerate}Hz)")
        return True
        
    except Exception as e:
        logger.error(f"Error validating audio file {file_path}: {e}")
        return False


def load_audio(
    file_path: Union[str, Path],
    sample_rate: int = 16000,
    mono: bool = True
) -> Tuple[np.ndarray, int]:
    """
    Load audio file and optionally resample/convert to mono.
    
    Args:
        file_path: Path to audio file
        sample_rate: Target sample rate (Hz). If None, uses original rate.
        mono: Convert to mono if True
    
    Returns:
        Tuple of (audio_data, sample_rate)
        audio_data is numpy array of shape (n_samples,) for mono or (n_channels, n_samples)
    
    Raises:
        ValueError: If file cannot be loaded
    """
    try:
        file_path = Path(file_path)
        
        # Load audio
        audio, sr = librosa.load(
            str(file_path),
            sr=sample_rate,
            mono=mono
        )
        
        logger.debug(
            f"Loaded audio: {file_path.name} "
            f"({len(audio)/sr:.1f}s, {sr}Hz, "
            f"{'mono' if mono else 'stereo'})"
        )
        
        return audio, sr
        
    except Exception as e:
        logger.error(f"Error loading audio file {file_path}: {e}")
        raise ValueError(f"Cannot load audio file: {e}")


def save_audio(
    audio: np.ndarray,
    file_path: Union[str, Path],
    sample_rate: int = 16000
) -> None:
    """
    Save audio data to file.
    
    Args:
        audio: Audio data as numpy array
        file_path: Output file path
        sample_rate: Sample rate of the audio
    
    Raises:
        ValueError: If audio cannot be saved
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        sf.write(str(file_path), audio, sample_rate)
        logger.debug(f"Saved audio to: {file_path}")
        
    except Exception as e:
        logger.error(f"Error saving audio to {file_path}: {e}")
        raise ValueError(f"Cannot save audio file: {e}")


def extract_segment(
    audio: np.ndarray,
    sample_rate: int,
    start_time: float,
    end_time: float
) -> np.ndarray:
    """
    Extract a time segment from audio data.
    
    Args:
        audio: Audio data as numpy array
        sample_rate: Sample rate of the audio
        start_time: Start time in seconds
        end_time: End time in seconds
    
    Returns:
        Audio segment as numpy array
    """
    start_sample = int(start_time * sample_rate)
    end_sample = int(end_time * sample_rate)
    
    # Ensure bounds
    start_sample = max(0, start_sample)
    end_sample = min(len(audio), end_sample)
    
    segment = audio[start_sample:end_sample]
    
    logger.debug(
        f"Extracted segment: {start_time:.2f}s-{end_time:.2f}s "
        f"({len(segment)} samples)"
    )
    
    return segment


def convert_to_mono(audio: np.ndarray) -> np.ndarray:
    """
    Convert stereo audio to mono by averaging channels.
    
    Args:
        audio: Audio data (can be mono or stereo)
    
    Returns:
        Mono audio as 1D numpy array
    """
    if audio.ndim == 1:
        # Already mono
        return audio
    elif audio.ndim == 2:
        # Convert stereo to mono
        return np.mean(audio, axis=0)
    else:
        raise ValueError(f"Unexpected audio shape: {audio.shape}")


def resample_audio(
    audio: np.ndarray,
    orig_sr: int,
    target_sr: int
) -> np.ndarray:
    """
    Resample audio to target sample rate.
    
    Args:
        audio: Audio data as numpy array
        orig_sr: Original sample rate
        target_sr: Target sample rate
    
    Returns:
        Resampled audio
    """
    if orig_sr == target_sr:
        return audio
    
    resampled = librosa.resample(
        audio,
        orig_sr=orig_sr,
        target_sr=target_sr
    )
    
    logger.debug(f"Resampled audio: {orig_sr}Hz -> {target_sr}Hz")
    
    return resampled


def get_audio_duration(file_path: Union[str, Path]) -> float:
    """
    Get duration of audio file in seconds.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Duration in seconds
    
    Raises:
        ValueError: If duration cannot be determined
    """
    try:
        info = sf.info(str(file_path))
        return info.duration
    except Exception as e:
        logger.error(f"Error getting audio duration for {file_path}: {e}")
        raise ValueError(f"Cannot get audio duration: {e}")


def normalize_audio(audio: np.ndarray, target_level: float = -20.0) -> np.ndarray:
    """
    Normalize audio to target dBFS level.
    
    Args:
        audio: Audio data as numpy array
        target_level: Target level in dBFS (e.g., -20.0)
    
    Returns:
        Normalized audio
    """
    # Calculate current RMS
    rms = np.sqrt(np.mean(audio**2))
    
    if rms == 0:
        return audio
    
    # Calculate target RMS from dBFS
    target_rms = 10**(target_level / 20.0)
    
    # Apply gain
    gain = target_rms / rms
    normalized = audio * gain
    
    # Prevent clipping
    max_val = np.abs(normalized).max()
    if max_val > 1.0:
        normalized = normalized / max_val
    
    logger.debug(f"Normalized audio: gain={gain:.2f}")
    
    return normalized
