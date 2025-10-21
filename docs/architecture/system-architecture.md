# System Architecture

## Document Information

- **Project**: Speaker Diarization & Selective Transcription System
- **Version**: 1.0
- **Date**: October 21, 2025
- **Status**: Design Document

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Context](#system-context)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)
7. [Design Decisions](#design-decisions)

---

## Architecture Overview

### High-Level Architecture

The system follows a **layered architecture** pattern with clear separation between presentation, business logic, and data layers.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│                     (Streamlit UI)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Enrollment  │  │ Batch Mode   │  │  Live Mode   │         │
│  │     UI       │  │     UI       │  │     UI       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Profile    │  │    Batch     │  │  Real-Time   │         │
│  │   Manager    │  │  Processor   │  │  Processor   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌────────────────────────────────────────────────┐            │
│  │        Configuration Manager                    │            │
│  └────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                              │
│  ┌───────────────────────────────────────────────┐             │
│  │         Speaker Diarization Service           │             │
│  │            (pyannote.audio)                   │             │
│  └───────────────────────────────────────────────┘             │
│                            ↕                                     │
│  ┌───────────────────────────────────────────────┐             │
│  │        Speaker Identification Service         │             │
│  │       (Embedding Extraction & Matching)       │             │
│  └───────────────────────────────────────────────┘             │
│                            ↕                                     │
│  ┌───────────────────────────────────────────────┐             │
│  │         Transcription Service                 │             │
│  │       (Azure Speech Service Client)           │             │
│  └───────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Speaker    │  │  Processing  │  │    Config    │         │
│  │   Profiles   │  │   Results    │  │   Storage    │         │
│  │   (JSON)     │  │   (JSON/TXT) │  │   (JSON)     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **Modularity**: Components can be developed and tested independently
3. **Extensibility**: Easy to add new features or replace components
4. **Configuration-Driven**: Behavior controlled through configuration, not code changes
5. **Error Resilience**: Failures in one component don't crash entire system

---

## System Context

### External Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│                    Speaker Diarization System                    │
└─────────────────────────────────────────────────────────────────┘
    ↓                           ↓                        ↓
┌──────────┐            ┌──────────────┐         ┌─────────────┐
│  Audio   │            │    Azure     │         │  pyannote   │
│  Input   │            │    Speech    │         │  Models     │
│  Files   │            │   Service    │         │ (Hugging    │
│  or Mic  │            │ (Cloud/Cont.)│         │   Face)     │
└──────────┘            └──────────────┘         └─────────────┘
```

### Integration Points

1. **Audio Input Sources**
   - Local audio files (upload)
   - Microphone/audio devices (live mode)
   - File system for batch processing

2. **Azure Speech Service**
   - Cloud endpoint: `https://<region>.api.cognitive.microsoft.com`
   - Container endpoint: `http://localhost:5000` (or custom)
   - Authentication: API key or token

3. **pyannote.audio Models**
   - Downloaded from Hugging Face Hub
   - Cached locally after first download
   - Models: `pyannote/speaker-diarization`, `pyannote/embedding`

4. **Local Storage**
   - Speaker profiles directory
   - Results/transcripts directory
   - Configuration files
   - Temporary processing files
   - Log files

---

## Component Architecture

### 1. Presentation Layer (Streamlit UI)

**Responsibility**: User interaction and display

**Components**:

#### 1.1 Enrollment UI
- File upload widget
- Audio player component
- Speaker name input
- Profile management list
- Status/error messages

#### 1.2 Batch Processing UI
- Multi-file uploader
- Profile selector dropdown
- Settings panel (threshold, endpoint)
- Progress tracking display
- Results table
- Export controls

#### 1.3 Live Mode UI
- Audio device selector
- Real-time status indicators
- Live transcript display
- Audio level meter
- Session controls (start/stop/export)

**Technology**: Streamlit (Python framework)

**Key Features**:
- Single-page application with tabs
- Real-time updates via Streamlit's reactive model
- Session state management for persistence
- Component-based structure

---

### 2. Application Layer

**Responsibility**: Business logic orchestration

#### 2.1 Profile Manager

**Responsibilities**:
- Create speaker profiles from reference audio
- Store and retrieve profiles
- Manage profile metadata
- Validate profile data
- Support multiple samples per profile

**Interface**:
```python
class ProfileManager:
    def create_profile(audio_file, speaker_name) -> Profile
    def get_profile(profile_id) -> Profile
    def list_profiles() -> List[Profile]
    def delete_profile(profile_id) -> bool
    def add_sample(profile_id, audio_file) -> bool
```

**Data Model**:
```python
Profile:
    - id: str
    - name: str
    - embedding: np.array (512-dim)
    - samples_count: int
    - created_date: datetime
    - metadata: dict
```

---

#### 2.2 Batch Processor

**Responsibilities**:
- Manage batch job queue
- Coordinate processing pipeline for multiple files
- Track progress and status
- Handle errors per file
- Aggregate results

**Interface**:
```python
class BatchProcessor:
    def add_files(file_list) -> BatchJob
    def set_target_profile(profile_id)
    def configure(settings: BatchSettings)
    def start_processing() -> Iterator[Progress]
    def get_results() -> BatchResults
    def cancel_job()
```

**Processing Workflow**:
1. Validate input files
2. For each file (parallel or sequential):
   - Call Diarization Service
   - Call Identification Service
   - Call Transcription Service (if target found)
   - Store results
3. Generate summary report

---

#### 2.3 Real-Time Processor

**Responsibilities**:
- Manage audio stream from input device
- Implement buffering strategy
- Coordinate real-time pipeline
- Maintain low latency
- Handle continuous operation

**Interface**:
```python
class RealtimeProcessor:
    def select_audio_device(device_id)
    def set_target_profile(profile_id)
    def configure(settings: LiveSettings)
    def start_monitoring() -> Iterator[TranscriptChunk]
    def stop_monitoring()
    def get_session_transcript() -> Transcript
```

**Buffering Strategy**:
- Sliding window: 3-second buffers with 1-second overlap
- Circular buffer for audio data
- Async processing to maintain real-time performance

---

#### 2.4 Configuration Manager

**Responsibilities**:
- Load and save application settings
- Provide default configurations
- Validate configuration values
- Support environment variables
- Manage Azure endpoint settings

**Interface**:
```python
class ConfigManager:
    def load_config() -> Config
    def save_config(config: Config)
    def get(key: str) -> Any
    def set(key: str, value: Any)
    def reset_to_defaults()
```

**Configuration Structure**:
```yaml
azure:
  mode: cloud  # or container
  cloud_endpoint: https://region.api.cognitive.microsoft.com
  container_endpoint: http://localhost:5000
  api_key: <encrypted>
  region: eastus

processing:
  similarity_threshold: 0.75
  parallel_processing: true
  max_workers: 4
  buffer_duration: 3.0

storage:
  profiles_dir: ./data/profiles
  results_dir: ./data/results
  temp_dir: ./data/temp
  logs_dir: ./logs

ui:
  default_tab: enrollment
  auto_export: false
  include_timestamps: true
  include_confidence: true
```

---

### 3. Processing Layer

#### 3.1 Speaker Diarization Service

**Responsibility**: Separate audio into speaker segments

**Technology**: pyannote.audio

**Interface**:
```python
class DiarizationService:
    def __init__(model_name="pyannote/speaker-diarization")
    def diarize(audio_file) -> Diarization
    def diarize_chunk(audio_chunk) -> Diarization
```

**Output Format**:
```python
Diarization:
    - segments: List[Segment]
        Segment:
            - start_time: float
            - end_time: float
            - speaker_label: str (e.g., "SPEAKER_00")
```

**Implementation Details**:
- Uses pretrained pipeline from pyannote
- Configurable min_speakers and max_speakers
- GPU acceleration supported
- Handles mono and stereo audio (converts to mono)

---

#### 3.2 Speaker Identification Service

**Responsibility**: Extract embeddings and match against target profile

**Technology**: pyannote.audio embedding models

**Interface**:
```python
class IdentificationService:
    def __init__(model_name="pyannote/embedding")
    def extract_embedding(audio_segment) -> np.array
    def compare_embeddings(emb1, emb2) -> float  # similarity score
    def identify_speaker(audio_segment, target_profile, threshold) -> bool
```

**Matching Algorithm**:
1. Extract embedding from audio segment (512-dim vector)
2. Compute cosine similarity with target profile embedding
3. Return True if similarity ≥ threshold, else False

**Similarity Calculation**:
```python
similarity = cosine_similarity(embedding1, embedding2)
# Result: 0.0 (completely different) to 1.0 (identical)
```

**Threshold Tuning**:
- Default: 0.75
- Strict: 0.85+ (fewer false positives)
- Permissive: 0.65+ (catch more segments)

---

#### 3.3 Transcription Service

**Responsibility**: Convert speech to text using Azure Speech Service

**Technology**: Azure Cognitive Services Speech SDK

**Interface**:
```python
class TranscriptionService:
    def __init__(endpoint, api_key)
    def transcribe_file(audio_file) -> Transcript
    def transcribe_chunk(audio_chunk) -> str
    def set_language(language_code)
```

**Azure Integration**:
- Supports both REST API and SDK
- Handles authentication (API key or token)
- Automatic retry on transient failures
- Timeout handling

**Output Format**:
```python
Transcript:
    - text: str
    - segments: List[TranscriptSegment]
        TranscriptSegment:
            - text: str
            - start_time: float
            - end_time: float
            - confidence: float
```

**Endpoint Abstraction**:
```python
class AzureSpeechClient:
    def __init__(config: AzureConfig):
        if config.mode == "cloud":
            self.endpoint = config.cloud_endpoint
        else:
            self.endpoint = config.container_endpoint
```

---

### 4. Data Layer

#### 4.1 Speaker Profiles Storage

**Format**: JSON files, one per speaker

**File Structure**:
```
data/profiles/
    ├── profile_001.json
    ├── profile_002.json
    └── ...
```

**Profile File Schema**:
```json
{
  "id": "profile_001",
  "name": "John Doe",
  "embedding": [0.123, -0.456, ...],  // 512 values
  "samples_count": 2,
  "created_date": "2025-10-21T10:30:00",
  "last_updated": "2025-10-21T14:45:00",
  "metadata": {
    "audio_duration": 45.3,
    "quality_score": 0.89
  }
}
```

---

#### 4.2 Processing Results Storage

**Format**: JSON and TXT files

**File Structure**:
```
data/results/
    ├── batch_20251021_143000/
    │   ├── meeting1_transcript.txt
    │   ├── meeting1_data.json
    │   ├── meeting2_transcript.txt
    │   ├── meeting2_data.json
    │   └── batch_summary.json
    └── live_20251021_150000/
        ├── session_transcript.txt
        └── session_data.json
```

**Transcript TXT Format**:
```
[00:01:23] This is the first segment of speech.
[00:02:45] This is another segment.
...
```

**Data JSON Schema**:
```json
{
  "file_name": "meeting1.wav",
  "processed_date": "2025-10-21T14:30:00",
  "target_speaker": "John Doe",
  "settings": {
    "threshold": 0.75,
    "endpoint": "cloud"
  },
  "results": {
    "target_detected": true,
    "total_segments": 15,
    "target_segments": 7,
    "total_duration": 300.5,
    "target_duration": 45.2,
    "average_confidence": 0.87
  },
  "segments": [
    {
      "start_time": 83.2,
      "end_time": 89.7,
      "speaker_match": true,
      "confidence": 0.92,
      "transcript": "This is what I said during the meeting."
    }
  ]
}
```

---

#### 4.3 Configuration Storage

**Format**: JSON file

**Location**: `config/settings.json`

**Schema**: See Configuration Manager section above

---

## Data Flow

### Enrollment Flow

```
User uploads audio
    ↓
[Presentation Layer] Validate file format
    ↓
[Profile Manager] Create profile request
    ↓
[Identification Service] Extract embedding
    ↓
[Data Layer] Save profile JSON
    ↓
[Presentation Layer] Display success
```

---

### Batch Processing Flow

```
User uploads files + selects profile + clicks "Process"
    ↓
[Batch Processor] Create batch job
    ↓
For each file:
    [Diarization Service] Split into speaker segments
        ↓
    For each segment:
        [Identification Service] Extract embedding & compare
            ↓
        If match:
            [Transcription Service] Send to Azure STT
                ↓
            Collect transcript
    ↓
[Data Layer] Save results (JSON + TXT)
    ↓
[Presentation Layer] Display results table
```

---

### Live Mode Flow

```
User selects device + profile + clicks "Start"
    ↓
[Real-Time Processor] Open audio stream
    ↓
Continuous loop:
    Capture 3-second audio buffer
        ↓
    [Diarization Service] Identify speakers in buffer
        ↓
    [Identification Service] Check if target speaker
        ↓
    If match:
        [Transcription Service] Send to Azure STT
            ↓
        [Presentation Layer] Update live transcript display
    ↓
User clicks "Stop"
    ↓
[Data Layer] Save session transcript
    ↓
[Presentation Layer] Offer export
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.8+ | Primary development language |
| **UI Framework** | Streamlit | 1.28+ | User interface |
| **Speaker Diarization** | pyannote.audio | 3.1+ | Diarization and embeddings |
| **Speech-to-Text** | Azure Speech SDK | 1.30+ | Transcription service |
| **Audio Processing** | librosa / soundfile | Latest | Audio I/O and manipulation |
| **Numerical Computing** | NumPy | 1.24+ | Array operations |
| **Deep Learning** | PyTorch | 2.0+ | Backend for pyannote |

### Supporting Libraries

- **pydub**: Audio format conversion
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for REST APIs
- **pyaudio**: Audio device access for live mode
- **scipy**: Scientific computing (cosine similarity)

### Development Tools

- **Git**: Version control
- **pytest**: Unit testing
- **black**: Code formatting
- **mypy**: Type checking
- **pylint**: Code linting

---

## Deployment Architecture

### Development Environment

```
Developer Laptop
    ├── Python 3.8+ virtual environment
    ├── pyannote.audio models (local cache)
    ├── Azure Speech Service (cloud endpoint)
    └── Application code + UI
```

**Setup Steps**:
1. Install Python dependencies
2. Configure Azure credentials
3. Download pyannote models (auto on first run)
4. Run `streamlit run app.py`

---

### Testing Environment

```
Test Server
    ├── Python application
    ├── Azure Speech Service (cloud)
    ├── Test data (sample audio files)
    └── Automated test suite
```

**Testing Strategy**:
- Unit tests for individual components
- Integration tests for end-to-end flows
- Performance benchmarks
- Azure Speech Service mock for offline testing

---

### Production Environment (On-Premises)

```
Production Server
    ├── Python application
    ├── pyannote.audio models (local)
    ├── Azure Speech Container (Docker)
    │   └── Port 5000 (local endpoint)
    ├── GPU (recommended for performance)
    └── Data storage (profiles, results)
```

**Deployment Steps**:
1. Deploy Azure Speech Container via Docker
2. Install Python application
3. Configure to use container endpoint
4. Set up monitoring and logging
5. Configure backups for profiles and results

**Container Setup**:
```bash
docker run --rm -it -p 5000:5000 \
  --memory 4g --cpus 2 \
  mcr.microsoft.com/azure-cognitive-services/speechservices/speech-to-text:latest \
  Eula=accept \
  Billing=<azure_endpoint> \
  ApiKey=<azure_key>
```

---

## Design Decisions

### Decision 1: Two-Stage Processing Pipeline

**Context**: How to structure the processing flow?

**Decision**: Implement two-stage pipeline (diarization → transcription) rather than single-pass.

**Rationale**:
- Clear separation of concerns
- Easier to debug and tune each stage
- Can optimize threshold without re-diarizing
- Supports both batch and real-time modes

**Alternatives Considered**:
- Single-pass streaming: More complex, harder to tune
- Three-stage with separate identification: Unnecessary complexity

---

### Decision 2: Streamlit for UI

**Context**: Which UI framework to use?

**Decision**: Use Streamlit for rapid development.

**Rationale**:
- Pure Python (no HTML/CSS/JS required)
- Built-in widgets for common tasks
- Reactive model simplifies state management
- Fast prototyping and iteration
- Sufficient for internal tool use case

**Alternatives Considered**:
- Flask + React: More flexible but much longer development time
- PyQt: Desktop-native but steeper learning curve
- Gradio: Similar to Streamlit but less mature ecosystem

---

### Decision 3: JSON for Data Storage

**Context**: How to store speaker profiles and results?

**Decision**: Use JSON files rather than database.

**Rationale**:
- Simple to implement and debug
- Human-readable format
- Easy backup and transfer
- Sufficient for expected scale (< 100 profiles)
- No database setup required

**Alternatives Considered**:
- SQLite: Overkill for current scale
- Pickle: Not human-readable, version compatibility issues
- HDF5: Overcomplicated for simple data

---

### Decision 4: pyannote.audio for Speaker Processing

**Context**: Which speaker diarization library?

**Decision**: Use pyannote.audio.

**Rationale**:
- State-of-the-art accuracy
- Integrated diarization and embedding extraction
- Active development and community
- Pretrained models available
- Good documentation

**Alternatives Considered**:
- SpeechBrain: More complex setup
- Resemblyzer: Less accurate, stagnant development
- Custom model: Too time-consuming to develop

---

### Decision 5: Configurable Azure Endpoint

**Context**: How to support both cloud and container deployments?

**Decision**: Abstract Azure client with configurable endpoint.

**Rationale**:
- Single codebase for both environments
- Easy testing (cloud) to production (container) transition
- User controls via configuration, no code changes
- Future-proof for additional endpoints

**Implementation**:
- Configuration flag: `azure.mode = "cloud" | "container"`
- Client initialization selects appropriate endpoint
- Same API regardless of backend

---

### Decision 6: Overlapping Buffers for Real-Time

**Context**: How to handle audio streaming without cutting words?

**Decision**: Use 3-second buffers with 1-second overlap.

**Rationale**:
- Prevents cutting words at buffer boundaries
- Acceptable latency (2-3 seconds)
- Sufficient context for diarization
- Can detect speaker changes reliably

**Trade-offs**:
- Some duplicate processing at boundaries
- Slightly increased latency vs non-overlapping
- Acceptable for real-time monitoring use case

---

## Security Considerations

1. **API Key Storage**: Encrypt or use environment variables
2. **Audio Privacy**: No unauthorized cloud uploads, option for local-only processing
3. **File Permissions**: Restrict access to profile and result files
4. **Input Validation**: Sanitize file uploads, prevent path traversal
5. **Logging**: Redact sensitive data (keys, embeddings) from logs

---

## Performance Optimization Strategies

1. **GPU Acceleration**: Use CUDA for pyannote models
2. **Lazy Loading**: Load models only when needed
3. **Caching**: Cache diarization results during threshold tuning
4. **Parallel Processing**: Process multiple batch files simultaneously
5. **Audio Preprocessing**: Convert to optimal format (16kHz mono) upfront

---

## Scalability Considerations

**Current Design**: Single-instance desktop application

**Future Scalability**:
- **Multi-user**: Add authentication, shared profile storage (database)
- **Distributed Processing**: Queue-based architecture (Celery, RabbitMQ)
- **API Service**: Expose as REST API for external integration
- **Cloud Deployment**: Deploy on Azure VM or Container Apps

---

## Monitoring & Observability

1. **Application Logs**: Structured logging with levels (INFO, WARNING, ERROR)
2. **Performance Metrics**: Track processing times, accuracy scores
3. **Error Tracking**: Log errors with context and stack traces
4. **Health Checks**: Verify Azure connectivity, model availability
5. **Audit Trail**: Log profile creation/deletion, configuration changes

---

## Future Architecture Enhancements

1. **Model Fine-Tuning**: Custom training pipeline for improved accuracy
2. **Multi-Speaker Support**: Identify multiple target speakers simultaneously
3. **Advanced Audio Preprocessing**: Noise reduction, echo cancellation
4. **API Layer**: RESTful API for programmatic access
5. **Web Deployment**: Browser-based UI for remote access
6. **Mobile Support**: iOS/Android apps for field recording
7. **Cloud Storage**: Integration with Azure Blob Storage, OneDrive
8. **Analytics Dashboard**: Visualize speaker statistics, trends over time

---

**Document Status**: Living Document  
**Last Updated**: October 21, 2025  
**Next Review**: After implementation begins
