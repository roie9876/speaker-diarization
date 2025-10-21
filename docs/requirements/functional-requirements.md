# Functional Requirements Specification

## Document Information

- **Project**: Speaker Diarization & Selective Transcription System
- **Version**: 1.0
- **Date**: October 21, 2025
- **Status**: Draft

## Overview

This document details the functional requirements for the speaker diarization system. Each requirement is assigned a unique identifier, priority level, and acceptance criteria.

## Requirement Categories

- **FR-ENR**: Speaker Enrollment
- **FR-BAT**: Batch Processing Mode
- **FR-LIV**: Live/Real-Time Mode
- **FR-UI**: User Interface
- **FR-CFG**: Configuration & Settings
- **FR-OUT**: Output & Results
- **FR-STO**: Storage & Data Management

---

## FR-ENR: Speaker Enrollment Requirements

### FR-ENR-001: Upload Reference Audio File

**Priority**: CRITICAL  
**Description**: User must be able to upload an audio file containing the target speaker's voice.

**Acceptance Criteria**:
- Support common audio formats: WAV, MP3, M4A, FLAC, OGG
- File size limit: 100MB maximum
- Upload methods: Browse button and drag & drop
- Display file name and size after upload
- Show error message for unsupported formats

**Dependencies**: None

---

### FR-ENR-002: Audio Preview Playback

**Priority**: HIGH  
**Description**: User must be able to play the uploaded reference audio to verify content.

**Acceptance Criteria**:
- Audio player with play/pause controls
- Display audio duration
- Volume control
- Playback position indicator
- Works for all supported formats

**Dependencies**: FR-ENR-001

---

### FR-ENR-003: Audio Quality Validation

**Priority**: HIGH  
**Description**: System must validate that uploaded audio meets minimum quality requirements.

**Acceptance Criteria**:
- Check minimum duration: ≥10 seconds
- Detect speech content (not silence or music)
- Estimate speech duration within file
- Warn user if quality is questionable
- Provide recommendations for better samples

**Dependencies**: FR-ENR-001

---

### FR-ENR-004: Speaker Profile Creation

**Priority**: CRITICAL  
**Description**: System must extract speaker embedding and save profile.

**Acceptance Criteria**:
- Extract 512-dimensional embedding vector using pyannote.audio
- User provides speaker name/identifier
- Optional: Add description or notes
- Save profile to storage
- Confirmation message on success
- Processing time: <30 seconds for 1-minute audio

**Dependencies**: FR-ENR-001, FR-ENR-003

---

### FR-ENR-005: Multiple Reference Samples

**Priority**: MEDIUM  
**Description**: Allow adding multiple audio samples to improve speaker profile.

**Acceptance Criteria**:
- Option to upload additional samples for existing profile
- System averages or concatenates embeddings
- Display number of samples per profile
- Can add samples later after initial enrollment
- Maximum 5 samples per profile

**Dependencies**: FR-ENR-004

---

### FR-ENR-006: View Enrolled Speakers

**Priority**: HIGH  
**Description**: Display list of all enrolled speaker profiles.

**Acceptance Criteria**:
- Table/list showing: name, date created, number of samples
- Sortable by name or date
- Search/filter capability
- Visual indicator of profile quality (if applicable)

**Dependencies**: FR-ENR-004

---

### FR-ENR-007: Delete Speaker Profile

**Priority**: MEDIUM  
**Description**: Allow deletion of speaker profiles.

**Acceptance Criteria**:
- Delete button per profile
- Confirmation dialog before deletion
- Remove all associated files
- Cannot undo deletion (warning displayed)
- Update profile list immediately

**Dependencies**: FR-ENR-006

---

### FR-ENR-008: Export/Import Speaker Profiles

**Priority**: LOW  
**Description**: Allow exporting profiles for backup or sharing.

**Acceptance Criteria**:
- Export profile as JSON file
- Include all metadata and embedding data
- Import profile from JSON file
- Validate imported profile structure
- Handle duplicate names (prompt user)

**Dependencies**: FR-ENR-004

---

## FR-BAT: Batch Processing Mode Requirements

### FR-BAT-001: Multiple File Upload

**Priority**: CRITICAL  
**Description**: User must be able to upload multiple meeting recording files.

**Acceptance Criteria**:
- Support drag & drop of multiple files
- Support folder drag & drop (process all audio files)
- Browse and multi-select files
- Display file list with names and sizes
- Show total files and total duration
- Remove individual files from queue before processing

**Dependencies**: None

---

### FR-BAT-002: Speaker Profile Selection

**Priority**: CRITICAL  
**Description**: User must select which speaker profile to search for.

**Acceptance Criteria**:
- Dropdown list of enrolled speakers
- Display speaker name and enrollment date
- Must select profile before starting processing
- Default to last used profile (optional)

**Dependencies**: FR-ENR-006

---

### FR-BAT-003: Processing Configuration

**Priority**: HIGH  
**Description**: User can configure processing parameters.

**Acceptance Criteria**:
- Similarity threshold slider (0.5 - 0.95)
- Default value: 0.75
- Tooltip explaining threshold impact
- Azure endpoint selection (cloud/container)
- Option: parallel processing on/off
- Option: include timestamps in output

**Dependencies**: None

---

### FR-BAT-004: Start Batch Processing

**Priority**: CRITICAL  
**Description**: User initiates processing of all queued files.

**Acceptance Criteria**:
- "Process All" button
- Validation: speaker profile selected, files uploaded
- Disable upload/configuration during processing
- Option to cancel processing mid-batch
- Processing starts within 2 seconds of click

**Dependencies**: FR-BAT-001, FR-BAT-002

---

### FR-BAT-005: Processing Progress Display

**Priority**: HIGH  
**Description**: Show real-time progress for each file being processed.

**Acceptance Criteria**:
- Progress bar per file
- Status indicator: Queued, Processing, Complete, Error
- Current step display: Diarizing, Identifying, Transcribing
- Estimated time remaining per file
- Overall batch progress percentage
- Auto-scroll to current file being processed

**Dependencies**: FR-BAT-004

---

### FR-BAT-006: Results Display

**Priority**: CRITICAL  
**Description**: Show processing results for all files.

**Acceptance Criteria**:
- Table with columns: Filename, Status, Target Detected, Speech Duration, Actions
- Status: Success, No Target Found, Error
- Target Detected: Yes/No with confidence score
- Speech Duration: Total seconds of target speaker
- View transcript button per file
- Download transcript button per file
- Filter results by status

**Dependencies**: FR-BAT-005

---

### FR-BAT-007: Individual Result Details

**Priority**: HIGH  
**Description**: View detailed results for a single processed file.

**Acceptance Criteria**:
- Modal or expandable panel per file
- Full transcript with timestamps
- List of identified segments with confidence scores
- Audio segments playback (optional)
- Copy transcript to clipboard
- Download as TXT or JSON

**Dependencies**: FR-BAT-006

---

### FR-BAT-008: Batch Export

**Priority**: MEDIUM  
**Description**: Export all results from batch processing.

**Acceptance Criteria**:
- "Export All" button
- Format options: TXT (one per file), JSON (combined), CSV (summary)
- Include metadata: processing date, settings used
- Zip file if multiple files
- Download starts immediately

**Dependencies**: FR-BAT-006

---

### FR-BAT-009: Reprocess Failed Files

**Priority**: MEDIUM  
**Description**: Retry processing for files that failed.

**Acceptance Criteria**:
- "Reprocess" button for errored files
- Option to adjust settings before retry
- Preserves original file in queue
- Updates status when complete
- Limit: 3 retry attempts per file

**Dependencies**: FR-BAT-006

---

### FR-BAT-010: Processing History

**Priority**: LOW  
**Description**: View history of previous batch jobs.

**Acceptance Criteria**:
- List of past batch jobs with dates
- Summary: files processed, files with target found
- Click to view results
- Results persist until manually deleted
- Limit: 30 days or 100 jobs (configurable)

**Dependencies**: FR-BAT-006

---

## FR-LIV: Live/Real-Time Mode Requirements

### FR-LIV-001: Audio Input Selection

**Priority**: CRITICAL  
**Description**: User must select audio input device for live monitoring.

**Acceptance Criteria**:
- Dropdown list of available audio devices
- Show device name and type (microphone, system audio, etc.)
- Test audio button (shows level meter)
- Remember last used device
- Detect new devices plugged in

**Dependencies**: None

---

### FR-LIV-002: Speaker Profile Selection

**Priority**: CRITICAL  
**Description**: User must select which speaker to monitor for.

**Acceptance Criteria**:
- Dropdown list of enrolled speakers
- Same as batch mode profile selector
- Must select before starting monitoring
- Can change profile between sessions (not during)

**Dependencies**: FR-ENR-006

---

### FR-LIV-003: Live Monitoring Configuration

**Priority**: HIGH  
**Description**: User can configure real-time processing parameters.

**Acceptance Criteria**:
- Similarity threshold slider
- Processing mode: Aggressive / Balanced / Conservative
- Buffer duration: 2s / 3s / 5s (affects latency)
- Auto-save transcript: on/off
- Show all speakers or target only

**Dependencies**: None

---

### FR-LIV-004: Start/Stop Monitoring

**Priority**: CRITICAL  
**Description**: User can start and stop live monitoring session.

**Acceptance Criteria**:
- "Start Monitoring" button
- Changes to "Stop Monitoring" when active
- Validation before start: device and profile selected
- Stop immediately on button click
- Disable configuration changes during monitoring
- Show session duration timer

**Dependencies**: FR-LIV-001, FR-LIV-002

---

### FR-LIV-005: Live Audio Level Indicator

**Priority**: HIGH  
**Description**: Visual feedback of audio input level.

**Acceptance Criteria**:
- Real-time audio level meter
- Color coding: green (good), yellow (quiet), red (clipping)
- Updates at least 10 times per second
- Visible even when not monitoring
- Helps user position microphone correctly

**Dependencies**: FR-LIV-001

---

### FR-LIV-006: Speaker Detection Indicator

**Priority**: HIGH  
**Description**: Visual indication when target speaker is detected.

**Acceptance Criteria**:
- Status indicator: "Silence", "Other Speaker", "Target Speaker"
- Color coding: gray, yellow, green
- Update latency: within 1 second of detection
- Show confidence score for target detections
- Audio or visual alert option (optional)

**Dependencies**: FR-LIV-004

---

### FR-LIV-007: Live Transcript Display

**Priority**: CRITICAL  
**Description**: Display transcript in real-time as target speaker talks.

**Acceptance Criteria**:
- Scrolling text area
- Auto-scroll to latest text
- Include timestamps for each segment
- Show confidence scores (optional toggle)
- Clear formatting, readable font size
- Maximum 2-5 second delay from speech to text

**Dependencies**: FR-LIV-006

---

### FR-LIV-008: Session Recording

**Priority**: MEDIUM  
**Description**: Optionally record the entire audio session.

**Acceptance Criteria**:
- Toggle: "Record Session" checkbox
- Saves full audio stream to file
- Timestamp in filename
- Format: WAV or MP3
- Can replay later in batch mode
- Shows recording status icon

**Dependencies**: FR-LIV-004

---

### FR-LIV-009: Export Live Session

**Priority**: HIGH  
**Description**: Export transcript from completed live session.

**Acceptance Criteria**:
- "Export Session" button (enabled after stop)
- Format options: TXT, JSON
- Include: transcript, timestamps, confidence scores
- Include: session metadata (date, duration, speaker)
- Filename: auto-generated with timestamp
- Option to clear session after export

**Dependencies**: FR-LIV-007

---

### FR-LIV-010: Pause/Resume Monitoring

**Priority**: LOW  
**Description**: Temporarily pause monitoring without stopping session.

**Acceptance Criteria**:
- "Pause" button during monitoring
- Changes to "Resume" when paused
- Retains session state and transcript
- Does not process audio during pause
- Resume picks up immediately

**Dependencies**: FR-LIV-004

---

## FR-UI: User Interface Requirements

### FR-UI-001: Tab Navigation

**Priority**: CRITICAL  
**Description**: UI must have clear navigation between modes.

**Acceptance Criteria**:
- Three main tabs: Enrollment, Batch Mode, Live Mode
- Active tab visually distinguished
- Tab switching immediate (<100ms)
- State preserved when switching tabs
- Tooltips on tab hover (optional)

**Dependencies**: None

---

### FR-UI-002: Responsive Layout

**Priority**: HIGH  
**Description**: UI must be usable on different screen sizes.

**Acceptance Criteria**:
- Minimum resolution: 1280x720
- Elements resize appropriately
- No horizontal scrolling required
- Text readable at default zoom
- Works on laptop and desktop screens

**Dependencies**: None

---

### FR-UI-003: Loading Indicators

**Priority**: HIGH  
**Description**: Show visual feedback during processing.

**Acceptance Criteria**:
- Spinner or progress bar for long operations
- Disable buttons during processing
- Status messages (e.g., "Loading model...")
- Cannot click UI elements multiple times
- Clear indication when operation complete

**Dependencies**: None

---

### FR-UI-004: Error Messages

**Priority**: CRITICAL  
**Description**: Display clear error messages when issues occur.

**Acceptance Criteria**:
- Error message in red or alert box
- Describe what went wrong
- Suggest corrective action when possible
- Dismiss button for error messages
- Errors don't crash the application

**Dependencies**: None

---

### FR-UI-005: Success Confirmations

**Priority**: MEDIUM  
**Description**: Confirm successful operations to user.

**Acceptance Criteria**:
- Success message in green or check icon
- Brief, clear confirmation text
- Auto-dismiss after 3-5 seconds (optional)
- Manual dismiss option
- Don't block user from continuing

**Dependencies**: None

---

### FR-UI-006: Help & Tooltips

**Priority**: LOW  
**Description**: Provide contextual help for users.

**Acceptance Criteria**:
- Tooltips on hover for settings and buttons
- Help icon (?) linking to documentation
- Examples shown for input fields
- FAQ or help section (optional)
- Version info and about page

**Dependencies**: None

---

## FR-CFG: Configuration & Settings Requirements

### FR-CFG-001: Azure Endpoint Configuration

**Priority**: CRITICAL  
**Description**: Configure Azure Speech Service endpoint (cloud or container).

**Acceptance Criteria**:
- Settings page or sidebar
- Radio button: Cloud / Container
- Cloud: Region dropdown and API key input
- Container: URL input (e.g., http://localhost:5000)
- Test connection button
- Save settings persistently

**Dependencies**: None

---

### FR-CFG-002: Default Threshold Setting

**Priority**: MEDIUM  
**Description**: Set default similarity threshold for speaker identification.

**Acceptance Criteria**:
- Slider in settings: 0.5 - 0.95
- Default value: 0.75
- Applied to new batch/live sessions
- Can override per session
- Explanation of threshold meaning

**Dependencies**: None

---

### FR-CFG-003: Output Format Preferences

**Priority**: LOW  
**Description**: Configure default output format for transcripts.

**Acceptance Criteria**:
- Checkbox: Include timestamps
- Checkbox: Include confidence scores
- Format dropdown: TXT, JSON, Both
- Auto-export option: on/off
- Saved between sessions

**Dependencies**: None

---

### FR-CFG-004: Performance Settings

**Priority**: MEDIUM  
**Description**: Configure resource usage for processing.

**Acceptance Criteria**:
- GPU usage: Auto-detect / Force CPU / Force GPU
- Parallel processing: Enable/disable
- Number of workers: 1-4 (if parallel enabled)
- Buffer size for live mode: 2s / 3s / 5s
- Display current hardware capabilities

**Dependencies**: None

---

### FR-CFG-005: Storage Location

**Priority**: LOW  
**Description**: Configure where profiles and results are stored.

**Acceptance Criteria**:
- File browser to select directory
- Default: project directory
- Validate write permissions
- Show current storage location
- Option to export/import profiles

**Dependencies**: None

---

## FR-OUT: Output & Results Requirements

### FR-OUT-001: Timestamped Transcripts

**Priority**: CRITICAL  
**Description**: Transcripts must include accurate timestamps.

**Acceptance Criteria**:
- Format: [HH:MM:SS] or [MM:SS] for each segment
- Timestamps relative to original audio file
- Accuracy: within 1 second
- Optional: millisecond precision
- Consistent formatting throughout

**Dependencies**: None

---

### FR-OUT-002: Confidence Scores

**Priority**: MEDIUM  
**Description**: Include speaker identification confidence scores.

**Acceptance Criteria**:
- Display confidence as percentage (0-100%)
- Optional toggle to show/hide
- Color coding: green (>85%), yellow (70-85%), red (<70%)
- Per segment or overall session score
- Helps user assess reliability

**Dependencies**: None

---

### FR-OUT-003: Summary Statistics

**Priority**: MEDIUM  
**Description**: Provide summary of processing results.

**Acceptance Criteria**:
- Total audio duration processed
- Target speaker detected: Yes/No
- Total target speaker speech time
- Number of segments identified
- Average confidence score
- Processing time taken

**Dependencies**: None

---

### FR-OUT-004: Text Format Export

**Priority**: CRITICAL  
**Description**: Export transcript as plain text file.

**Acceptance Criteria**:
- Clean, readable text format
- Optional: timestamps included
- UTF-8 encoding
- Filename: speaker_date_time.txt
- One file per recording

**Dependencies**: FR-OUT-001

---

### FR-OUT-005: JSON Format Export

**Priority**: HIGH  
**Description**: Export structured data in JSON format.

**Acceptance Criteria**:
- Include: transcript, timestamps, confidence scores
- Include: metadata (speaker, file, date, settings)
- Valid JSON structure
- Pretty-printed (indented)
- Schema documented

**Dependencies**: FR-OUT-001, FR-OUT-002

---

### FR-OUT-006: Batch Summary Report

**Priority**: LOW  
**Description**: Generate summary report for batch processing jobs.

**Acceptance Criteria**:
- HTML or PDF format
- List all files processed
- Summary statistics per file
- Overall batch statistics
- Visual indicators (charts optional)
- Export as standalone file

**Dependencies**: FR-BAT-006

---

## FR-STO: Storage & Data Management Requirements

### FR-STO-001: Speaker Profile Storage

**Priority**: CRITICAL  
**Description**: Persist speaker profiles between sessions.

**Acceptance Criteria**:
- Stored in JSON format
- Include: name, embedding vector, metadata
- One file per profile or single database
- Load automatically on application start
- Backup option available

**Dependencies**: FR-ENR-004

---

### FR-STO-002: Results Storage

**Priority**: HIGH  
**Description**: Save processing results for later access.

**Acceptance Criteria**:
- Organized by date or batch job ID
- Include audio file references (path or name)
- Include transcripts and metadata
- Retention: configurable (default 30 days)
- Manual delete option

**Dependencies**: FR-BAT-006, FR-LIV-009

---

### FR-STO-003: Configuration Persistence

**Priority**: MEDIUM  
**Description**: Save user settings between sessions.

**Acceptance Criteria**:
- Saved in config file (JSON or INI)
- Loaded on application start
- Includes: Azure settings, thresholds, preferences
- Reset to defaults option
- Manual edit option (advanced users)

**Dependencies**: FR-CFG-001

---

### FR-STO-004: Temporary File Management

**Priority**: MEDIUM  
**Description**: Handle temporary files during processing.

**Acceptance Criteria**:
- Create temp directory for audio segments
- Clean up after processing complete
- Handle errors gracefully (cleanup on crash)
- Configurable temp directory location
- Warn if low disk space

**Dependencies**: None

---

### FR-STO-005: Data Export/Import

**Priority**: LOW  
**Description**: Backup and restore all application data.

**Acceptance Criteria**:
- Export: speaker profiles, results, settings
- Format: ZIP archive
- Import: validate structure before restoring
- Option to merge or replace existing data
- Confirmation before import

**Dependencies**: FR-STO-001, FR-STO-002, FR-STO-003

---

## Requirements Summary

### Priority Breakdown

- **CRITICAL**: 15 requirements
- **HIGH**: 12 requirements
- **MEDIUM**: 14 requirements
- **LOW**: 10 requirements

**Total**: 51 functional requirements

### Category Breakdown

- **Enrollment**: 8 requirements
- **Batch Processing**: 10 requirements
- **Live Mode**: 10 requirements
- **User Interface**: 6 requirements
- **Configuration**: 5 requirements
- **Output**: 6 requirements
- **Storage**: 5 requirements

---

## Traceability Matrix

This requirements specification will be used to:
1. Guide implementation planning
2. Create test cases and validation criteria
3. Track development progress
4. Verify completeness of delivered system

Each requirement should be traceable to:
- Design documents
- Implementation code
- Test cases
- User documentation

---

**Document Status**: Draft for Review  
**Next Steps**: Review and approval by stakeholders  
**Last Updated**: October 21, 2025
