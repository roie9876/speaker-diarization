"""
Configuration Manager for Speaker Diarization System.

Loads and manages configuration from environment variables and provides
centralized access to settings throughout the application.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration from environment variables."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Optional path to .env file. If None, uses default .env in project root.
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to find .env in project root
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / ".env"
            if env_path.exists():
                load_dotenv(env_path)
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate that required configuration is present."""
        required_vars = ["AZURE_SPEECH_KEY", "HUGGING_FACE_HUB_TOKEN"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Please check your .env file."
            )
    
    # Azure Speech Service Configuration
    @property
    def azure_speech_key(self) -> str:
        """Azure Speech Service API key."""
        return os.getenv("AZURE_SPEECH_KEY", "")
    
    @property
    def azure_region(self) -> str:
        """Azure Speech Service region."""
        return os.getenv("AZURE_REGION", "eastus")
    
    @property
    def azure_mode(self) -> str:
        """Azure mode: 'cloud' or 'container'."""
        return os.getenv("AZURE_MODE", "cloud")
    
    @property
    def azure_endpoint(self) -> Optional[str]:
        """Azure endpoint URL for container mode."""
        return os.getenv("AZURE_ENDPOINT")
    
    # Hugging Face Configuration
    @property
    def huggingface_token(self) -> str:
        """Hugging Face Hub token for pyannote models."""
        return os.getenv("HUGGING_FACE_HUB_TOKEN", "")
    
    # Processing Configuration
    @property
    def similarity_threshold(self) -> float:
        """Similarity threshold for speaker identification (0.0-1.0)."""
        return float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))
    
    @property
    def use_gpu(self) -> bool:
        """Whether to use GPU acceleration if available."""
        return os.getenv("USE_GPU", "true").lower() in ("true", "1", "yes")
    
    @property
    def sample_rate(self) -> int:
        """Audio sample rate in Hz."""
        return int(os.getenv("SAMPLE_RATE", "16000"))
    
    @property
    def audio_chunk_duration(self) -> float:
        """Audio chunk duration in seconds for real-time processing."""
        return float(os.getenv("AUDIO_CHUNK_DURATION", "3.0"))
    
    @property
    def audio_overlap_duration(self) -> float:
        """Audio overlap duration in seconds for real-time processing."""
        return float(os.getenv("AUDIO_OVERLAP_DURATION", "1.0"))
    
    # Storage Paths
    @property
    def profiles_dir(self) -> Path:
        """Directory for speaker profiles."""
        project_root = Path(__file__).parent.parent.parent
        path = Path(os.getenv("PROFILES_DIR", "data/profiles"))
        if not path.is_absolute():
            path = project_root / path
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def results_dir(self) -> Path:
        """Directory for processing results."""
        project_root = Path(__file__).parent.parent.parent
        path = Path(os.getenv("RESULTS_DIR", "data/results"))
        if not path.is_absolute():
            path = project_root / path
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def temp_dir(self) -> Path:
        """Directory for temporary files."""
        project_root = Path(__file__).parent.parent.parent
        path = Path(os.getenv("TEMP_DIR", "data/temp"))
        if not path.is_absolute():
            path = project_root / path
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    # Logging Configuration
    @property
    def log_level(self) -> str:
        """Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""
        return os.getenv("LOG_LEVEL", "INFO").upper()
    
    @property
    def log_file(self) -> Optional[Path]:
        """Log file path."""
        log_file_str = os.getenv("LOG_FILE")
        if log_file_str:
            project_root = Path(__file__).parent.parent.parent
            path = Path(log_file_str)
            if not path.is_absolute():
                path = project_root / path
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        return None
    
    def __repr__(self) -> str:
        """String representation of configuration (safe - no secrets)."""
        return (
            f"ConfigManager("
            f"azure_region={self.azure_region}, "
            f"azure_mode={self.azure_mode}, "
            f"similarity_threshold={self.similarity_threshold}, "
            f"use_gpu={self.use_gpu}, "
            f"sample_rate={self.sample_rate})"
        )


# Global configuration instance
_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get the global configuration instance.
    
    Returns:
        ConfigManager instance
    """
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config


def reset_config() -> None:
    """Reset the global configuration instance (mainly for testing)."""
    global _config
    _config = None
