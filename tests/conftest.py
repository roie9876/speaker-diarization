"""
Pytest configuration and fixtures.

Shared fixtures and configuration for all tests.
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Get test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_audio_dir(test_data_dir):
    """Get sample audio directory."""
    audio_dir = test_data_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    return audio_dir


@pytest.fixture
def mock_azure_credentials(monkeypatch):
    """Mock Azure credentials for testing."""
    monkeypatch.setenv("AZURE_SPEECH_KEY", "test_key")
    monkeypatch.setenv("AZURE_REGION", "eastus")
    monkeypatch.setenv("AZURE_MODE", "cloud")


@pytest.fixture
def mock_huggingface_token(monkeypatch):
    """Mock Hugging Face token for testing."""
    monkeypatch.setenv("HUGGING_FACE_HUB_TOKEN", "test_token")


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_gpu: marks tests that require GPU"
    )
    config.addinivalue_line(
        "markers", "requires_audio: marks tests that require audio fixtures"
    )
