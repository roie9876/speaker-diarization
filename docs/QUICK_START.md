# Speaker Diarization System - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Azure Speech Service account
- Hugging Face account
- Microphone (for live monitoring)

### Installation

1. **Run the setup script:**
```bash
chmod +x setup.sh
./setup.sh
```

2. **Configure environment variables:**
Edit `.env` file with your credentials:
```bash
# Azure Speech Service
AZURE_SPEECH_KEY=your_azure_key
AZURE_REGION=eastus

# Hugging Face (for pyannote models)
HUGGING_FACE_HUB_TOKEN=your_hf_token
```

3. **Accept Hugging Face model agreements:**
- Visit: https://huggingface.co/pyannote/speaker-diarization-3.1
- Visit: https://huggingface.co/pyannote/segmentation-3.0
- Click "Agree and access repository" on both pages

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
streamlit run src/ui/app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Enrollment Tab 👤

**Create Speaker Profile:**
1. Enter speaker name
2. Upload reference audio file (WAV, MP3, M4A, or FLAC)
3. Preview audio to ensure quality
4. Click "Create Profile"

**Manage Profiles:**
- Search profiles by name
- Select profile for batch/live processing
- Delete unwanted profiles
- Export/import profiles for backup

**Tips:**
- Use 10-30 seconds of clear audio
- Avoid background noise
- Multiple sentences work best
- The speaker should be the only person talking

### 2. Batch Processing Tab 📁

**Process Audio Files:**
1. Select target speaker from dropdown
2. Adjust similarity threshold (0.75 default)
3. Choose transcription language
4. Upload one or more audio files
5. Click "Start Processing"

**View Results:**
- Summary statistics (segments, match rate, etc.)
- Individual file results with timestamps
- Transcripts with confidence scores
- Export as JSON or text

**Tips:**
- Higher threshold = fewer false positives
- Lower threshold = catch more instances
- Process multiple files in one batch
- Results are saved automatically

### 3. Live Monitoring Tab 🔴

**Real-Time Transcription:**
1. Select audio input device
2. Choose target speaker profile
3. Set similarity threshold
4. Click "Start Monitoring"
5. Speak naturally into microphone

**Features:**
- Live audio level meter
- Real-time transcript display
- Session statistics
- Save/export session transcripts

**Tips:**
- Test audio levels before starting
- Position microphone appropriately
- Minimize background noise
- Stop monitoring to export session

## 🔧 Configuration

### Similarity Threshold
- **0.65-0.70**: Permissive (catches more, more false positives)
- **0.75**: Balanced (recommended default)
- **0.80-0.85**: Strict (fewer false positives, may miss some)

### Audio Requirements
- **Format**: WAV, MP3, M4A, FLAC
- **Sample Rate**: 16kHz (auto-converted)
- **Channels**: Mono (auto-converted from stereo)
- **Duration**: Minimum 1 second

### GPU Acceleration
The system automatically detects and uses:
- **Apple Silicon (M1/M2/M3)**: MPS backend
- **NVIDIA GPUs**: CUDA backend
- **Fallback**: CPU (slower but works)

## 🐛 Troubleshooting

### pyaudio Installation Fails
**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### "No audio devices found"
- Check microphone permissions in System Preferences
- Ensure microphone is connected
- Restart application

### "Import pyannote.audio failed"
- Verify Hugging Face token in `.env`
- Accept model agreements on Hugging Face
- Check internet connection (models download on first run)

### "Azure Speech Service error"
- Verify `AZURE_SPEECH_KEY` in `.env`
- Check `AZURE_REGION` matches your service region
- Ensure Azure subscription is active

### Models downloading slowly
- First run downloads ~500MB of models
- Subsequent runs use cached models
- Check internet connection

## 📊 File Structure

```
speaker-diarization/
├── src/
│   ├── config/          # Configuration management
│   ├── services/        # Core services (diarization, transcription, etc.)
│   ├── processors/      # Batch and real-time processors
│   ├── ui/              # Streamlit UI components
│   └── utils/           # Audio utilities and logging
├── data/
│   ├── profiles/        # Speaker profile JSON files
│   ├── results/         # Processing results
│   └── temp/            # Temporary files
├── logs/                # Application logs
├── .env                 # Environment variables (create from .env.example)
└── requirements.txt     # Python dependencies
```

## 🔐 Security Notes

- Keep `.env` file secure (contains API keys)
- Don't commit `.env` to version control
- Use environment-specific keys for production
- Rotate API keys regularly

## 📝 Additional Resources

- **Full Documentation**: See `docs/` directory
- **Implementation Guide**: `docs/IMPLEMENTATION_GUIDE.md`
- **Architecture**: `docs/architecture/system-architecture.md`
- **Requirements**: `docs/requirements/functional-requirements.md`

## 🎯 Common Use Cases

### Meeting Transcription
1. Enroll yourself or key participants
2. Upload meeting recording in batch mode
3. Get transcript of only your speech
4. Export for review/sharing

### Podcast Editing
1. Enroll podcast host
2. Process episode files
3. Get timestamped segments
4. Use for editing/highlight reels

### Live Event Monitoring
1. Enroll target speaker
2. Start live monitoring
3. Real-time transcription appears
4. Export session after event

## 💡 Best Practices

### For Best Accuracy:
- Use high-quality reference audio
- Minimize background noise
- Ensure clear pronunciation
- Use appropriate similarity threshold
- Test with sample files first

### For Performance:
- Enable GPU if available
- Process files in batches
- Use appropriate audio quality
- Close unnecessary applications

### For Reliability:
- Keep profiles backed up (export feature)
- Monitor processing logs
- Validate results periodically
- Update dependencies regularly

## 🆘 Getting Help

If you encounter issues:
1. Check logs in `logs/` directory
2. Review troubleshooting section above
3. Verify configuration in `.env`
4. Check Azure/Hugging Face service status

## 📄 License

See LICENSE file for details.

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: January 2025
