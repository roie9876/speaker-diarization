# Speaker Diarization & Selective Transcription System

🎤 Intelligent audio processing system that identifies a specific person's voice in group conversations and transcribes only their speech.

---

## 🎯 What Does This Do?

1. **Learn** a person's voice from reference audio samples
2. **Identify** when that person speaks in meeting recordings  
3. **Transcribe** only that person's speech (ignoring others)

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Azure Speech Service account
- Hugging Face account (for pyannote.audio models)

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

## 🚀 Features

### 1. 👤 Speaker Enrollment
- Upload reference audio of target speaker (30-60 seconds)
- System extracts voice "fingerprint" (512-dimensional embedding)
- Save speaker profile for future use

### 2. 📁 Batch Processing
- Upload multiple meeting recordings
- Select target speaker profile
- System processes all files:
  - Identifies when target speaker talks
  - Transcribes only their segments
- Export timestamped transcripts

### 3. 🔴 Live Monitoring
- Real-time audio capture from microphone
- Detect target speaker as they talk
- Live transcript display (2-5 second latency)
- Export session results

---

## 📚 Documentation

Comprehensive documentation available in [`docs/`](./docs/):

- **[GitHub Copilot Instructions](../.github/copilot-instructions.md)** - Quick implementation guide for AI assistants
- **[Project Overview](./docs/PROJECT_OVERVIEW.md)** - Goals, scope, and business context
- **[System Architecture](./docs/architecture/system-architecture.md)** - Technical design and components
- **[Implementation Guide](./docs/IMPLEMENTATION_GUIDE.md)** - Step-by-step development roadmap
- **[Functional Requirements](./docs/requirements/functional-requirements.md)** - 51 detailed feature specs
- **[Technology Stack](./docs/technical/technology-stack.md)** - All libraries and setup guides
- **[pyannote Integration](./docs/technical/pyannote-integration.md)** - Speaker identification implementation

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

## 🎯 How It Works

### Processing Pipeline

```
Audio Input
    ↓
[pyannote] Speaker Diarization → Segments per speaker
    ↓
[pyannote] Extract Embeddings → Voice fingerprints
    ↓
Compare with Target Profile
    ↓
If Match (similarity ≥ 0.75):
    ↓
[Azure Speech] Transcribe → Text
    ↓
Output: Timestamped transcript (target speaker only)
```

### Example Output

```
[00:01:23] This is what I said during the meeting.
[00:02:45] I think we should proceed with option A.
[00:05:12] Let me clarify my earlier point about the budget.
```

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

**Project Status**: ✅ Implementation Complete → Ready for Testing  
**Last Updated**: January 2025  
**Version**: 1.0.0

---

## 📂 Project Structure

```
speaker-diarization/
├── .github/                    # GitHub configuration
│   └── copilot-instructions.md # AI coding assistant instructions
├── src/                        # Source code
│   ├── config/                # Configuration management
│   ├── services/              # Core services (diarization, transcription, etc.)
│   ├── processors/            # Batch and realtime processors
│   ├── ui/                    # Streamlit UI components
│   └── utils/                 # Utilities (audio, logging)
├── tests/                     # Unit and integration tests
│   ├── fixtures/              # Test data and fixtures
│   ├── conftest.py           # Pytest configuration
│   ├── test_*.py             # Test files
│   └── verify_installation.py # Installation checker
├── docs/                      # Documentation
│   ├── architecture/          # System architecture docs
│   ├── requirements/          # Requirements specifications
│   ├── technical/             # Technical documentation
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── IMPLEMENTATION_STATUS.md
│   ├── PROJECT_OVERVIEW.md
│   └── QUICK_START.md        # User guide
├── data/                      # Data storage
│   ├── profiles/             # Speaker profiles (JSON)
│   ├── results/              # Processing results
│   └── temp/                 # Temporary files
├── logs/                      # Application logs
├── .env                       # Environment variables (not in repo)
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
└── README.md                 # This file
```

See [docs/PROJECT_STRUCTURE.txt](./docs/PROJECT_STRUCTURE.txt) for complete tree.
