# Project Overview: Speaker Diarization & Selective Transcription System

## Executive Summary

This project delivers an intelligent audio processing system that identifies a specific person's voice in group conversations and transcribes only their speech. The system combines advanced speaker diarization technology (pyannote.audio) with Azure Speech Service to provide selective, accurate transcription capabilities.

## Business Problem

### The Challenge

In multi-speaker conversations and meetings, there's often a need to:
1. Track what a specific person said across multiple recordings
2. Filter out irrelevant conversation from other participants
3. Process large volumes of meeting recordings efficiently
4. Monitor live conversations for specific speaker contributions

### Current Limitations

- Standard transcription services transcribe everyone equally
- Manual review of full transcripts is time-consuming
- No built-in way to identify specific speakers across different recordings
- Difficult to process recordings at scale

### Our Solution

An automated system that:
- **Learns** a target person's voice from reference samples
- **Identifies** when that person speaks in any recording
- **Transcribes** only their contributions
- **Supports** both batch processing and real-time monitoring

## Project Goals

### Primary Objectives

1. **Accurate Speaker Identification**
   - Identify target speaker with >90% accuracy
   - Minimize false positives (transcribing wrong person)
   - Handle various acoustic conditions

2. **Selective Transcription**
   - Transcribe only target speaker's speech
   - Preserve timestamps and context
   - Generate clean, readable output

3. **Flexible Processing Modes**
   - Batch mode for processing multiple recordings
   - Live mode for real-time monitoring
   - Easy enrollment of new speaker profiles

4. **User-Friendly Interface**
   - Simple enrollment process for reference audio
   - Intuitive batch processing workflow
   - Clear real-time monitoring display

5. **Deployment Flexibility**
   - Test using Azure cloud services
   - Production deployment with containerized Azure Speech Service
   - On-premises capability for data privacy

### Success Criteria

- Speaker identification accuracy: ≥90%
- Transcription accuracy: ≥95% (Azure Speech Service standard)
- Batch processing: Handle 10+ files efficiently
- Real-time mode: Latency <5 seconds
- User can enroll speaker in <2 minutes
- Simple deployment with clear documentation

## Target Users

### Primary User Personas

**1. Compliance Officer**
- Needs to track specific individuals' statements across meetings
- Processes 50+ meeting recordings per week
- Requires accurate, timestamped transcripts

**2. Research Analyst**
- Studies specific person's contributions in group discussions
- Needs to compare statements across multiple sessions
- Values batch processing capability

**3. Meeting Organizer**
- Monitors live meetings for VIP participant contributions
- Needs real-time awareness of specific speaker's input
- Values low-latency processing

## Scope

### In Scope

#### Phase 1: Core Functionality
- Speaker profile enrollment from reference audio
- Batch processing of pre-recorded meetings
- Speaker diarization and identification
- Selective transcription
- Basic Streamlit UI

#### Phase 2: Enhanced Features
- Real-time/live processing mode
- Multiple speaker profile support
- Advanced UI with progress tracking
- Result export in multiple formats

#### Phase 3: Production Deployment
- Container-based Azure Speech Service integration
- Performance optimization
- Error handling and logging
- Deployment documentation

### Out of Scope

- Multi-language support (English only initially)
- Speaker profile training/fine-tuning UI
- Video processing
- Advanced audio enhancement
- Mobile application
- API for external system integration (future consideration)

## Technical Approach

### Core Technologies

1. **pyannote.audio**: Speaker diarization and embedding extraction
2. **Azure Speech Service**: Speech-to-text transcription
3. **Streamlit**: User interface framework
4. **Python 3.8+**: Primary development language

### Architecture Principles

1. **Separation of Concerns**: Clear boundaries between diarization, identification, and transcription
2. **Modularity**: Independent components for easy testing and maintenance
3. **Configuration-Driven**: Easy switching between cloud and container deployments
4. **Scalability**: Design for processing multiple files efficiently

### Processing Strategy

**Two-Stage Pipeline:**

**Stage 1: Identification**
- Diarize audio into speaker segments
- Extract embeddings for each segment
- Compare against target speaker profile
- Tag segments as "target" or "other"

**Stage 2: Selective Transcription**
- Collect all "target" segments
- Send to Azure Speech Service
- Compile timestamped transcript
- Present results to user

## Key Features

### 1. Speaker Enrollment

**Purpose**: Create voice profile for target speaker

**Features**:
- Upload reference audio file (WAV, MP3, etc.)
- Automatic quality validation
- Audio preview playback
- Profile naming and management
- Support for multiple reference samples

**User Workflow**:
1. Click "Enroll New Speaker"
2. Upload audio file (30-60 seconds recommended)
3. Play preview to verify
4. Enter speaker name
5. Click "Create Profile"
6. System confirms profile saved

### 2. Batch Processing Mode

**Purpose**: Process multiple meeting recordings efficiently

**Features**:
- Multi-file upload (drag & drop)
- Speaker profile selection
- Parallel processing support
- Progress tracking per file
- Configurable similarity threshold
- Results table with statistics
- Export transcripts (TXT, JSON)

**User Workflow**:
1. Switch to "Batch Mode" tab
2. Select target speaker profile
3. Upload meeting files (drag & drop folder)
4. Adjust settings if needed
5. Click "Process All"
6. Monitor progress in real-time
7. View/download results when complete

### 3. Live/Real-Time Mode

**Purpose**: Monitor live conversations with minimal delay

**Features**:
- Audio input device selection
- Real-time speaker detection
- Live transcript display
- Visual speaker indicator
- Configurable processing latency
- Session recording option
- Export session transcript

**User Workflow**:
1. Switch to "Live Mode" tab
2. Select audio input device
3. Select target speaker profile
4. Click "Start Monitoring"
5. View live transcript as target speaker talks
6. Click "Stop" when done
7. Export session results

## Benefits

### For End Users

- **Time Savings**: No need to listen to full recordings or read complete transcripts
- **Accuracy**: Automated identification reduces human error
- **Scalability**: Process many recordings quickly
- **Flexibility**: Support for both archived and live content

### For Organizations

- **Cost Efficiency**: Reduce manual transcription review time
- **Compliance**: Accurate tracking of individual statements
- **Privacy**: On-premises deployment option for sensitive data
- **Integration**: Azure Speech Service compatibility

## Constraints & Assumptions

### Technical Constraints

- Requires sufficient computing resources (GPU recommended for real-time)
- Audio quality impacts accuracy (clear speech preferred)
- Minimum reference audio: 10-15 seconds
- English language only (initial version)

### Assumptions

- Target speaker has distinguishable voice characteristics
- Audio recordings have reasonable quality (no extreme noise)
- Users have basic computer skills
- Azure subscription available for Speech Service
- Reference audio samples can be obtained

### Known Limitations

- Similarity threshold tuning may be needed per deployment
- Very similar voices (twins, mimics) may be challenging
- Overlapping speech may be skipped for safety
- Real-time mode has inherent latency (2-5 seconds)

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low speaker ID accuracy | High | Medium | Extensive testing, threshold tuning, quality reference samples |
| Performance bottlenecks | Medium | Medium | GPU acceleration, optimized pipeline, batch processing |
| Azure Speech Service latency | Medium | Low | Container deployment option, buffer optimization |
| Poor reference audio quality | High | Medium | Quality validation, user guidance, multiple samples |
| Complex user interface | Medium | Low | Streamlit simplicity, user testing, clear documentation |

## Timeline & Milestones

### Phase 1: Foundation (Weeks 1-2)
- Set up development environment
- Implement speaker enrollment
- Basic diarization pipeline
- Proof of concept

### Phase 2: Batch Processing (Weeks 3-4)
- Batch mode implementation
- Azure Speech Service integration
- Results management
- Testing and validation

### Phase 3: Live Mode (Weeks 5-6)
- Real-time processing pipeline
- Live mode UI
- Performance optimization
- End-to-end testing

### Phase 4: Production Ready (Weeks 7-8)
- Container deployment support
- Error handling and logging
- Documentation completion
- Deployment and handoff

## Success Metrics

### Technical Metrics

- Speaker identification accuracy: ≥90%
- Transcription accuracy: ≥95%
- Batch processing throughput: ≥10 files/hour
- Real-time processing latency: ≤5 seconds
- System uptime: ≥99%

### User Experience Metrics

- Time to enroll speaker: ≤2 minutes
- UI intuitiveness: Minimal training required
- Processing setup: ≤1 minute per batch
- Result accessibility: Immediate view/download

### Business Metrics

- Reduction in manual review time: ≥70%
- User adoption rate: Track usage
- Deployment success rate: 100%
- Cost per transcription hour: Measure and optimize

## Future Enhancements

### Potential Features (Post-MVP)

- Multi-language support
- Multiple simultaneous target speakers
- Advanced audio preprocessing
- API for external integration
- Mobile application
- Cloud-based SaaS offering
- Speaker profile auto-improvement
- Sentiment analysis for target speaker
- Topic extraction and summarization

---

**Document Status**: Living Document  
**Last Updated**: October 21, 2025  
**Next Review**: After implementation phase begins
