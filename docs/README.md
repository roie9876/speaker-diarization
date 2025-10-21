# Speaker Diarization Project Documentation

## Project Overview

This project implements a speaker diarization and selective transcription system using Azure Speech Service and pyannote.audio. The system identifies a specific target speaker in group conversations and transcribes only their speech, ignoring other participants.

## Documentation Structure

## Documentation Structure

```
.github/
└── copilot-instructions.md                      ✅ GitHub Copilot implementation guide

docs/
├── README.md                                    ✅ Documentation overview
├── PROJECT_OVERVIEW.md                          ✅ High-level project goals and scope
├── IMPLEMENTATION_GUIDE.md                      ✅ Step-by-step implementation roadmap
├── requirements/
│   ├── functional-requirements.md               ✅ 51 detailed functional requirements
│   └── non-functional-requirements.md           ✅ 44 performance/quality requirements
├── architecture/
│   └── system-architecture.md                   ✅ Complete system design
└── technical/
    ├── technology-stack.md                      ✅ All technologies and setup guides
    └── pyannote-integration.md                  ✅ Detailed pyannote.audio guide
```

## Quick Start Guide

### For Developers

1. Read [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) to understand the project goals
2. Review [requirements/functional-requirements.md](./requirements/functional-requirements.md) for feature specifications
3. Study [architecture/system-architecture.md](./architecture/system-architecture.md) for technical design
4. Check [technical/technology-stack.md](./technical/technology-stack.md) for implementation details

### For Product Owners

1. Start with [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)
2. Review [requirements/user-stories.md](./requirements/user-stories.md)
3. Check [requirements/functional-requirements.md](./requirements/functional-requirements.md)

### For DevOps/Infrastructure

1. Review [architecture/deployment-architecture.md](./architecture/deployment-architecture.md)
2. Check [technical/azure-speech-integration.md](./technical/azure-speech-integration.md) for endpoint configuration
3. Study [requirements/non-functional-requirements.md](./requirements/non-functional-requirements.md) for resource requirements

## Key Features

- **Speaker Enrollment**: Upload reference audio samples to create speaker profiles
- **Batch Processing**: Process multiple recorded meetings to find and transcribe target speaker
- **Live Mode**: Real-time speaker identification and transcription during live conversations
- **Flexible Deployment**: Support for both Azure cloud and containerized Azure Speech Service
- **User-Friendly UI**: Streamlit-based interface for easy operation

## Technology Highlights

- **Speaker Diarization**: pyannote.audio for state-of-the-art speaker separation
- **Speaker Identification**: Custom embedding-based speaker matching
- **Speech-to-Text**: Azure Speech Service (cloud or container)
- **User Interface**: Streamlit for rapid development and intuitive design
- **Language**: Python 3.8+

## Project Status

**Current Phase**: Documentation and Architecture Design

**Next Steps**:
1. Complete documentation review
2. Set up development environment
3. Implement core processing engine
4. Build Streamlit UI
5. Integration testing
6. Production deployment preparation

## Contact & Support

- **Project Location**: `/Users/robenhai/speaker diarization/`
- **Documentation Date**: October 2025
- **Last Updated**: October 21, 2025

---

*This documentation is a living document and will be updated as the project evolves.*
