# GitHub Copilot Implementation Instructions

## Project: Speaker Diarization & Selective Transcription System

This document provides focused instructions for implementing the complete system. Use this as a prompt/reference when working with GitHub Copilot or AI coding assistants.

---

## 🎯 Project Goal

Build a Python/Streamlit application that:
1. **Learns** a specific person's voice from reference audio samples
2. **Identifies** when that person speaks in meeting recordings
3. **Transcribes** only that person's speech (ignoring others)
4. Supports **3 modes**: Enrollment, Batch Processing, Live Monitoring

---

## 🏗️ Architecture Overview

### Technology Stack
- **Language**: Python 3.10+
- **UI Framework**: Streamlit
- **Speaker Diarization**: pyannote.audio 3.1+
- **Speech-to-Text**: Azure Cognitive Services Speech SDK
- **ML Framework**: PyTorch (with MPS support for Apple Silicon)
- **Audio Processing**: librosa, soundfile, pyaudio

### Core Processing Pipeline

```
Audio Input
    ↓
[pyannote.audio] Speaker Diarization
    → Segments: [(start, end, speaker_label), ...]
    ↓
For each segment:
    [pyannote.audio] Extract Embedding (512-dim vector)
    ↓
    Compare with Target Profile Embedding
    ↓
    Calculate Similarity Score
    ↓
    If Similarity ≥ Threshold (0.75):
        ✅ Target Speaker Detected
        Send to Azure Speech Service
        Get Transcript
    Else:
        ❌ Other Speaker - Skip
    ↓
Output: Timestamped Transcript (target speaker only)
```

---

## 📁 Project Structure

```
speaker-diarization/
├── src/
│   ├── services/
│   │   ├── diarization_service.py      # pyannote diarization
│   │   ├── identification_service.py   # Embedding extraction & matching
│   │   ├── transcription_service.py    # Azure Speech Service client
│   │   └── profile_manager.py          # Speaker profile CRUD
│   ├── processors/
│   │   ├── batch_processor.py          # Batch mode orchestration
│   │   └── realtime_processor.py       # Live mode streaming
│   ├── ui/
│   │   ├── app.py                      # Main Streamlit app
│   │   ├── enrollment_tab.py           # Speaker enrollment UI
│   │   ├── batch_tab.py                # Batch processing UI
│   │   └── live_tab.py                 # Real-time monitoring UI
│   ├── config/
│   │   └── config_manager.py           # Configuration management
│   └── utils/
│       ├── audio_utils.py              # Audio format conversion
│       └── logger.py                   # Logging setup
├── data/
│   ├── profiles/                       # JSON files with embeddings
│   ├── results/                        # Transcripts and outputs
│   └── temp/                           # Temporary processing files
├── tests/
│   ├── test_services.py
│   └── test_processors.py
├── .env                                # Environment variables
├── requirements.txt
└── README.md
```

---

## 🔑 Key Implementation Details

### 1. Speaker Profile Format

Store as JSON in `data/profiles/`:

```json
{
  "id": "abc123def456",
  "name": "John Doe",
  "embedding": [0.123, -0.456, ...],  // 512 values
  "samples_count": 1,
  "created_date": "2025-10-21T10:30:00",
  "metadata": {
    "audio_duration": 45.3
  }
}
```

### 2. Similarity Threshold

- **Default**: 0.75
- **Strict** (fewer false positives): 0.85
- **Permissive** (catch more): 0.65
- Use cosine similarity: `1 - cosine(embedding1, embedding2)`

### 3. Device Selection (GPU)

```python
import torch

# Works on both NVIDIA (CUDA) and Apple Silicon (MPS)
if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
```

### 4. Azure Speech Service Configuration

Support both cloud and container:

```python
# Cloud mode
speech_config = speechsdk.SpeechConfig(
    subscription=api_key,
    region="eastus"
)

# Container mode
speech_config = speechsdk.SpeechConfig(
    subscription=api_key,
    endpoint="http://localhost:5000"
)
```

### 5. Audio Format Requirements

- **Sample Rate**: 16kHz (convert if needed)
- **Channels**: Mono (convert stereo to mono)
- **Format**: WAV preferred, support MP3/M4A/FLAC

---

## 📝 Implementation Checklist

### Phase 1: Core Services

#### `diarization_service.py`
```python
class DiarizationService:
    def __init__(self, use_gpu=True):
        # Load pyannote pipeline
        # Set device (mps/cuda/cpu)
    
    def diarize(self, audio_file) -> List[Dict]:
        # Returns: [{'start': float, 'end': float, 'speaker_label': str}, ...]
```

#### `identification_service.py`
```python
class IdentificationService:
    def __init__(self, use_gpu=True):
        # Load pyannote embedding model
    
    def extract_embedding(self, audio_file, start=None, end=None) -> np.array:
        # Returns: 512-dim numpy array
    
    def compare_embeddings(self, emb1, emb2) -> float:
        # Returns: similarity score 0.0-1.0
    
    def identify_segments(self, audio_file, segments, target_embedding, threshold=0.75) -> List[Dict]:
        # Returns: segments with 'is_target' and 'similarity' added
```

#### `transcription_service.py`
```python
class TranscriptionService:
    def __init__(self, config):
        # Initialize Azure Speech SDK
        # Handle cloud vs container endpoint
    
    def transcribe_segment(self, audio_data, sample_rate) -> Dict:
        # Returns: {'text': str, 'confidence': float}
    
    def transcribe_segments(self, audio_file, segments) -> List[Dict]:
        # Process only segments where is_target=True
        # Returns: [{'start': float, 'end': float, 'text': str, 'confidence': float}, ...]
```

#### `profile_manager.py`
```python
class ProfileManager:
    def __init__(self, config):
        # Set profiles directory
    
    def create_profile(self, name, embedding, metadata=None) -> Dict:
        # Generate ID, save to JSON
    
    def load_profile(self, profile_id) -> Dict:
        # Load from JSON, convert embedding to numpy
    
    def list_profiles(self) -> List[Dict]:
        # Return profile summaries
    
    def delete_profile(self, profile_id) -> bool:
        # Remove JSON file
```

### Phase 2: Processors

#### `batch_processor.py`
```python
class BatchProcessor:
    def __init__(self, config, services):
        # Store config and service instances
    
    def process_file(self, audio_file, target_profile, threshold=0.75) -> Dict:
        # 1. Diarize audio
        # 2. Identify target speaker
        # 3. Transcribe target segments
        # 4. Return results with metadata
    
    def process_batch(self, files, target_profile, parallel=True) -> Dict:
        # Process multiple files (optionally in parallel)
        # Yield progress updates
        # Return aggregated results
```

#### `realtime_processor.py`
```python
class RealtimeProcessor:
    def __init__(self, config, services):
        # Initialize audio stream
        # Set buffer size (3 seconds)
    
    def start_monitoring(self, audio_device_id, target_profile, threshold=0.75):
        # Open audio stream
        # Implement sliding window buffering
        # Yield transcript chunks as they're detected
    
    def stop_monitoring(self):
        # Close stream, return session transcript
```

### Phase 3: Streamlit UI

#### `app.py`
```python
import streamlit as st

st.set_page_config(page_title="Speaker Diarization", layout="wide")

# Initialize services in session_state
# Create tabs: Enrollment, Batch, Live
# Render each tab
```

#### `enrollment_tab.py`
```python
def render_enrollment_tab():
    # File uploader
    # Audio player preview
    # Speaker name input
    # "Create Profile" button
    # List existing profiles with delete buttons
```

#### `batch_tab.py`
```python
def render_batch_tab():
    # Multi-file uploader
    # Profile selector dropdown
    # Settings: threshold slider, endpoint selection
    # Progress bars per file
    # Results table with view/download buttons
```

#### `live_tab.py`
```python
def render_live_tab():
    # Audio device selector
    # Profile selector
    # Audio level meter
    # Start/Stop buttons
    # Live transcript display
    # Export session button
```

---

## 🔧 Configuration

### `.env` File
```bash
# Azure Speech Service
AZURE_SPEECH_KEY=your_key_here
AZURE_REGION=eastus
AZURE_MODE=cloud  # or 'container'

# Hugging Face (for pyannote models)
HUGGING_FACE_HUB_TOKEN=your_token_here

# Processing
SIMILARITY_THRESHOLD=0.75
USE_GPU=true
```

### `requirements.txt`
```
streamlit>=1.28.0
pyannote.audio>=3.1.0
azure-cognitiveservices-speech>=1.30.0
librosa>=0.10.0
soundfile>=0.12.0
pyaudio>=0.2.13
numpy>=1.24.0
scipy>=1.10.0
torch>=2.0.0
python-dotenv>=1.0.0
```

---

## 🚀 Quick Start Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your keys

# Run application
streamlit run src/ui/app.py

# Run tests
pytest tests/
```

---

## 💡 Important Notes for Implementation

### pyannote.audio Setup
1. Accept user agreements on Hugging Face:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
2. Generate and set `HUGGING_FACE_HUB_TOKEN`
3. Models auto-download on first run (~500MB)

### Audio Processing Best Practices
1. Convert all audio to 16kHz mono before processing
2. Use librosa for format conversion
3. Handle temporary files properly (cleanup after use)
4. Validate audio duration (minimum 1 second)

### Error Handling
1. Wrap API calls in try-except
2. Provide clear error messages to users
3. Log errors with context
4. Don't crash on single file failure in batch mode

### Performance Optimization
1. Use GPU/MPS when available
2. Cache diarization results when tuning threshold
3. Process batch files in parallel (ThreadPoolExecutor)
4. Implement progress callbacks for long operations

### Real-Time Mode Specifics
1. Use 3-second buffers with 1-second overlap
2. Implement circular buffer for audio data
3. Run processing in separate thread
4. Update UI async (use Streamlit's session_state)

---

## 🎯 Critical Success Factors

### Must-Have Features
✅ Enrollment: Create/delete speaker profiles  
✅ Batch: Process multiple files, display results  
✅ Live: Real-time monitoring with <5s latency  
✅ Transcripts: Timestamped, accurate, exportable  

### Quality Standards
- Speaker identification accuracy: ≥90%
- Transcription accuracy: ≥95% (Azure Speech standard)
- UI responsiveness: <200ms for interactions
- No crashes on bad input (graceful error handling)

### Testing Requirements
- Test with various audio qualities
- Test with similar voices (edge case)
- Test with background noise
- Validate threshold tuning works

---

## 🐛 Common Pitfalls to Avoid

1. **Don't** process embeddings without normalizing (pyannote handles this)
2. **Don't** forget to convert embeddings to numpy when loading from JSON
3. **Don't** use CUDA-specific code (use device-agnostic: `model.to(device)`)
4. **Don't** transcribe ALL segments (only is_target=True)
5. **Don't** block Streamlit UI during long operations (use progress bars)

---

## 📚 Reference Documentation

Full documentation available in `docs/`:
- `PROJECT_OVERVIEW.md` - Goals and requirements
- `architecture/system-architecture.md` - Detailed design
- `technical/pyannote-integration.md` - pyannote.audio guide
- `technical/technology-stack.md` - Setup and dependencies
- `requirements/functional-requirements.md` - 51 feature specs
- `IMPLEMENTATION_GUIDE.md` - Phased roadmap

---

## 🎬 Example End-to-End Flow

```python
# 1. User enrolls speaker
profile = profile_manager.create_profile(
    name="John Doe",
    embedding=identification_service.extract_embedding("reference.wav")
)

# 2. User uploads meeting recording
segments = diarization_service.diarize("meeting.wav")

# 3. System identifies target speaker
results = identification_service.identify_segments(
    audio_file="meeting.wav",
    segments=segments,
    target_embedding=profile['embedding'],
    threshold=0.75
)

# 4. System transcribes target segments only
transcripts = transcription_service.transcribe_segments(
    audio_file="meeting.wav",
    segments=[s for s in results if s['is_target']]
)

# 5. Display to user
for t in transcripts:
    print(f"[{t['start']:.1f}s] {t['text']}")
```

---

**Ready to implement?** Start with Phase 1 (Core Services) and work through each component systematically. Use this document as your reference throughout development! 🚀

---

**Document Version**: 1.0  
**Created**: October 21, 2025  
**Status**: Ready for Development
