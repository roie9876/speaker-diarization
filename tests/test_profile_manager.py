"""
Unit tests for ProfileManager.

Tests speaker profile CRUD operations.
"""

import pytest
import json
import numpy as np
from pathlib import Path
from datetime import datetime

from src.services.profile_manager import ProfileManager


class TestProfileManager:
    """Test cases for ProfileManager."""
    
    @pytest.fixture
    def temp_profiles_dir(self, tmp_path):
        """Create temporary profiles directory."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        return profiles_dir
    
    @pytest.fixture
    def manager(self, temp_profiles_dir, monkeypatch):
        """Create ProfileManager with temp directory."""
        # Mock config to use temp directory
        from src.config.config_manager import ConfigManager
        
        def mock_profiles_dir(self):
            return temp_profiles_dir
        
        monkeypatch.setattr(ConfigManager, 'profiles_dir', property(mock_profiles_dir))
        
        return ProfileManager()
    
    @pytest.fixture
    def sample_embedding(self):
        """Create sample embedding."""
        return np.random.randn(512)
    
    def test_create_profile(self, manager, sample_embedding):
        """Test profile creation."""
        profile = manager.create_profile(
            name="Test Speaker",
            embedding=sample_embedding,
            metadata={"test": "data"}
        )
        
        assert profile['name'] == "Test Speaker"
        assert 'id' in profile
        assert 'created_date' in profile
        assert profile['samples_count'] == 1
        assert profile['metadata']['test'] == "data"
    
    def test_load_profile(self, manager, sample_embedding):
        """Test profile loading."""
        # Create profile
        created = manager.create_profile("Test Speaker", sample_embedding)
        
        # Load profile
        loaded = manager.load_profile(created['id'])
        
        assert loaded['id'] == created['id']
        assert loaded['name'] == created['name']
        assert isinstance(loaded['embedding'], np.ndarray)
        assert loaded['embedding'].shape == (512,)
    
    def test_load_profile_by_name(self, manager, sample_embedding):
        """Test loading profile by name."""
        # Create profile
        manager.create_profile("Test Speaker", sample_embedding)
        
        # Load by name
        loaded = manager.load_profile_by_name("Test Speaker")
        
        assert loaded is not None
        assert loaded['name'] == "Test Speaker"
    
    def test_list_profiles(self, manager, sample_embedding):
        """Test listing all profiles."""
        # Create multiple profiles
        manager.create_profile("Speaker 1", sample_embedding)
        manager.create_profile("Speaker 2", sample_embedding)
        
        # List profiles
        profiles = manager.list_profiles()
        
        assert len(profiles) == 2
        assert profiles[0]['name'] in ["Speaker 1", "Speaker 2"]
        # Embeddings should not be included in list
        assert 'embedding' not in profiles[0]
    
    def test_delete_profile(self, manager, sample_embedding):
        """Test profile deletion."""
        # Create profile
        profile = manager.create_profile("Test Speaker", sample_embedding)
        profile_id = profile['id']
        
        # Delete profile
        success = manager.delete_profile(profile_id)
        assert success is True
        
        # Verify deletion
        with pytest.raises(FileNotFoundError):
            manager.load_profile(profile_id)
    
    def test_search_profiles(self, manager, sample_embedding):
        """Test profile search."""
        # Create profiles
        manager.create_profile("John Doe", sample_embedding)
        manager.create_profile("Jane Smith", sample_embedding)
        manager.create_profile("John Smith", sample_embedding)
        
        # Search
        results = manager.search_profiles("John")
        
        assert len(results) == 2
        assert all("John" in p['name'] for p in results)
    
    def test_update_profile(self, manager, sample_embedding):
        """Test profile update."""
        # Create profile
        profile = manager.create_profile("Test Speaker", sample_embedding)
        profile_id = profile['id']
        
        # Update
        success = manager.update_profile(
            profile_id,
            name="Updated Speaker",
            metadata={"updated": True}
        )
        
        assert success is True
        
        # Verify update
        updated = manager.load_profile(profile_id)
        assert updated['name'] == "Updated Speaker"
        assert updated['metadata']['updated'] is True
    
    def test_export_profile(self, manager, sample_embedding, tmp_path):
        """Test profile export."""
        # Create profile
        profile = manager.create_profile("Test Speaker", sample_embedding)
        
        # Export
        export_file = tmp_path / "exported_profile.json"
        success = manager.export_profile(profile['id'], export_file)
        
        assert success is True
        assert export_file.exists()
        
        # Verify export content
        with open(export_file, 'r') as f:
            exported = json.load(f)
        
        assert exported['name'] == "Test Speaker"
        assert 'embedding' in exported
    
    def test_import_profile(self, manager, sample_embedding, tmp_path):
        """Test profile import."""
        # Create export file
        export_data = {
            'name': 'Imported Speaker',
            'embedding': sample_embedding.tolist(),
            'samples_count': 1,
            'created_date': datetime.now().isoformat(),
            'metadata': {}
        }
        
        export_file = tmp_path / "import_profile.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f)
        
        # Import
        profile = manager.import_profile(export_file)
        
        assert profile is not None
        assert profile['name'] == 'Imported Speaker'
        assert 'id' in profile
        
        # Verify it can be loaded
        loaded = manager.load_profile(profile['id'])
        assert loaded['name'] == 'Imported Speaker'
    
    def test_load_nonexistent_profile(self, manager):
        """Test loading nonexistent profile."""
        with pytest.raises(FileNotFoundError):
            manager.load_profile("nonexistent-id")
    
    def test_duplicate_name_allowed(self, manager, sample_embedding):
        """Test that duplicate names are allowed."""
        manager.create_profile("Duplicate", sample_embedding)
        manager.create_profile("Duplicate", sample_embedding)
        
        profiles = manager.list_profiles()
        duplicates = [p for p in profiles if p['name'] == "Duplicate"]
        
        assert len(duplicates) == 2
        assert duplicates[0]['id'] != duplicates[1]['id']
