# Technology Stack

## Document Information

- **Project**: Speaker Diarization & Selective Transcription System
- **Version**: 1.0
- **Date**: October 21, 2025

## Overview

This document provides comprehensive details about all technologies, libraries, frameworks, and tools used in the project.

---

## Core Technologies

### Python 3.8+

**Purpose**: Primary development language

**Version Requirements**:
- Minimum: Python 3.8
- Recommended: Python 3.10 or 3.11
- Maximum: Python 3.11 (PyTorch compatibility)

**Rationale**:
- Excellent ML/AI ecosystem
- Rich audio processing libraries
- Streamlit and pyannote compatibility
- Azure SDK support

**Installation**:
```bash
# macOS (Homebrew)
brew install python@3.10

# Ubuntu
sudo apt install python3.10 python3.10-venv

# Windows
# Download from python.org
```

---

## User Interface

### Streamlit 1.28+

**Purpose**: Web-based UI framework

**Official Site**: https://streamlit.io

**Key Features**:
- Pure Python (no HTML/CSS/JS)
- Reactive programming model
- Built-in widgets (file upload, sliders, etc.)
- Session state management
- Real-time updates

**Installation**:
```bash
pip install streamlit>=1.28.0
```

**Usage Example**:
```python
import streamlit as st

st.title("Speaker Diarization")
uploaded_file = st.file_uploader("Upload audio file")
if uploaded_file:
    st.audio(uploaded_file)
```

**Why Streamlit**:
- Fastest development time
- No frontend expertise required
- Built-in UI components
- Sufficient for internal tool

**Limitations**:
- Less customizable than React/Vue
- Desktop-focused (not mobile-optimized)
- Limited to Python backend

---

## Speaker Processing

### pyannote.audio 3.1+

**Purpose**: Speaker diarization and embedding extraction

**Official Site**: https://github.com/pyannote/pyannote-audio

**Key Features**:
- State-of-the-art speaker diarization
- Pretrained models available
- Speaker embedding extraction
- GPU acceleration support
- Active development

**Installation**:
```bash
pip install pyannote.audio>=3.1
```

**Authentication** (Required for Hugging Face models):
```bash
# Accept user agreement at:
# https://huggingface.co/pyannote/speaker-diarization
# https://huggingface.co/pyannote/segmentation

# Set token
export HUGGING_FACE_HUB_TOKEN=<your_token>
```

**Usage Example**:
```python
from pyannote.audio import Pipeline

# Diarization
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="<token>"
)

diarization = pipeline("audio.wav")

# Embedding extraction
from pyannote.audio import Inference

model = Inference("pyannote/embedding", window="whole")
embedding = model("audio.wav")
```

**Models Used**:
- `pyannote/speaker-diarization-3.1`: Main diarization pipeline
- `pyannote/embedding`: Speaker embedding extraction
- `pyannote/segmentation-3.0`: Voice activity detection

**Model Size**: ~500MB total (downloaded on first run)

**GPU Requirements**:
- Optional but highly recommended
- CUDA-compatible GPU (NVIDIA)
- 4GB+ VRAM
- 10-50x speedup vs CPU

**CPU Performance**:
- Acceptable for batch processing
- Too slow for real-time mode
- Recommend 4+ cores

---

## Speech-to-Text

### Azure Cognitive Services Speech SDK 1.30+

**Purpose**: Convert speech to text

**Official Site**: https://learn.microsoft.com/azure/cognitive-services/speech-service/

**Key Features**:
- High accuracy transcription
- Multiple languages support
- Real-time and batch modes
- Cloud and container deployment
- Punctuation and formatting

**Installation**:
```bash
pip install azure-cognitiveservices-speech>=1.30.0
```

**Usage Example**:
```python
import azure.cognitiveservices.speech as speechsdk

# Configuration
speech_config = speechsdk.SpeechConfig(
    subscription="<api_key>",
    region="eastus"
)

# From file
audio_config = speechsdk.audio.AudioConfig(filename="audio.wav")
recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config,
    audio_config=audio_config
)

result = recognizer.recognize_once()
print(result.text)
```

**Deployment Modes**:

**1. Cloud (Testing)**:
- Endpoint: `https://<region>.api.cognitive.microsoft.com`
- Authentication: API key or token
- Requires internet connection
- Pay-per-use pricing

**2. Container (Production)**:
- Endpoint: `http://localhost:5000` (or custom)
- Runs on-premises
- One-time license fee
- No data leaves network

**Container Setup**:
```bash
docker pull mcr.microsoft.com/azure-cognitive-services/speechservices/speech-to-text:latest

docker run --rm -it -p 5000:5000 \
  --memory 4g --cpus 2 \
  mcr.microsoft.com/azure-cognitive-services/speechservices/speech-to-text:latest \
  Eula=accept \
  Billing=<endpoint> \
  ApiKey=<key>
```

**Supported Languages** (Initial: English only):
- `en-US`: US English (default)
- `en-GB`: British English
- Future: Add more languages as needed

**Pricing** (Cloud):
- Standard: $1/hour
- Custom: $1.40/hour
- Container: One-time deployment fee

---

## Audio Processing

### librosa 0.10+

**Purpose**: Audio analysis and feature extraction

**Official Site**: https://librosa.org

**Key Features**:
- Load/save audio files
- Resampling
- Feature extraction
- Audio transformations

**Installation**:
```bash
pip install librosa>=0.10.0
```

**Usage Example**:
```python
import librosa

# Load audio
audio, sr = librosa.load("audio.mp3", sr=16000, mono=True)

# Get duration
duration = librosa.get_duration(y=audio, sr=sr)

# Resample
audio_8k = librosa.resample(audio, orig_sr=16000, target_sr=8000)
```

---

### soundfile 0.12+

**Purpose**: Audio file I/O

**Official Site**: https://github.com/bastibe/python-soundfile

**Key Features**:
- Read/write audio files
- Multiple format support
- Fast and efficient
- WAV, FLAC, OGG support

**Installation**:
```bash
pip install soundfile>=0.12.0
```

**Usage Example**:
```python
import soundfile as sf

# Read
data, samplerate = sf.read("audio.wav")

# Write
sf.write("output.wav", data, samplerate)

# Get info
info = sf.info("audio.wav")
print(info.duration, info.samplerate, info.channels)
```

---

### PyAudio 0.2.13+

**Purpose**: Audio device I/O for live mode

**Official Site**: https://people.csail.mit.edu/hubert/pyaudio/

**Key Features**:
- Capture audio from microphone
- Real-time audio streaming
- Cross-platform

**Installation**:
```bash
# macOS
brew install portaudio
pip install pyaudio

# Ubuntu
sudo apt install portaudio19-dev python3-pyaudio
pip install pyaudio

# Windows
pip install pyaudio
```

**Usage Example**:
```python
import pyaudio
import numpy as np

p = pyaudio.PyAudio()

# List devices
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

# Open stream
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024
)

# Read audio
data = stream.read(1024)
audio_chunk = np.frombuffer(data, dtype=np.int16)

stream.close()
p.terminate()
```

---

## Scientific Computing

### NumPy 1.24+

**Purpose**: Numerical array operations

**Official Site**: https://numpy.org

**Key Features**:
- Multi-dimensional arrays
- Mathematical functions
- Linear algebra
- Broadcasting

**Installation**:
```bash
pip install numpy>=1.24.0
```

**Usage in Project**:
- Speaker embeddings (512-dim vectors)
- Audio signal processing
- Similarity calculations

---

### SciPy 1.10+

**Purpose**: Scientific computing utilities

**Official Site**: https://scipy.org

**Key Features**:
- Cosine similarity
- Signal processing
- Statistical functions

**Installation**:
```bash
pip install scipy>=1.10.0
```

**Usage Example**:
```python
from scipy.spatial.distance import cosine

# Cosine similarity
similarity = 1 - cosine(embedding1, embedding2)
```

---

## Deep Learning

### PyTorch 2.0+

**Purpose**: Deep learning framework (backend for pyannote)

**Official Site**: https://pytorch.org

**Key Features**:
- GPU acceleration (CUDA)
- Neural network models
- Automatic differentiation

**Installation**:
```bash
# CPU only
pip install torch>=2.0.0

# With CUDA 11.8
pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cu118

# With CUDA 12.1
pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cu121
```

**Check GPU Availability**:
```python
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0)}")
```

---

## Utilities

### python-dotenv 1.0+

**Purpose**: Environment variable management

**Installation**:
```bash
pip install python-dotenv>=1.0.0
```

**Usage**:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file
api_key = os.getenv("AZURE_SPEECH_KEY")
```

**.env file example**:
```
AZURE_SPEECH_KEY=your_key_here
AZURE_REGION=eastus
HUGGING_FACE_HUB_TOKEN=your_token_here
```

---

### requests 2.31+

**Purpose**: HTTP client

**Installation**:
```bash
pip install requests>=2.31.0
```

**Usage**: Backup for Azure REST API calls

---

### pydub 0.25+

**Purpose**: Audio format conversion

**Installation**:
```bash
pip install pydub>=0.25.0

# Requires FFmpeg
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

**Usage Example**:
```python
from pydub import AudioSegment

# Convert MP3 to WAV
audio = AudioSegment.from_mp3("input.mp3")
audio.export("output.wav", format="wav")
```

---

## Development Tools

### pytest 7.4+

**Purpose**: Unit testing

**Installation**:
```bash
pip install pytest>=7.4.0
```

**Usage**:
```bash
pytest tests/
```

---

### black 23.0+

**Purpose**: Code formatting

**Installation**:
```bash
pip install black>=23.0.0
```

**Usage**:
```bash
black src/
```

---

### mypy 1.5+

**Purpose**: Static type checking

**Installation**:
```bash
pip install mypy>=1.5.0
```

**Usage**:
```bash
mypy src/
```

---

### pylint 2.17+

**Purpose**: Code linting

**Installation**:
```bash
pip install pylint>=2.17.0
```

**Usage**:
```bash
pylint src/
```

---

## Complete Requirements File

**`requirements.txt`**:
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
mypy>=1.5.0
pylint>=2.17.0
```

**Installation**:
```bash
pip install -r requirements.txt
```

---

## System Requirements

### Minimum Requirements

**Hardware**:
- CPU: Intel i5 or equivalent (4 cores)
- RAM: 8GB
- Disk: 10GB free space
- GPU: Optional (CPU-only mode supported)

**Software**:
- OS: macOS 11+, Windows 10+, Ubuntu 20.04+
- Python: 3.8+
- FFmpeg: Required for audio format support
- Internet: Required for initial model download and cloud mode

### Recommended Requirements

**Hardware**:
- CPU: Intel i7 or equivalent (8 cores)
- RAM: 16GB
- Disk: 20GB free space (SSD preferred)
- GPU: NVIDIA GTX 1660 or better (4GB+ VRAM)

**Software**:
- Python: 3.10 or 3.11
- CUDA: 11.8 or 12.1 (for GPU acceleration)
- Docker: For Azure Speech Container

---

## Environment Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `.env` file:
```
AZURE_SPEECH_KEY=your_key
AZURE_REGION=eastus
AZURE_MODE=cloud
HUGGING_FACE_HUB_TOKEN=your_token
```

### 4. Verify Installation

```python
# test_installation.py
import streamlit
import torch
from pyannote.audio import Pipeline
import azure.cognitiveservices.speech as speechsdk

print(f"Streamlit: {streamlit.__version__}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Azure Speech SDK: {speechsdk.__version__}")
print("✅ All dependencies installed successfully!")
```

Run:
```bash
python test_installation.py
```

---

## Version Compatibility Matrix

| Python | PyTorch | pyannote.audio | Streamlit | Azure SDK |
|--------|---------|----------------|-----------|-----------|
| 3.8 | 2.0+ | 3.1+ | 1.28+ | 1.30+ |
| 3.9 | 2.0+ | 3.1+ | 1.28+ | 1.30+ |
| 3.10 | 2.0+ | 3.1+ | 1.28+ | 1.30+ |
| 3.11 | 2.0+ | 3.1+ | 1.28+ | 1.30+ |
| 3.12 | ⚠️ Limited | ⚠️ Limited | 1.28+ | 1.30+ |

**Recommendation**: Use Python 3.10 or 3.11 for best compatibility.

---

## GPU Support

### CUDA Installation (NVIDIA GPUs)

**Check GPU**:
```bash
nvidia-smi
```

**Install CUDA Toolkit**:
- Download from: https://developer.nvidia.com/cuda-downloads
- Version: 11.8 or 12.1
- Follow platform-specific installation guide

**Install PyTorch with CUDA**:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Verify**:
```python
import torch
print(torch.cuda.is_available())  # Should print True
```

### Apple Silicon (M1/M2/M3)

PyTorch supports MPS (Metal Performance Shaders):
```python
import torch
print(torch.backends.mps.is_available())  # Should print True
device = torch.device("mps")
```

---

## Troubleshooting

### Issue: PyAudio installation fails

**Solution**:
```bash
# macOS
brew install portaudio
pip install pyaudio

# Ubuntu
sudo apt-get install portaudio19-dev
pip install pyaudio

# Windows
# Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio-0.2.13-cp310-cp310-win_amd64.whl
```

---

### Issue: pyannote models fail to download

**Solution**:
1. Accept user agreements on Hugging Face
2. Set authentication token:
```bash
export HUGGING_FACE_HUB_TOKEN=your_token
```

---

### Issue: CUDA out of memory

**Solution**:
- Reduce batch size in configuration
- Use CPU mode for small batches
- Close other GPU applications
- Upgrade GPU or use cloud GPU instance

---

### Issue: FFmpeg not found

**Solution**:
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
# Add to PATH
```

---

## Performance Optimization

### 1. Use GPU Acceleration
```python
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

### 2. Batch Processing
Process multiple files in parallel when possible

### 3. Model Caching
Models are cached after first download:
- Location: `~/.cache/torch/pyannote`
- Size: ~500MB

### 4. Audio Preprocessing
Convert to optimal format upfront:
- Sample rate: 16kHz
- Channels: Mono
- Format: WAV (uncompressed)

---

**Document Status**: Complete Reference  
**Last Updated**: October 21, 2025  
**Maintained By**: Development Team
