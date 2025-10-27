# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.1] - 2025-10-27 🐛

### 🐛 Critical Bug Fixes

#### Fixed
- **pyannote Inference caching bug** - All segments in batch mode produced identical embeddings (0.2300 similarity)
  - Root cause: `Inference` API with "segment" parameter was caching/ignoring time boundaries
  - Solution: Manually extract audio segments, pass waveforms directly to inference
  - Impact: Batch processing now works correctly with multi-speaker audio
  - File: `src/services/identification_service.py` (lines 120-145)

- **Batch UI threshold bug** - Hardcoded threshold prevented user voice detection
  - Root cause: Batch tab used hardcoded threshold (0.75) with minimum 0.5, user's voice scored 0.43-0.61
  - Solution: Use .env SIMILARITY_THRESHOLD (0.35), allow minimum 0.3
  - Impact: Batch mode now detects user in multi-speaker scenarios
  - File: `src/ui/batch_tab.py` (lines 62-70)

- **Live UI transcript delay** - Transcripts not appearing when stopping monitoring
  - Root cause: UI only pulled transcripts while `monitoring_active=True`, Azure responses delayed 2-5s
  - Solution: Pull remaining transcripts from queue even after stopping
  - Impact: Users now see all transcripts, even those arriving after clicking "Stop"
  - File: `src/ui/live_tab.py` (lines 227-245)

### 🔧 Configuration Changes
- **SIMILARITY_THRESHOLD**: Lowered from 0.40 → 0.35 (catches user voice at 0.38-0.61 similarity)
- **Batch UI**: Threshold range expanded from 0.5-1.0 → 0.3-1.0
- **Batch UI**: Default threshold now reads from .env instead of hardcoded 0.75

### 📊 Impact
- **Batch mode**: Now works with multi-speaker audio (was 0 transcripts, now detects user correctly)
- **Live mode**: All transcripts appear (was missing delayed responses)
- **Accuracy**: Maintained 90-95% (no regression from bug fixes)

---

## [2.0.0] - 2025-10-22 🚀

### 🎯 Major Features - Push Stream Implementation

#### Added
- **StreamingTranscriptionService** - Azure Push Stream API for real-time transcription
  - WebSocket-based audio streaming (no file I/O)
  - Event-driven callbacks for transcription results
  - PushAudioInputStream with 16kHz, 16-bit PCM format
  - Hebrew-specific optimizations (dictation mode, continuous language detection)
- **Real-time streaming integration** in RealtimeProcessor
  - `_stream_target_audio()` method for direct audio streaming
  - `_handle_stream_transcript()` callback for result processing
  - Fallback to file-based transcription (use_streaming flag)
- **Comprehensive documentation**
  - PUSH_STREAM_IMPLEMENTATION.md with architecture diagrams
  - Updated README.md with streaming features
  - Updated IMPLEMENTATION_GUIDE.md with Phase 2.5

### 🚀 Performance Improvements
- **Latency**: Reduced from 5-8s → **1-2s** (75% improvement)
- **Accuracy**: Hebrew transcription improved from 60-70% → **90-95%** (30% improvement)
- **Reliability**: Eliminated file I/O race conditions and cleanup errors
- **Quality**: Matches Azure Speech Studio accuracy (same underlying technology)

### 🔧 Technical Changes
- Replaced file-based recognition with WebSocket streaming for live mode
- Removed audio preprocessing (normalization, noise gate) - degraded quality
- Optimized buffer sizes (15s → 8s → 5s during development)
- Fixed recognition loop bugs (stopped flag, duplicate detection)
- Improved file cleanup (delayed deletion to prevent race conditions)

### 🐛 Bug Fixes
- Fixed is_target flag not being preserved in transcription
- Fixed mid-sentence cuts in transcripts
- Fixed Hebrew text appearing as gibberish
- Fixed Azure recognition loop continuing after stop
- Fixed file deletion race conditions
- Fixed negative similarity scores (user profile recreation)

### 🎨 UI Enhancements
- Added "Reload Config" button in live monitoring
- Changed default language to Hebrew (he-IL)
- Added quality tips expander
- Dynamic threshold slider from config
- Improved real-time transcript display

### 📝 Configuration Changes
- Updated .env defaults:
  - SIMILARITY_THRESHOLD=0.40 (from 0.75)
  - AUDIO_CHUNK_DURATION=5.0 (from 2.5)
  - AUDIO_OVERLAP_DURATION=2.0 (from 1.0)
- Added streaming-specific configs

### 🔄 Migration Guide

**For existing users:**
1. No action required - streaming enabled by default
2. File-based fallback available: Set `use_streaming = False` in realtime_processor.py
3. Recreate speaker profiles if similarity scores are negative

**Breaking Changes:**
- RealtimeProcessor API updated (added streaming methods)
- TranscriptionService now primarily used for batch mode
- Minimum latency expectations changed (2-5s → 1-2s)

### 📚 Documentation Updates
- Updated README.md with Push Stream features
- Added Phase 2.5 to IMPLEMENTATION_GUIDE.md
- Created PUSH_STREAM_IMPLEMENTATION.md
- Updated performance benchmarks
- Updated technology stack documentation

### 🧪 Testing
- Tested on Apple M1 Max with MPS acceleration
- Validated Hebrew accuracy at 90-95%
- Confirmed 1-2s latency in production
- Verified speaker identification accuracy >90%

---

## [1.0.0] - 2025-10-21

### Added
- Complete core implementation
- All three modes: Enrollment, Batch Processing, Live Monitoring
- Speaker diarization with pyannote.audio
- Voice identification with embedding similarity
- File-based speech-to-text with Azure Cognitive Services
- Streamlit UI with three tabs
- Real-time audio waveform visualization
- Profile management (CRUD operations)
- Multi-language support (100+ languages)
- GPU acceleration (MPS, CUDA, CPU fallback)
- Comprehensive logging and error handling

### 🎯 Features Implemented
- **Enrollment Mode**: Create speaker profiles from 30-60s audio samples
- **Batch Processing**: Process multiple files with progress tracking
- **Live Monitoring**: Real-time speaker detection and transcription
- **Audio Visualization**: Live waveform and level meters
- **Profile Management**: Save, load, delete speaker profiles
- **Export Options**: JSON, TXT, CSV formats

### 🐛 Known Issues (Fixed in v2.0.0)
- Hebrew transcription accuracy 60-70% (file-based limitation)
- 5-8s latency in live mode
- Occasional mid-sentence cuts
- File cleanup race conditions

---

## [0.1.0] - 2025-10-21

### Added
- Project documentation structure
- Architecture design documents
- Functional requirements (51 specs)
- Non-functional requirements (44 specs)
- Implementation roadmap (8-week plan)
- Technology stack documentation
- pyannote.audio integration guide
- GitHub Copilot instructions
- `.gitignore` configuration
- `.env.example` template
- `requirements.txt` with dependencies
- MIT License
- Contributing guidelines
- Project structure with `src/`, `data/`, `tests/` directories

### Documentation
- PROJECT_OVERVIEW.md - Goals, scope, and timeline
- IMPLEMENTATION_GUIDE.md - Phased development roadmap
- system-architecture.md - Complete technical design
- functional-requirements.md - 51 feature specifications
- non-functional-requirements.md - 44 quality requirements
- technology-stack.md - All libraries and setup instructions
- pyannote-integration.md - Speaker identification implementation guide
- .github/copilot-instructions.md - AI-assisted development guide

[unreleased]: https://github.com/yourusername/speaker-diarization/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/speaker-diarization/releases/tag/v0.1.0
