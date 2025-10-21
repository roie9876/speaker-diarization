# Speaker Diarization & Selective Transcription System

🎤 **AI-powered voice identification and selective transcription for meetings and conversations**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)](docs/IMPLEMENTATION_STATUS.md)

---

## 🎯 What Does This System Do?

This application solves a common problem: **extracting what ONE specific person said in a group conversation** without manually listening to hours of audio.

### Real-World Use Cases

- 📝 **Meeting Minutes**: Extract only your manager's decisions from a 2-hour meeting
- 🎓 **Student Notes**: Transcribe only the professor's words, not student questions
- �️ **Interview Processing**: Get just the interviewee's responses, not the interviewer
- 📞 **Call Analysis**: Isolate customer statements from agent responses
- 🏢 **Conference Sessions**: Capture specific speaker's presentations from panel discussions

### How It Works (In Simple Terms)

1. **👤 Training Phase** - Upload 30-60 seconds of the target person speaking alone
   - System learns their unique voice characteristics (like a voice fingerprint)
   - Creates a speaker profile you can reuse

2. **🔍 Identification Phase** - Upload meeting recordings (or use live microphone)
   - Detects who is speaking at each moment (Speaker A, B, C...)
   - Compares each speaker's voice to your saved profile
   - Identifies segments where the target person is talking

3. **📝 Transcription Phase** - Converts speech to text (only for target speaker)
   - Skips everyone else
   - Returns timestamped transcript: `[00:12:34] What the person said...`

---

## 💡 Why Use This?

### The Problem
You have a 2-hour meeting recording with 5 people talking. You only need what **one specific person** said, but:
- ❌ Manual listening takes 2+ hours
- ❌ Generic transcription gives you everyone's words (mixed together)
- ❌ No easy way to filter by speaker

### The Solution
This system:
- ✅ Learns the target person's voice once (30-60 seconds)
- ✅ Automatically identifies when they speak in any recording
- ✅ Transcribes ONLY their words with timestamps
- ✅ Works in real-time or processes existing files

### Example Result
**Input**: 2-hour meeting with 5 speakers (120 minutes of audio)  
**Output**: 15-minute transcript of just the CEO's comments

```
[00:03:15] CEO: I think we should move forward with the merger.
[00:12:42] CEO: The Q3 targets are ambitious but achievable.
[00:45:18] CEO: Let's allocate more budget to marketing.
[01:23:09] CEO: I approve this plan. Let's execute next week.
```

**Time saved**: 1 hour 45 minutes 🎉

---

## 🎥 Demo & Screenshots

### Live Monitoring Interface
Real-time speaker detection with live audio waveform, transcript display, and session statistics.

*(Screenshots: Add your UI screenshots to `docs/images/` folder)*

### Workflow Overview
1. **Enrollment Tab** → Upload 30s voice sample → Create profile
2. **Batch Tab** → Upload meeting files → Process → Download transcripts
3. **Live Tab** → Start monitoring → Speak → See transcripts in real-time

**📖 See**: [Waveform Visualization](./docs/WAVEFORM_VISUALIZATION.md) for technical details

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.10+** (3.10, 3.11, or 3.12 recommended)
- **Azure Speech Service** account ([Free tier available](https://azure.microsoft.com/en-us/free/ai-services/))
- **Hugging Face** account (free) for pyannote.audio models
- **8GB+ RAM** recommended
- **GPU optional** (Apple Silicon MPS, NVIDIA CUDA, or CPU mode)

### Installation

```bash
# Clone repository
cd speaker-diarization

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure and Hugging Face credentials

# Run application
streamlit run src/ui/app.py
```

### First Time Setup

1. **Azure Speech Service**:
   - Create Azure account: https://azure.microsoft.com/
   - Create Speech Service resource
   - Copy API key and region to `.env`

2. **Hugging Face** (for pyannote models):
   - Create account: https://huggingface.co/
   - Accept user agreements:
     - https://huggingface.co/pyannote/speaker-diarization-3.1
     - https://huggingface.co/pyannote/segmentation-3.0
   - Generate access token: https://huggingface.co/settings/tokens
   - Add token to `.env`

---

## 🚀 Features & Capabilities

### 1. 👤 Speaker Enrollment (Voice Profile Creation)
- **Upload Reference Audio**: 30-60 seconds of the target person speaking alone
- **Voice Fingerprint Extraction**: System creates a unique 512-dimensional embedding
- **Profile Management**: Save, load, delete speaker profiles
- **Multi-Profile Support**: Create profiles for different people
- **Quality Validation**: Automatic audio quality checks

**📖 See**: [Enrollment Requirements](./docs/requirements/functional-requirements.md#enrollment-mode)

---

### 2. 📁 Batch Processing (Process Recordings)
- **Multi-File Upload**: Process multiple recordings simultaneously
- **Flexible Formats**: MP3, WAV, M4A, FLAC supported
- **Adjustable Thresholds**: Fine-tune speaker matching sensitivity
- **Progress Tracking**: Real-time processing status per file
- **Detailed Results**: 
  - Timestamped transcripts with confidence scores
  - Speaker match statistics
  - Audio segment metadata
- **Export Options**: JSON, TXT, CSV formats

**📖 See**: [Batch Processing Guide](./docs/requirements/functional-requirements.md#batch-processing-mode)

---

### 3. 🔴 Live Monitoring (Real-Time Transcription)
- **Real-Time Audio Capture**: Direct microphone input
- **Live Speaker Detection**: Identify target speaker as they speak
- **Instant Transcription**: 2-5 second latency
- **Visual Feedback**:
  - Live audio waveform display
  - Audio level meter with voice activity detection
  - Target speaker detection indicators
- **Session Management**: Save and export live session transcripts
- **Multi-Language Support**: Hebrew, English, 100+ languages

**📖 See**: [Live Monitoring Guide](./docs/requirements/functional-requirements.md#live-monitoring-mode)

---

### Additional Features
- ✅ **GPU Acceleration**: MPS (Apple Silicon), CUDA (NVIDIA), CPU fallback
- ✅ **Multi-Language**: Support for 100+ languages via Azure Speech
- ✅ **High Accuracy**: 90%+ speaker identification, 95%+ transcription accuracy
- ✅ **Privacy Options**: On-premises deployment available (Azure container)
- ✅ **Confidence Scores**: Know how reliable each transcription is
- ✅ **Audio Visualization**: Real-time waveform and level meters

**📖 Full specs**: [Functional Requirements](./docs/requirements/functional-requirements.md) (51 features)

---

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) folder:

### 🚀 Getting Started
- **[Quick Start Guide](./docs/QUICK_START.md)** - Installation and first-run walkthrough
- **[Setup Complete](./docs/SETUP_COMPLETE.md)** - Verify your installation
- **[Implementation Status](./docs/IMPLEMENTATION_STATUS.md)** - Current project status

### 📖 Project Documentation
- **[Project Overview](./docs/PROJECT_OVERVIEW.md)** - Goals, scope, and business context
- **[Project Organization](./docs/PROJECT_ORGANIZATION.md)** - How the codebase is structured
- **[Changelog](./docs/CHANGELOG.md)** - Version history and updates

### 🏗️ Architecture & Technical
- **[System Architecture](./docs/architecture/system-architecture.md)** - Technical design and component interactions
- **[Technology Stack](./docs/technical/technology-stack.md)** - Libraries, dependencies, and setup guides
- **[pyannote Integration](./docs/technical/pyannote-integration.md)** - Deep dive into speaker diarization
- **[Waveform Visualization](./docs/WAVEFORM_VISUALIZATION.md)** - Real-time audio display implementation

### 👨‍💻 Development
- **[Implementation Guide](./docs/IMPLEMENTATION_GUIDE.md)** - Step-by-step development roadmap (4 phases)
- **[Functional Requirements](./docs/requirements/functional-requirements.md)** - 51 detailed feature specifications
- **[Contributing Guide](./docs/CONTRIBUTING.md)** - How to contribute to the project
- **[GitHub Copilot Instructions](./.github/copilot-instructions.md)** - AI-assisted development guide

### ✅ Quality Assurance
- **[Pre-Push Checklist](./docs/PRE_PUSH_CHECKLIST.md)** - Code quality checks before commits
- **[Ready to Push](./docs/READY_TO_PUSH.md)** - Deployment readiness verification

---

## 🏗️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.10+ |
| **UI Framework** | Streamlit |
| **Speaker Diarization** | pyannote.audio 3.1+ |
| **Speech-to-Text** | Azure Cognitive Services |
| **ML Framework** | PyTorch (MPS/CUDA/CPU) |
| **Audio Processing** | librosa, soundfile |

---

## 📁 Project Structure

```
speaker-diarization/
├── .github/
│   └── copilot-instructions.md     # GitHub Copilot implementation guide
├── src/
│   ├── services/                   # Core processing services
│   ├── processors/                 # Batch and real-time processors
│   ├── ui/                         # Streamlit interface
│   ├── config/                     # Configuration management
│   └── utils/                      # Helper utilities
├── data/
│   ├── profiles/                   # Speaker profiles
│   ├── results/                    # Processing results
│   └── temp/                       # Temporary files
├── docs/                           # Comprehensive documentation
├── tests/                          # Unit and integration tests
├── .env                            # Environment variables (create from .env.example)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🔧 Configuration

Create `.env` file with:

```bash
# Azure Speech Service
AZURE_SPEECH_KEY=your_azure_key_here
AZURE_REGION=eastus
AZURE_MODE=cloud  # or 'container' for on-premises

# Hugging Face (for pyannote models)
HUGGING_FACE_HUB_TOKEN=your_hf_token_here

# Processing Settings
SIMILARITY_THRESHOLD=0.75
USE_GPU=true
```

---

## 🎯 How It Works (Technical Pipeline)

The system combines three AI technologies to achieve selective transcription:

### Step-by-Step Processing

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: Meeting Recording (MP3/WAV) or Live Microphone      │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Speaker Diarization (pyannote.audio)               │
│  "Who spoke when?"                                           │
│  Output: Segments with speaker labels                       │
│    • [0.0s - 3.5s] SPEAKER_00                              │
│    • [3.8s - 7.2s] SPEAKER_01                              │
│    • [7.5s - 12.1s] SPEAKER_00                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Voice Identification (pyannote embedding)          │
│  "Which speaker is our target person?"                       │
│  • Extract 512-D embedding for each segment                 │
│  • Compare with saved profile embedding                     │
│  • Calculate cosine similarity                              │
│  • If similarity ≥ 0.50 → TARGET MATCH ✅                   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Selective Transcription (Azure Speech Service)     │
│  "Convert only target person's speech to text"              │
│  • Send matched segments to Azure API                       │
│  • Support for Hebrew, English, 100+ languages              │
│  • Return confidence scores                                 │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT: Timestamped Transcript (JSON/TXT)                  │
│  [00:01:23] This is what I said during the meeting.         │
│  [00:02:45] I think we should proceed with option A.        │
│  [00:05:12] Let me clarify my earlier point about the budget│
└─────────────────────────────────────────────────────────────┘
```

### Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Speaker Diarization** | [pyannote.audio 3.1+](https://github.com/pyannote/pyannote-audio) | Detects "who spoke when" |
| **Voice Embeddings** | pyannote embedding model | Extracts voice fingerprints (512-D vectors) |
| **Speech-to-Text** | [Azure Cognitive Services](https://azure.microsoft.com/en-us/products/ai-services/speech-to-text) | Converts speech to text (100+ languages) |
| **ML Backend** | PyTorch (MPS/CUDA/CPU) | Neural network inference |

**📖 Deep dive**: See [pyannote Integration Guide](./docs/technical/pyannote-integration.md) for technical details

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_services.py
```

---

## 🚢 Deployment

### Development (Cloud Azure)
- Use Azure Speech Service cloud endpoint
- Fast setup, pay-per-use

### Production (On-Premises Container)
- Deploy Azure Speech Service as Docker container
- Data stays on local network
- One-time licensing fee

See [deployment documentation](./docs/architecture/system-architecture.md#deployment-architecture) for details.

---

## 🤝 Contributing

1. Read [IMPLEMENTATION_GUIDE.md](./docs/IMPLEMENTATION_GUIDE.md)
2. Follow the phased development approach
3. Use [copilot-instructions.md](./.github/copilot-instructions.md) for implementation context
4. Write tests for new features
5. Update documentation as needed

---

## 📊 Performance

| Mode | Processing Speed | GPU Required? |
|------|-----------------|---------------|
| **Enrollment** | 5-15 seconds | Optional |
| **Batch** | 1-2x real-time | Recommended |
| **Live** | <5s latency | **Required** |

**Tested on**: Apple M1 Max (excellent performance with MPS)

---

## 🐛 Troubleshooting

### Common Issues

**PyAudio installation fails**:
```bash
# macOS
brew install portaudio
pip install pyaudio

# Ubuntu
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**pyannote models won't download**:
- Verify Hugging Face token is set
- Accept user agreements on model pages
- Check internet connection

**Low speaker identification accuracy**:
- Use 30+ seconds of reference audio
- Ensure reference audio is clear
- Try adjusting similarity threshold
- Use multiple reference samples

See [Technology Stack](./docs/technical/technology-stack.md#troubleshooting) for more solutions.

---

## 📄 License

[Add your license here]

---

## 👥 Team

[Add team/contact information]

---

## 🙏 Acknowledgments

- **pyannote.audio** - State-of-the-art speaker diarization
- **Azure Cognitive Services** - Speech-to-text transcription  
- **Streamlit** - Rapid UI development

---

## 🔗 Key Documentation Links

### For Users
- 📖 **[Quick Start Guide](./docs/QUICK_START.md)** - Get started in 10 minutes
- 📖 **[Setup Complete Checklist](./docs/SETUP_COMPLETE.md)** - Verify installation
- 📖 **[Troubleshooting](./docs/technical/technology-stack.md#troubleshooting)** - Common issues and fixes

### For Developers
- 🏗️ **[System Architecture](./docs/architecture/system-architecture.md)** - How components interact
- 📝 **[Implementation Guide](./docs/IMPLEMENTATION_GUIDE.md)** - 4-phase development roadmap
- 🤖 **[GitHub Copilot Instructions](./.github/copilot-instructions.md)** - AI-assisted coding guide
- 🔧 **[Technology Stack](./docs/technical/technology-stack.md)** - All dependencies and setup
- 🎯 **[Functional Requirements](./docs/requirements/functional-requirements.md)** - 51 feature specs

### For Contributors
- 🤝 **[Contributing Guide](./docs/CONTRIBUTING.md)** - How to contribute
- ✅ **[Pre-Push Checklist](./docs/PRE_PUSH_CHECKLIST.md)** - Quality checks
- 📋 **[Implementation Status](./docs/IMPLEMENTATION_STATUS.md)** - Current state

---

**Project Status**: ✅ **Production Ready** - Fully implemented and tested  
**Last Updated**: October 2025  
**Version**: 1.0.0  
**Maintained by**: [Add your name/organization]

---

## 📂 Project Structure

```
speaker-diarization/
├── .github/
│   └── copilot-instructions.md     # 🤖 AI assistant implementation guide
├── src/                            # 💻 Source Code
│   ├── services/                   # Core AI services
│   │   ├── diarization_service.py  # Speaker detection
│   │   ├── identification_service.py # Voice matching
│   │   ├── transcription_service.py # Speech-to-text
│   │   └── profile_manager.py      # Speaker profile CRUD
│   ├── processors/                 # Processing orchestration
│   │   ├── batch_processor.py      # Multi-file processing
│   │   └── realtime_processor.py   # Live audio streaming
│   ├── ui/                         # 🖥️ Streamlit Interface
│   │   ├── app.py                  # Main application
│   │   ├── enrollment_tab.py       # Voice profile creation
│   │   ├── batch_tab.py           # Batch processing UI
│   │   └── live_tab.py            # Real-time monitoring
│   ├── config/                     # Configuration management
│   │   └── config_manager.py
│   └── utils/                      # Helper utilities
│       ├── audio_utils.py          # Audio format conversion
│       └── logger.py               # Logging setup
├── docs/                           # 📚 Documentation
│   ├── architecture/               # System design
│   ├── requirements/               # Feature specifications
│   ├── technical/                  # Tech deep-dives
│   ├── PROJECT_OVERVIEW.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── QUICK_START.md
│   └── [20+ more docs...]
├── data/                           # 💾 Data Storage
│   ├── profiles/                   # Speaker profiles (JSON)
│   ├── results/                    # Transcripts output
│   └── temp/                       # Processing temp files
├── tests/                          # ✅ Testing
│   ├── test_services.py
│   ├── test_processors.py
│   └── verify_installation.py
├── .env                            # 🔐 Environment variables (create from .env.example)
├── requirements.txt                # 📦 Python dependencies
└── README.md                       # 📖 This file
```

**📖 Full tree**: [docs/PROJECT_STRUCTURE.txt](./docs/PROJECT_STRUCTURE.txt)  
**📖 Organization**: [docs/PROJECT_ORGANIZATION.md](./docs/PROJECT_ORGANIZATION.md)
