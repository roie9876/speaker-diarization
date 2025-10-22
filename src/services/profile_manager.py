"""
Speaker Profile Manager for Speaker Diarization System.

Manages speaker profiles including creation, storage, retrieval, and deletion.
Profiles contain speaker embeddings and metadata for identification.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union
import numpy as np
from src.config.config_manager import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProfileManager:
    """
    Manages speaker profiles with embeddings and metadata.
    
    Profiles are stored as JSON files in the profiles directory.
    """
    
    def __init__(self):
        """Initialize profile manager."""
        self.config = get_config()
        self.profiles_dir = self.config.profiles_dir
        logger.info(f"Profile manager initialized (dir={self.profiles_dir})")
    
    def create_profile(
        self,
        name: str,
        embedding: np.ndarray,
        audio_file: Optional[Union[str, Path]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new speaker profile.
        
        Args:
            name: Speaker name
            embedding: 512-dimensional embedding vector
            audio_file: Optional path to reference audio file
            metadata: Optional additional metadata
        
        Returns:
            Created profile dictionary containing:
                - 'id': Unique profile ID
                - 'name': Speaker name
                - 'embedding': Embedding vector (as list)
                - 'created_date': ISO format creation timestamp
                - 'metadata': Additional metadata
        
        Raises:
            ValueError: If profile creation fails
        """
        try:
            # Generate unique ID
            profile_id = str(uuid.uuid4())
            
            # Prepare profile data
            profile = {
                "id": profile_id,
                "name": name,
                "embedding": embedding.tolist(),  # Convert numpy to list for JSON
                "created_date": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add audio file info if provided
            if audio_file:
                profile["metadata"]["audio_file"] = str(Path(audio_file).name)
            
            # Add embedding shape info
            profile["metadata"]["embedding_shape"] = embedding.shape[0]
            
            # Add quality assessment if provided in metadata
            if metadata and "quality" in metadata:
                profile["quality"] = metadata["quality"]
            
            # Save to file
            self._save_profile(profile)
            
            logger.info(f"Created profile: {name} (ID={profile_id})")
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create profile for {name}: {e}")
            raise ValueError(f"Cannot create profile: {e}")
    
    def load_profile(self, profile_id: str) -> Dict:
        """
        Load a speaker profile by ID.
        
        Args:
            profile_id: Profile ID
        
        Returns:
            Profile dictionary with embedding as numpy array
        
        Raises:
            ValueError: If profile not found or cannot be loaded
        """
        try:
            profile_path = self.profiles_dir / f"{profile_id}.json"
            
            if not profile_path.exists():
                raise ValueError(f"Profile not found: {profile_id}")
            
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            
            # Convert embedding back to numpy array
            profile["embedding"] = np.array(profile["embedding"])
            
            logger.debug(f"Loaded profile: {profile['name']} (ID={profile_id})")
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to load profile {profile_id}: {e}")
            raise ValueError(f"Cannot load profile: {e}")
    
    def load_profile_by_name(self, name: str) -> Optional[Dict]:
        """
        Load a speaker profile by name.
        
        Args:
            name: Speaker name
        
        Returns:
            Profile dictionary or None if not found
        """
        profiles = self.list_profiles()
        
        for profile_summary in profiles:
            if profile_summary["name"].lower() == name.lower():
                return self.load_profile(profile_summary["id"])
        
        logger.warning(f"Profile not found with name: {name}")
        return None
    
    def list_profiles(self) -> List[Dict]:
        """
        List all available speaker profiles.
        
        Returns:
            List of profile summaries (without embeddings) containing:
                - 'id': Profile ID
                - 'name': Speaker name
                - 'created_date': Creation timestamp
                - 'metadata': Metadata dict
        """
        profiles = []
        
        try:
            for profile_path in self.profiles_dir.glob("*.json"):
                try:
                    with open(profile_path, 'r') as f:
                        profile = json.load(f)
                    
                    # Return summary without embedding (for performance)
                    summary = {
                        "id": profile["id"],
                        "name": profile["name"],
                        "created_date": profile["created_date"],
                        "metadata": profile.get("metadata", {}),
                        "quality": profile.get("quality", {})  # Include quality info
                    }
                    
                    profiles.append(summary)
                    
                except Exception as e:
                    logger.warning(f"Failed to load profile {profile_path}: {e}")
                    continue
            
            logger.debug(f"Found {len(profiles)} profiles")
            
        except Exception as e:
            logger.error(f"Failed to list profiles: {e}")
        
        # Sort by name
        profiles.sort(key=lambda p: p["name"].lower())
        
        return profiles
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a speaker profile.
        
        Args:
            profile_id: Profile ID to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            profile_path = self.profiles_dir / f"{profile_id}.json"
            
            if not profile_path.exists():
                logger.warning(f"Profile not found: {profile_id}")
                return False
            
            # Load profile to get name for logging
            try:
                profile = self.load_profile(profile_id)
                name = profile["name"]
            except Exception:
                name = "unknown"
            
            # Delete file
            profile_path.unlink()
            
            logger.info(f"Deleted profile: {name} (ID={profile_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete profile {profile_id}: {e}")
            return False
    
    def update_profile(
        self,
        profile_id: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Update profile information (not including embedding).
        
        Args:
            profile_id: Profile ID
            name: New name (optional)
            metadata: New metadata to merge (optional)
        
        Returns:
            Updated profile dictionary
        
        Raises:
            ValueError: If profile cannot be updated
        """
        try:
            # Load existing profile
            profile = self.load_profile(profile_id)
            
            # Update fields
            if name:
                profile["name"] = name
            
            if metadata:
                profile["metadata"].update(metadata)
            
            # Add modified timestamp
            profile["metadata"]["modified_date"] = datetime.now().isoformat()
            
            # Save updated profile
            self._save_profile(profile)
            
            logger.info(f"Updated profile: {profile['name']} (ID={profile_id})")
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to update profile {profile_id}: {e}")
            raise ValueError(f"Cannot update profile: {e}")
    
    def profile_exists(self, profile_id: str) -> bool:
        """
        Check if a profile exists.
        
        Args:
            profile_id: Profile ID
        
        Returns:
            True if profile exists, False otherwise
        """
        profile_path = self.profiles_dir / f"{profile_id}.json"
        return profile_path.exists()
    
    def search_profiles(self, query: str) -> List[Dict]:
        """
        Search profiles by name.
        
        Args:
            query: Search query
        
        Returns:
            List of matching profile summaries
        """
        all_profiles = self.list_profiles()
        query_lower = query.lower()
        
        matches = [
            p for p in all_profiles
            if query_lower in p["name"].lower()
        ]
        
        logger.debug(f"Search '{query}': found {len(matches)} matches")
        
        return matches
    
    def get_profile_count(self) -> int:
        """
        Get total number of profiles.
        
        Returns:
            Number of profiles
        """
        return len(list(self.profiles_dir.glob("*.json")))
    
    def _save_profile(self, profile: Dict) -> None:
        """
        Save profile to JSON file.
        
        Args:
            profile: Profile dictionary
        
        Raises:
            ValueError: If profile cannot be saved
        """
        try:
            # Convert numpy array to list if present
            profile_to_save = profile.copy()
            if isinstance(profile_to_save.get("embedding"), np.ndarray):
                profile_to_save["embedding"] = profile_to_save["embedding"].tolist()
            
            # Save to file
            profile_path = self.profiles_dir / f"{profile['id']}.json"
            
            with open(profile_path, 'w') as f:
                json.dump(profile_to_save, f, indent=2)
            
            logger.debug(f"Saved profile to: {profile_path}")
            
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            raise ValueError(f"Cannot save profile: {e}")
    
    def export_profile(self, profile_id: str, output_path: Union[str, Path]) -> None:
        """
        Export profile to a specific location.
        
        Args:
            profile_id: Profile ID to export
            output_path: Destination file path
        
        Raises:
            ValueError: If export fails
        """
        try:
            profile = self.load_profile(profile_id)
            output_path = Path(output_path)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert embedding to list for JSON
            if isinstance(profile["embedding"], np.ndarray):
                profile["embedding"] = profile["embedding"].tolist()
            
            # Save
            with open(output_path, 'w') as f:
                json.dump(profile, f, indent=2)
            
            logger.info(f"Exported profile to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export profile {profile_id}: {e}")
            raise ValueError(f"Cannot export profile: {e}")
    
    def import_profile(self, input_path: Union[str, Path]) -> Dict:
        """
        Import profile from a JSON file.
        
        Args:
            input_path: Path to profile JSON file
        
        Returns:
            Imported profile dictionary
        
        Raises:
            ValueError: If import fails
        """
        try:
            input_path = Path(input_path)
            
            with open(input_path, 'r') as f:
                profile = json.load(f)
            
            # Validate required fields
            required_fields = ["name", "embedding"]
            missing = [f for f in required_fields if f not in profile]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")
            
            # Generate new ID if not present
            if "id" not in profile:
                profile["id"] = str(uuid.uuid4())
            
            # Convert embedding to numpy array
            profile["embedding"] = np.array(profile["embedding"])
            
            # Save profile
            self._save_profile(profile)
            
            logger.info(f"Imported profile: {profile['name']} from {input_path}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to import profile from {input_path}: {e}")
            raise ValueError(f"Cannot import profile: {e}")
