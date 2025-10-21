# Implementation Guide & Roadmap

## Document Information

- **Project**: Speaker Diarization & Selective Transcription System
- **Version**: 1.0
- **Date**: October 21, 2025

## Overview

This document provides a step-by-step implementation roadmap for building the complete system. It serves as a guide for developers to implement the project from scratch.

---

## Implementation Phases

### Phase 1: Foundation & Setup (Week 1)
### Phase 2: Core Processing Engine (Week 2)
### Phase 3: Streamlit UI - Enrollment (Week 3)
### Phase 4: Batch Processing Mode (Week 4)
### Phase 5: Live/Real-Time Mode (Week 5-6)
### Phase 6: Testing & Refinement (Week 7)
### Phase 7: Deployment & Documentation (Week 8)

---

## Phase 1: Foundation & Setup

### Goals
- Set up development environment
- Install dependencies
- Create project structure
- Verify all tools work

### Tasks

#### 1.1 Project Structure Setup

```
speaker-diarization/
├── src/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── diarization_service.py
│   │   ├── identification_service.py
│   │   ├── transcription_service.py
│   │   └── profile_manager.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── batch_processor.py
│   │   └── realtime_processor.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── enrollment_tab.py
│   │   ├── batch_tab.py
│   │   └── live_tab.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_manager.py
│   └── utils/
│       ├── __init__.py
│       ├── audio_utils.py
│       └── logger.py
├── data/
│   ├── profiles/
│   ├── results/
│   └── temp/
├── tests/
│   ├── __init__.py
│   ├── test_services.py
│   └── test_processors.py
├── docs/
│   └── [documentation files created earlier]
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── setup.py
```

**Action**: Create this folder structure

```bash
mkdir -p src/{services,processors,ui,config,utils}
mkdir -p data/{profiles,results,temp}
mkdir -p tests
touch src/__init__.py src/services/__init__.py src/processors/__init__.py
touch src/ui/__init__.py src/config/__init__.py src/utils/__init__.py
```

#### 1.2 Environment Setup

**Create `requirements.txt`**:
```
# Core application
streamlit>=1.28.0
pyannote.audio>=3.1.0
azure-cognitiveservices-speech>=1.30.0

# Audio processing
librosa>=0.10.0
soundfile>=0.12.0
pyaudio>=0.2.13
pydub>=0.25.0

# Scientific computing
numpy>=1.24.0
scipy>=1.10.0
torch>=2.0.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0

# Development
pytest>=7.4.0
black>=23.0.0
```

**Create `.env.example`**:
```
# Azure Speech Service
AZURE_SPEECH_KEY=your_azure_key_here
AZURE_REGION=eastus
AZURE_MODE=cloud

# Hugging Face
HUGGING_FACE_HUB_TOKEN=your_hf_token_here

# Application Settings
SIMILARITY_THRESHOLD=0.75
USE_GPU=true
```

**Action**: Set up virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 1.3 Configuration Manager

**Create `src/config/config_manager.py`**:
```python
import os
import json
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_path="config/settings.json"):
        load_dotenv()
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment"""
        default_config = {
            "azure": {
                "mode": os.getenv("AZURE_MODE", "cloud"),
                "cloud_endpoint": f"https://{os.getenv('AZURE_REGION', 'eastus')}.api.cognitive.microsoft.com",
                "container_endpoint": "http://localhost:5000",
                "api_key": os.getenv("AZURE_SPEECH_KEY"),
                "region": os.getenv("AZURE_REGION", "eastus")
            },
            "processing": {
                "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.75")),
                "use_gpu": os.getenv("USE_GPU", "true").lower() == "true",
                "parallel_processing": True,
                "max_workers": 4,
                "buffer_duration": 3.0
            },
            "storage": {
                "profiles_dir": "data/profiles",
                "results_dir": "data/results",
                "temp_dir": "data/temp",
                "logs_dir": "logs"
            },
            "ui": {
                "default_tab": "enrollment",
                "auto_export": False,
                "include_timestamps": True,
                "include_confidence": True
            }
        }
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                file_config = json.load(f)
                default_config.update(file_config)
        
        return default_config
    
    def get(self, key_path):
        """Get config value by dot-notation path"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            value = value.get(key)
            if value is None:
                return None
        return value
    
    def save(self):
        """Save current configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
```

**Deliverables**:
- ✅ Project structure created
- ✅ Dependencies installed
- ✅ Configuration system working
- ✅ Environment variables set

---

## Phase 2: Core Processing Engine

### Goals
- Implement speaker diarization
- Implement speaker identification
- Implement Azure STT integration
- Create profile management

### Tasks

#### 2.1 Diarization Service

**Create `src/services/diarization_service.py`**:
```python
import torch
from pyannote.audio import Pipeline
from pyannote.core import Segment

class DiarizationService:
    """Speaker diarization using pyannote.audio"""
    
    def __init__(self, use_gpu=True):
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        self.pipeline = None
        self._load_pipeline()
    
    def _load_pipeline(self):
        """Load pyannote diarization pipeline"""
        import os
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        self.pipeline.to(self.device)
    
    def diarize(self, audio_file):
        """
        Perform speaker diarization
        
        Returns: List of segment dicts with start, end, speaker_label
        """
        diarization = self.pipeline(audio_file)
        
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                'start': turn.start,
                'end': turn.end,
                'duration': turn.end - turn.start,
                'speaker_label': speaker
            })
        
        return segments
```

#### 2.2 Identification Service

**Create `src/services/identification_service.py`**:
```python
import torch
import numpy as np
from pyannote.audio import Inference, Audio
from pyannote.core import Segment
from scipy.spatial.distance import cosine

class IdentificationService:
    """Speaker identification using embeddings"""
    
    def __init__(self, use_gpu=True):
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        self.model = None
        self.audio = Audio()
        self._load_model()
    
    def _load_model(self):
        """Load embedding model"""
        import os
        self.model = Inference(
            "pyannote/embedding",
            window="whole",
            use_auth_token=os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        self.model.to(self.device)
    
    def extract_embedding(self, audio_file, start=None, end=None):
        """Extract speaker embedding from audio"""
        if start is not None and end is not None:
            waveform, sample_rate = self.audio.crop(
                audio_file,
                Segment(start, end)
            )
            embedding = self.model({
                "waveform": waveform,
                "sample_rate": sample_rate
            })
        else:
            embedding = self.model(audio_file)
        
        return np.array(embedding)
    
    def compare_embeddings(self, emb1, emb2):
        """Compute cosine similarity between embeddings"""
        return 1 - cosine(emb1, emb2)
    
    def identify_segments(self, audio_file, segments, target_embedding, threshold=0.75):
        """
        Identify which segments match target speaker
        
        Returns: segments with added 'is_target' and 'similarity' fields
        """
        results = []
        
        for segment in segments:
            # Extract embedding for segment
            seg_embedding = self.extract_embedding(
                audio_file,
                start=segment['start'],
                end=segment['end']
            )
            
            # Compare with target
            similarity = self.compare_embeddings(seg_embedding, target_embedding)
            is_target = similarity >= threshold
            
            segment_result = segment.copy()
            segment_result['similarity'] = similarity
            segment_result['is_target'] = is_target
            results.append(segment_result)
        
        return results
```

#### 2.3 Transcription Service

**Create `src/services/transcription_service.py`**:
```python
import azure.cognitiveservices.speech as speechsdk
import tempfile
import soundfile as sf

class TranscriptionService:
    """Azure Speech Service transcription"""
    
    def __init__(self, config):
        self.config = config
        self.speech_config = self._create_speech_config()
    
    def _create_speech_config(self):
        """Create Azure Speech configuration"""
        if self.config.get('azure.mode') == 'cloud':
            speech_config = speechsdk.SpeechConfig(
                subscription=self.config.get('azure.api_key'),
                region=self.config.get('azure.region')
            )
        else:
            # Container mode
            endpoint = self.config.get('azure.container_endpoint')
            speech_config = speechsdk.SpeechConfig(
                subscription=self.config.get('azure.api_key'),
                endpoint=endpoint
            )
        
        speech_config.speech_recognition_language = "en-US"
        return speech_config
    
    def transcribe_segment(self, audio_data, sample_rate):
        """
        Transcribe audio segment
        
        Args:
            audio_data: numpy array
            sample_rate: int
            
        Returns:
            dict with text, start, end, confidence
        """
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            sf.write(tmp.name, audio_data, sample_rate)
            
            # Create audio config
            audio_config = speechsdk.audio.AudioConfig(filename=tmp.name)
            
            # Create recognizer
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Recognize
            result = recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    'text': result.text,
                    'confidence': result.properties.get('confidence', 0.0)
                }
            else:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'error': str(result.reason)
                }
    
    def transcribe_segments(self, audio_file, segments):
        """
        Transcribe multiple segments from audio file
        
        Args:
            audio_file: path to audio
            segments: list of segment dicts (must have is_target=True)
            
        Returns:
            list of transcripts with timestamps
        """
        from pyannote.audio import Audio
        audio = Audio()
        
        transcripts = []
        
        for segment in segments:
            if not segment.get('is_target', False):
                continue
            
            # Extract audio segment
            from pyannote.core import Segment
            waveform, sample_rate = audio.crop(
                audio_file,
                Segment(segment['start'], segment['end'])
            )
            
            # Convert to numpy
            audio_data = waveform.numpy()[0]  # Take first channel
            
            # Transcribe
            transcript = self.transcribe_segment(audio_data, sample_rate)
            
            transcripts.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': transcript['text'],
                'confidence': transcript['confidence'],
                'speaker_confidence': segment.get('similarity', 0.0)
            })
        
        return transcripts
```

#### 2.4 Profile Manager

**Create `src/services/profile_manager.py`**:
```python
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

class ProfileManager:
    """Manage speaker profiles"""
    
    def __init__(self, config):
        self.profiles_dir = config.get('storage.profiles_dir')
        os.makedirs(self.profiles_dir, exist_ok=True)
    
    def create_profile(self, name, embedding, metadata=None):
        """Create new speaker profile"""
        profile_id = self._generate_id(name)
        
        profile = {
            'id': profile_id,
            'name': name,
            'embedding': embedding.tolist(),
            'samples_count': 1,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self._save_profile(profile)
        return profile
    
    def _generate_id(self, name):
        """Generate unique profile ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{name}_{timestamp}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:16]
    
    def _save_profile(self, profile):
        """Save profile to disk"""
        filename = f"{profile['id']}.json"
        filepath = os.path.join(self.profiles_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(profile, f, indent=2)
    
    def load_profile(self, profile_id):
        """Load profile by ID"""
        filepath = os.path.join(self.profiles_dir, f"{profile_id}.json")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Profile not found: {profile_id}")
        
        with open(filepath, 'r') as f:
            profile = json.load(f)
        
        # Convert embedding back to numpy
        import numpy as np
        profile['embedding'] = np.array(profile['embedding'])
        
        return profile
    
    def list_profiles(self):
        """List all profiles"""
        profiles = []
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                profile_id = filename[:-5]
                try:
                    profile = self.load_profile(profile_id)
                    profiles.append({
                        'id': profile['id'],
                        'name': profile['name'],
                        'created_date': profile['created_date'],
                        'samples_count': profile['samples_count']
                    })
                except Exception:
                    pass
        
        return profiles
    
    def delete_profile(self, profile_id):
        """Delete profile"""
        filepath = os.path.join(self.profiles_dir, f"{profile_id}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
```

**Deliverables**:
- ✅ Diarization service implemented
- ✅ Identification service implemented
- ✅ Transcription service implemented
- ✅ Profile management working
- ✅ Unit tests passed

---

## Phase 3: Streamlit UI - Enrollment

### Goals
- Create basic Streamlit app structure
- Implement enrollment tab
- Test end-to-end enrollment flow

### Tasks

#### 3.1 Main App Structure

**Create `src/ui/app.py`**:
```python
import streamlit as st
from config.config_manager import ConfigManager
from ui.enrollment_tab import render_enrollment_tab
from ui.batch_tab import render_batch_tab
from ui.live_tab import render_live_tab

# Page config
st.set_page_config(
    page_title="Speaker Diarization System",
    page_icon="🎤",
    layout="wide"
)

# Initialize config
if 'config' not in st.session_state:
    st.session_state.config = ConfigManager()

# Title
st.title("🎤 Speaker Diarization & Selective Transcription")

# Tabs
tab1, tab2, tab3 = st.tabs(["👤 Enrollment", "📁 Batch Processing", "🔴 Live Mode"])

with tab1:
    render_enrollment_tab()

with tab2:
    render_batch_tab()

with tab3:
    render_live_tab()
```

#### 3.2 Enrollment Tab

**Create `src/ui/enrollment_tab.py`**:
```python
import streamlit as st
from services.identification_service import IdentificationService
from services.profile_manager import ProfileManager

def render_enrollment_tab():
    """Render speaker enrollment interface"""
    
    st.header("Speaker Enrollment")
    st.write("Upload a reference audio file to create a speaker profile.")
    
    # Initialize services
    if 'identification_service' not in st.session_state:
        config = st.session_state.config
        st.session_state.identification_service = IdentificationService(
            use_gpu=config.get('processing.use_gpu')
        )
        st.session_state.profile_manager = ProfileManager(config)
    
    # File upload
    audio_file = st.file_uploader(
        "Upload reference audio",
        type=['wav', 'mp3', 'm4a', 'flac'],
        help="Upload 30-60 seconds of clear speech from the target speaker"
    )
    
    if audio_file:
        # Save uploaded file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_file.read())
            tmp_path = tmp.name
        
        # Audio player
        st.audio(tmp_path)
        
        # Get audio info
        import librosa
        duration = librosa.get_duration(path=tmp_path)
        st.info(f"📊 Duration: {duration:.1f} seconds")
        
        if duration < 10:
            st.warning("⚠️ Audio is short. Recommend 30+ seconds for better accuracy.")
        
        # Speaker name input
        speaker_name = st.text_input("Speaker Name", placeholder="e.g., John Doe")
        
        # Create profile button
        if st.button("Create Profile", type="primary", disabled=not speaker_name):
            with st.spinner("Extracting speaker embedding..."):
                try:
                    # Extract embedding
                    embedding = st.session_state.identification_service.extract_embedding(tmp_path)
                    
                    # Create profile
                    profile = st.session_state.profile_manager.create_profile(
                        name=speaker_name,
                        embedding=embedding,
                        metadata={'audio_duration': duration}
                    )
                    
                    st.success(f"✅ Profile created for {speaker_name}!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error creating profile: {e}")
    
    # Display existing profiles
    st.divider()
    st.subheader("Enrolled Speakers")
    
    profiles = st.session_state.profile_manager.list_profiles()
    
    if profiles:
        for profile in profiles:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{profile['name']}**")
            with col2:
                st.write(f"Created: {profile['created_date'][:10]}")
            with col3:
                st.write(f"Samples: {profile['samples_count']}")
            with col4:
                if st.button("🗑️", key=f"delete_{profile['id']}"):
                    st.session_state.profile_manager.delete_profile(profile['id'])
                    st.rerun()
    else:
        st.info("No profiles yet. Upload an audio file to get started!")
```

**Run App**:
```bash
streamlit run src/ui/app.py
```

**Deliverables**:
- ✅ Streamlit app running
- ✅ Enrollment tab functional
- ✅ Can create and view profiles
- ✅ Can delete profiles

---

## Phase 4: Batch Processing Mode

*Continue with batch_tab.py implementation similar to enrollment...*

**Deliverables**:
- ✅ Batch upload working
- ✅ Processing pipeline functional
- ✅ Results display working
- ✅ Export functionality complete

---

## Phase 5: Live/Real-Time Mode

*Implement live mode with audio streaming...*

**Deliverables**:
- ✅ Audio input selection working
- ✅ Real-time processing functional
- ✅ Live transcript display working
- ✅ Session export working

---

## Phase 6: Testing & Refinement

### Tasks
- Unit tests for all services
- Integration tests for workflows
- Performance benchmarks
- Bug fixes and optimization

---

## Phase 7: Deployment & Documentation

### Tasks
- Azure Speech Container setup guide
- Deployment scripts
- User documentation
- Final testing
- Handoff

---

## Success Criteria

- ✅ All functional requirements implemented
- ✅ Non-functional requirements met
- ✅ Tests passing
- ✅ Documentation complete
- ✅ Successfully deployed and validated

---

**Document Status**: Implementation Roadmap  
**Last Updated**: October 21, 2025  
**Ready for Development**: Yes
