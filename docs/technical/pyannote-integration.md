# pyannote.audio Integration Guide

## Document Information

- **Project**: Speaker Diarization & Selective Transcription System
- **Version**: 1.0
- **Date**: October 21, 2025

## Overview

This document provides detailed implementation guidance for integrating pyannote.audio for speaker diarization and identification in the project.

---

## What is pyannote.audio?

pyannote.audio is a Python library for speaker diarization, speaker verification, and speaker embedding extraction. It provides state-of-the-art pretrained models and is built on PyTorch.

**Official Repository**: https://github.com/pyannote/pyannote-audio  
**Documentation**: https://pyannote.github.io/

---

## Installation & Setup

### 1. Install pyannote.audio

```bash
pip install pyannote.audio>=3.1.0
```

### 2. Hugging Face Authentication

pyannote models require accepting user agreements on Hugging Face:

**Steps**:
1. Create account at https://huggingface.co
2. Accept agreements:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. Generate access token: https://huggingface.co/settings/tokens
4. Set environment variable:
```bash
export HUGGING_FACE_HUB_TOKEN=hf_xxxxxxxxxxxxx
```

### 3. Verify Installation

```python
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="<your_token>"
)
print("✅ pyannote.audio installed successfully!")
```

---

## Core Components

### 1. Speaker Diarization Pipeline

**Purpose**: Detect "who spoke when" in audio

**Implementation**:

```python
from pyannote.audio import Pipeline
import torch

class DiarizationService:
    def __init__(self, use_gpu=True):
        """Initialize diarization pipeline"""
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        
        # Load pipeline
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        
        # Move to device
        self.pipeline.to(self.device)
    
    def diarize(self, audio_file):
        """
        Perform speaker diarization on audio file
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Diarization object with speaker segments
        """
        diarization = self.pipeline(audio_file)
        return diarization
    
    def get_segments(self, diarization):
        """
        Extract segments from diarization result
        
        Returns:
            List of (start, end, speaker_label) tuples
        """
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker,
                'duration': turn.end - turn.start
            })
        return segments
```

**Usage Example**:

```python
service = DiarizationService(use_gpu=True)
diarization = service.diarize("meeting.wav")

for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{speaker}: {turn.start:.1f}s - {turn.end:.1f}s")

# Output:
# SPEAKER_00: 0.5s - 5.2s
# SPEAKER_01: 5.8s - 12.3s
# SPEAKER_00: 12.9s - 18.4s
```

### 2. Speaker Embedding Extraction

**Purpose**: Convert audio segment to numerical vector (voice fingerprint)

**Implementation**:

```python
from pyannote.audio import Inference
import numpy as np

class EmbeddingService:
    def __init__(self, use_gpu=True):
        """Initialize embedding model"""
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        
        # Load embedding model
        self.model = Inference(
            "pyannote/embedding",
            window="whole",
            use_auth_token=os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        self.model.to(self.device)
    
    def extract_embedding(self, audio_file, start=None, end=None):
        """
        Extract speaker embedding from audio
        
        Args:
            audio_file: Path to audio file or audio array
            start: Start time in seconds (optional)
            end: End time in seconds (optional)
            
        Returns:
            numpy array (512-dimensional embedding)
        """
        if start is not None and end is not None:
            # Extract specific segment
            from pyannote.audio import Audio
            audio = Audio()
            waveform, sample_rate = audio.crop(
                audio_file,
                Segment(start, end)
            )
            embedding = self.model({"waveform": waveform, "sample_rate": sample_rate})
        else:
            # Whole file
            embedding = self.model(audio_file)
        
        return embedding
    
    def compute_similarity(self, embedding1, embedding2):
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1, embedding2: numpy arrays (512-dim)
            
        Returns:
            float: similarity score (0.0 to 1.0)
        """
        from scipy.spatial.distance import cosine
        return 1 - cosine(embedding1, embedding2)
```

**Usage Example**:

```python
service = EmbeddingService(use_gpu=True)

# Extract embedding from reference audio
reference_embedding = service.extract_embedding("john_reference.wav")

# Extract from segment
test_embedding = service.extract_embedding("meeting.wav", start=10.0, end=15.0)

# Compare
similarity = service.compute_similarity(reference_embedding, test_embedding)
print(f"Similarity: {similarity:.2f}")

if similarity > 0.75:
    print("✅ Same speaker")
else:
    print("❌ Different speaker")
```

---

## Speaker Identification Service

**Purpose**: Combine diarization and embedding extraction for speaker identification

**Complete Implementation**:

```python
import os
import torch
import numpy as np
from pyannote.audio import Pipeline, Inference, Audio
from pyannote.core import Segment
from scipy.spatial.distance import cosine

class SpeakerIdentificationService:
    """
    Complete service for speaker diarization and identification
    """
    
    def __init__(self, use_gpu=True):
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        
        # Initialize components
        self._init_diarization()
        self._init_embedding()
        self.audio = Audio()
        
    def _init_diarization(self):
        """Load diarization pipeline"""
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        self.diarization_pipeline.to(self.device)
        
    def _init_embedding(self):
        """Load embedding model"""
        self.embedding_model = Inference(
            "pyannote/embedding",
            window="whole",
            use_auth_token=os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        self.embedding_model.to(self.device)
    
    def create_speaker_profile(self, audio_file):
        """
        Create speaker profile from reference audio
        
        Args:
            audio_file: Path to reference audio
            
        Returns:
            dict with embedding and metadata
        """
        embedding = self.embedding_model(audio_file)
        
        # Get audio metadata
        info = self.audio.get_duration(audio_file)
        
        return {
            'embedding': embedding,
            'duration': info,
            'file': os.path.basename(audio_file)
        }
    
    def process_audio(self, audio_file, target_profile, threshold=0.75):
        """
        Process audio file: diarize and identify target speaker
        
        Args:
            audio_file: Path to audio file
            target_profile: Speaker profile dict with 'embedding'
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of segments with identification results
        """
        # Step 1: Diarization
        print("🔍 Performing speaker diarization...")
        diarization = self.diarization_pipeline(audio_file)
        
        # Step 2: Extract and compare embeddings
        print("🎯 Identifying target speaker...")
        results = []
        target_embedding = target_profile['embedding']
        
        for turn, _, speaker_label in diarization.itertracks(yield_label=True):
            # Extract embedding for this segment
            waveform, sample_rate = self.audio.crop(
                audio_file,
                Segment(turn.start, turn.end)
            )
            
            segment_embedding = self.embedding_model({
                "waveform": waveform,
                "sample_rate": sample_rate
            })
            
            # Compare with target
            similarity = self._compute_similarity(segment_embedding, target_embedding)
            is_target = similarity >= threshold
            
            results.append({
                'start': turn.start,
                'end': turn.end,
                'duration': turn.end - turn.start,
                'speaker_label': speaker_label,
                'similarity': similarity,
                'is_target': is_target
            })
        
        return results
    
    def _compute_similarity(self, emb1, emb2):
        """Compute cosine similarity"""
        return 1 - cosine(emb1, emb2)
    
    def get_target_segments_audio(self, audio_file, results):
        """
        Extract audio segments for target speaker only
        
        Args:
            audio_file: Original audio file
            results: Output from process_audio()
            
        Returns:
            List of audio segments (waveform, sample_rate)
        """
        segments = []
        for result in results:
            if result['is_target']:
                waveform, sample_rate = self.audio.crop(
                    audio_file,
                    Segment(result['start'], result['end'])
                )
                segments.append({
                    'waveform': waveform,
                    'sample_rate': sample_rate,
                    'start': result['start'],
                    'end': result['end'],
                    'confidence': result['similarity']
                })
        return segments
```

**Full Usage Example**:

```python
# Initialize service
service = SpeakerIdentificationService(use_gpu=True)

# Step 1: Create target speaker profile
print("Creating speaker profile...")
profile = service.create_speaker_profile("john_reference.wav")

# Step 2: Process meeting audio
print("Processing meeting audio...")
results = service.process_audio(
    "meeting.wav",
    target_profile=profile,
    threshold=0.75
)

# Step 3: Analyze results
target_segments = [r for r in results if r['is_target']]
print(f"\n📊 Found {len(target_segments)} segments from target speaker")
print(f"⏱️  Total target speech: {sum(s['duration'] for s in target_segments):.1f}s")

# Step 4: Display segments
print("\n🎤 Target speaker segments:")
for seg in target_segments:
    print(f"  {seg['start']:.1f}s - {seg['end']:.1f}s (confidence: {seg['similarity']:.2f})")

# Step 5: Extract audio for transcription
audio_segments = service.get_target_segments_audio("meeting.wav", results)
print(f"\n✅ Ready for transcription: {len(audio_segments)} segments")
```

---

## Performance Optimization

### GPU Acceleration

**Check GPU Availability**:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Current device: {torch.cuda.get_device_name(0)}")
```

**Performance Comparison**:
- **CPU**: 5-10x real-time (5-10 minutes to process 1 minute of audio)
- **GPU**: 0.5-1x real-time (30-60 seconds to process 1 minute)

**Recommendation**: Use GPU for real-time mode, CPU acceptable for batch

---

### Batch Processing Optimization

```python
def process_batch_files(service, files, target_profile, num_workers=4):
    """
    Process multiple files in parallel
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = {}
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_file = {
            executor.submit(
                service.process_audio,
                file,
                target_profile
            ): file for file in files
        }
        
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                results[file] = future.result()
                print(f"✅ Completed: {file}")
            except Exception as e:
                print(f"❌ Error processing {file}: {e}")
                results[file] = None
    
    return results
```

---

## Configuration Options

### Diarization Pipeline Parameters

```python
# Configure pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=token
)

# Override default parameters
pipeline.instantiate({
    "segmentation": {
        "min_duration_off": 0.0,  # Min silence between speakers (seconds)
    },
    "clustering": {
        "method": "centroid",  # Clustering method
        "min_cluster_size": 15,  # Min samples per cluster
        "threshold": 0.7,  # Clustering threshold
    }
})
```

### Embedding Extraction Parameters

```python
# Window mode
model = Inference("pyannote/embedding", window="whole")  # Process entire audio

# Or sliding window mode
model = Inference(
    "pyannote/embedding",
    window="sliding",
    duration=3.0,  # 3-second windows
    step=1.0  # 1-second step
)
```

---

## Audio Format Requirements

### Supported Formats

pyannote.audio uses soundfile/librosa, supporting:
- WAV (recommended)
- FLAC
- OGG
- MP3 (requires FFmpeg)

### Optimal Format

**For Best Performance**:
- **Format**: WAV (uncompressed)
- **Sample Rate**: 16kHz
- **Channels**: Mono
- **Bit Depth**: 16-bit

**Conversion Example**:
```python
import librosa
import soundfile as sf

# Load and convert
audio, sr = librosa.load("input.mp3", sr=16000, mono=True)

# Save as WAV
sf.write("output.wav", audio, 16000)
```

---

## Handling Edge Cases

### 1. Short Audio Segments

**Problem**: Very short segments (<1 second) may not have reliable embeddings

**Solution**:
```python
MIN_SEGMENT_DURATION = 1.0  # seconds

def filter_short_segments(results):
    return [r for r in results if r['duration'] >= MIN_SEGMENT_DURATION]
```

### 2. Overlapping Speech

**Problem**: Multiple speakers talking simultaneously

**pyannote Behavior**: Diarization may skip or split overlapped regions

**Solution**: Accept conservative approach (skip ambiguous segments)

### 3. Low Quality Audio

**Problem**: Background noise, low volume, distortion

**Impact**: Lower embedding quality, reduced similarity scores

**Solution**:
- Lower threshold for noisy environments
- Preprocess audio (noise reduction)
- Use multiple reference samples

---

## Threshold Tuning Guide

### Understanding Similarity Scores

- **0.90+**: Very high confidence (likely same speaker)
- **0.75-0.90**: High confidence (recommended threshold range)
- **0.60-0.75**: Medium confidence (may include errors)
- **<0.60**: Low confidence (likely different speakers)

### Tuning Strategy

```python
def evaluate_threshold(service, test_files, ground_truth, profile):
    """
    Test different thresholds to find optimal value
    """
    thresholds = [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]
    
    for threshold in thresholds:
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for file, true_segments in zip(test_files, ground_truth):
            results = service.process_audio(file, profile, threshold)
            
            # Compare with ground truth
            # ... evaluation logic ...
        
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        f1 = 2 * (precision * recall) / (precision + recall)
        
        print(f"Threshold {threshold:.2f}: P={precision:.2f}, R={recall:.2f}, F1={f1:.2f}")
```

**Recommended Defaults**:
- **Balanced**: 0.75
- **Strict** (minimize false positives): 0.85
- **Permissive** (maximize recall): 0.65

---

## Error Handling

```python
class SpeakerIdentificationService:
    def process_audio(self, audio_file, target_profile, threshold=0.75):
        try:
            # Validate input
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            # Check audio duration
            duration = self.audio.get_duration(audio_file)
            if duration < 1.0:
                raise ValueError(f"Audio too short: {duration:.1f}s (minimum 1s)")
            
            # Perform processing
            diarization = self.diarization_pipeline(audio_file)
            
            # ... rest of processing ...
            
        except Exception as e:
            print(f"❌ Error processing {audio_file}: {e}")
            raise
```

---

## Testing & Validation

### Unit Test Example

```python
import pytest

def test_speaker_profile_creation():
    service = SpeakerIdentificationService(use_gpu=False)
    profile = service.create_speaker_profile("test_audio.wav")
    
    assert 'embedding' in profile
    assert profile['embedding'].shape == (512,)
    assert profile['duration'] > 0

def test_speaker_identification():
    service = SpeakerIdentificationService(use_gpu=False)
    profile = service.create_speaker_profile("reference.wav")
    
    results = service.process_audio("meeting.wav", profile, threshold=0.75)
    
    assert len(results) > 0
    assert all('is_target' in r for r in results)
    assert all(0 <= r['similarity'] <= 1 for r in results)
```

---

## Troubleshooting

### Issue: "Model download fails"

**Solution**:
1. Check Hugging Face token
2. Accept user agreements
3. Check internet connection

```python
# Test authentication
from huggingface_hub import HfApi
api = HfApi()
user = api.whoami(token=os.getenv("HUGGING_FACE_HUB_TOKEN"))
print(f"Logged in as: {user['name']}")
```

### Issue: "CUDA out of memory"

**Solution**:
```python
# Use CPU instead
service = SpeakerIdentificationService(use_gpu=False)

# Or process shorter segments
# Or use smaller batch size
```

### Issue: "Low similarity scores for same speaker"

**Possible Causes**:
- Different recording conditions
- Background noise
- Different emotional state
- Poor reference audio quality

**Solutions**:
- Use multiple reference samples
- Lower threshold
- Improve reference audio quality
- Test with clean audio first

---

## Best Practices

1. **Reference Audio Quality**:
   - 30-60 seconds of clear speech
   - Minimal background noise
   - Natural conversation (not reading)
   - Multiple samples from different contexts

2. **Threshold Selection**:
   - Start with 0.75
   - Tune based on validation data
   - Different thresholds for different environments

3. **Performance**:
   - Use GPU for real-time applications
   - Batch process multiple files
   - Cache diarization results when tuning threshold

4. **Error Handling**:
   - Validate audio files before processing
   - Handle short segments gracefully
   - Provide fallback for overlapping speech

5. **Testing**:
   - Test with various audio qualities
   - Validate with ground truth data
   - Monitor false positive/negative rates

---

**Document Status**: Implementation Guide  
**Last Updated**: October 21, 2025  
**Next Steps**: Implement in project, validate with real data
