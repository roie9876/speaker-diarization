# Tests

This directory contains unit tests, integration tests, and test utilities for the Speaker Diarization System.

## Structure

```
tests/
├── conftest.py                         # Pytest configuration and shared fixtures
├── fixtures/                           # Test fixtures and sample data
│   ├── audio/                         # Sample audio files
│   └── profiles/                      # Sample speaker profiles
├── test_diarization_service.py        # Diarization service tests
├── test_identification_service.py     # Identification service tests
├── test_profile_manager.py            # Profile manager tests
├── test_transcription_service.py      # Transcription service tests (TODO)
├── test_batch_processor.py            # Batch processor tests (TODO)
├── test_realtime_processor.py         # Realtime processor tests (TODO)
└── verify_installation.py             # Installation verification script
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_profile_manager.py
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Only Fast Tests (Skip Slow Tests)
```bash
pytest tests/ -m "not slow"
```

### Run Only Unit Tests (Skip Integration)
```bash
pytest tests/ -m "not integration"
```

## Test Markers

Tests are marked with different categories:

- `@pytest.mark.slow` - Tests that take significant time
- `@pytest.mark.integration` - Integration tests requiring external services
- `@pytest.mark.requires_gpu` - Tests requiring GPU acceleration
- `@pytest.mark.requires_audio` - Tests requiring audio fixture files

## Test Fixtures

### Audio Fixtures

Place sample audio files in `fixtures/audio/`:
- `sample_audio.wav` - General test audio (10-30 seconds)
- `speaker_1.wav` - Reference audio for speaker 1
- `speaker_2.wav` - Reference audio for speaker 2
- `multi_speaker.wav` - Audio with multiple speakers

### Creating Audio Fixtures

You can create test audio using Python:

```python
import numpy as np
import soundfile as sf

# Create 5 seconds of test audio (sine wave)
duration = 5
sample_rate = 16000
frequency = 440  # A4 note

t = np.linspace(0, duration, duration * sample_rate)
audio = np.sin(2 * np.pi * frequency * t)

sf.write('fixtures/audio/test_tone.wav', audio, sample_rate)
```

## Mocking External Services

Tests mock external dependencies:

- **Azure Speech Service**: Mocked in tests, credentials in fixtures
- **Hugging Face Models**: Tests use CPU-only, smaller models when possible
- **Audio Devices**: PyAudio calls are mocked for realtime tests

## Test Coverage Goals

Target coverage: 80%+

Current coverage by module:
- Config Manager: ✅ 100%
- Audio Utils: ⏳ Pending
- Profile Manager: ✅ 90%+
- Diarization Service: ⏳ Pending
- Identification Service: ⏳ Pending
- Transcription Service: ⏳ Pending
- Batch Processor: ⏳ Pending
- Realtime Processor: ⏳ Pending

## Installation Verification

Before running tests, verify your installation:

```bash
python tests/verify_installation.py
```

This checks:
- Python version
- Package imports
- GPU availability
- Configuration files
- Required directories
- Audio devices

## CI/CD Integration

Tests are designed to run in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest tests/ -v --cov=src --cov-report=xml -m "not requires_gpu"
```

## Writing New Tests

### Test Template

```python
"""
Tests for MyService.
"""

import pytest
from src.services.my_service import MyService


class TestMyService:
    """Test cases for MyService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return MyService()
    
    def test_basic_functionality(self, service):
        """Test basic functionality."""
        result = service.do_something()
        assert result is not None
    
    @pytest.mark.slow
    def test_slow_operation(self, service):
        """Test that takes significant time."""
        result = service.slow_operation()
        assert result is not None
```

### Best Practices

1. **Use fixtures** for setup/teardown
2. **Mock external services** to avoid API costs
3. **Mark slow tests** with `@pytest.mark.slow`
4. **Use temp directories** for file operations
5. **Clean up resources** in fixtures
6. **Test edge cases** and error handling
7. **Keep tests isolated** (no shared state)

## Troubleshooting

### "No audio fixtures available"
- Tests skip when fixtures are missing
- Add sample audio files to `fixtures/audio/`
- Or mark test with `@pytest.mark.requires_audio`

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check `PYTHONPATH` includes project root

### Azure/HuggingFace Errors
- Tests use mock credentials by default
- For integration tests, set real credentials in `.env`
- Mark integration tests with `@pytest.mark.integration`

## Future Enhancements

- [ ] Add integration tests for full pipeline
- [ ] Add performance benchmarks
- [ ] Add stress tests for realtime processor
- [ ] Add UI tests with Streamlit testing framework
- [ ] Add audio quality tests
- [ ] Add model accuracy tests with ground truth data
