# Real-Time Monitoring Improvements

## Issue: Speaker Transition Detection

### Problem Description

User reported that live monitoring had issues detecting their voice in specific scenarios:

**Test 1: ✅ SUCCESS**
- User talks alone
- System correctly detects user's voice

**Test 2: ✅ SUCCESS**
- Podcast playing (other speakers)
- System correctly identifies as NOT the target speaker

**Test 3: ❌ FAILURE**
- Podcast plays → User stops podcast → User starts talking
- **Issue**: System only detects user's voice if there's a silence gap between podcast and user's speech
- **Problem**: If user speaks immediately after or during podcast, voice is NOT detected

### Root Cause Analysis

The issue occurred due to the **audio buffering and processing window**:

1. **Large chunk size (3 seconds)**
   - System waits for 3 seconds of audio before processing
   - When podcast plays for 2s then user speaks for 1s:
     - Chunk contains: `[2s podcast + 1s user voice]`
     - Diarization sees podcast as dominant speaker (majority vote)
     - User's voice is lost/misidentified

2. **Insufficient overlap (1 second)**
   - Chunks slide by 2 seconds (3s chunk - 1s overlap)
   - Speaker transitions between chunks can be missed
   - Not enough context to detect rapid speaker changes

3. **No transition detection**
   - System processes each chunk independently
   - No comparison between consecutive chunks to detect speaker changes

### Solution Implemented

#### Change 1: Reduced Chunk Duration

**Before:**
```python
AUDIO_CHUNK_DURATION = 3.0 seconds
```

**After:**
```python
AUDIO_CHUNK_DURATION = 1.5 seconds
```

**Benefit:**
- Faster processing (1.5s instead of 3s)
- Smaller window = less chance of mixing multiple speakers
- Quicker response to speaker changes
- Better real-time user experience

#### Change 2: Increased Overlap

**Before:**
```python
AUDIO_OVERLAP_DURATION = 1.0 second
→ Slides by 2.0 seconds per iteration
```

**After:**
```python
AUDIO_OVERLAP_DURATION = 0.75 seconds
→ Slides by 0.75 seconds per iteration
```

**Benefit:**
- More frequent processing updates
- Better coverage of speaker transitions
- Less chance of missing speech at chunk boundaries
- Smoother continuous monitoring

#### Change 3: Enhanced Logging

**Added detailed speaker detection logging:**

```python
# Log all detected speakers with similarity scores
for seg in identified:
    speaker_type = "TARGET" if seg.get('is_target') else "OTHER"
    similarity = seg.get('similarity', 0.0)
    logger.info(f"  Segment [{seg['start']:.1f}s-{seg['end']:.1f}s]: {speaker_type} (similarity: {similarity:.3f})")
```

**Benefit:**
- Clear visibility into what's being detected
- Similarity scores help debug edge cases
- Easier to tune threshold if needed

## Expected Behavior After Fix

### Test 3: Podcast → User Speech (SHOULD NOW WORK)

**Scenario:**
1. Podcast plays for 2 seconds
2. User stops podcast immediately
3. User starts speaking

**Expected Processing:**

**Chunk 1 (0.0s - 1.5s):**
- Contains: Podcast audio
- Detection: OTHER speaker (not target)
- Result: No transcription ✓

**Chunk 2 (0.75s - 2.25s):**
- Contains: 0.75s podcast + 0.75s user voice
- Detection: BOTH speakers (diarization splits segment)
- Result: Only user's portion transcribed ✓

**Chunk 3 (1.5s - 3.0s):**
- Contains: User voice
- Detection: TARGET speaker
- Result: Transcription ✓

**Key Improvement:** User's voice is now detected within 1.5-2.25 seconds instead of being lost in a 3-second podcast-dominated chunk.

## Performance Considerations

### Processing Load

**Before:**
- Process every 2 seconds (3s chunk - 1s overlap)
- ~0.5 processing calls per second

**After:**
- Process every 0.75 seconds (1.5s chunk - 0.75s overlap)
- ~1.33 processing calls per second

**Impact:**
- ~2.7x more processing calls
- Higher CPU/GPU usage
- Trade-off: Better accuracy for higher compute cost
- GPU acceleration (MPS/CUDA) should handle this easily

### Memory Usage

**Before:**
- 3 seconds * 16kHz = 48,000 samples per chunk

**After:**
- 1.5 seconds * 16kHz = 24,000 samples per chunk

**Impact:**
- 50% less memory per chunk
- More chunks in flight simultaneously
- Overall memory usage similar or slightly higher

## Configuration Options

Users can customize these values via environment variables:

```bash
# .env file
AUDIO_CHUNK_DURATION=1.5    # Chunk size in seconds (default: 1.5)
AUDIO_OVERLAP_DURATION=0.75  # Overlap in seconds (default: 0.75)
```

**Tuning Guidelines:**

| Use Case | Chunk Duration | Overlap | Trade-off |
|----------|----------------|---------|-----------|
| **Fast transitions** | 1.0s | 0.5s | High CPU, best responsiveness |
| **Balanced (current)** | 1.5s | 0.75s | Moderate CPU, good responsiveness |
| **Low resource** | 2.5s | 1.0s | Low CPU, slower response |

## Future Enhancements

### 1. Voice Activity Detection (VAD)

Add pre-processing step to detect speech vs silence:

```python
# Detect speech regions first
speech_regions = vad.detect_speech(audio_chunk)

# Only process chunks with actual speech
if speech_regions:
    diarize_and_process(speech_regions)
```

**Benefits:**
- Skip silent chunks entirely
- Reduce false positives
- Lower processing load

### 2. Speaker Change Detection

Track embedding changes between consecutive chunks:

```python
# Compare current chunk embedding with previous
if embedding_distance(prev_embedding, curr_embedding) > threshold:
    logger.info("Speaker change detected!")
    # Process transition more carefully
```

**Benefits:**
- Explicit detection of speaker transitions
- Better handling of overlapping speech
- Improved accuracy at boundaries

### 3. Adaptive Thresholding

Dynamically adjust similarity threshold based on audio quality:

```python
# Lower threshold in noisy environments
if snr < 10:
    effective_threshold = base_threshold * 0.9
else:
    effective_threshold = base_threshold
```

**Benefits:**
- Better performance in varied acoustic conditions
- Fewer false negatives in noisy environments
- More robust real-world operation

### 4. Multi-Scale Processing

Process at multiple time scales simultaneously:

```python
# Process short chunks for responsiveness
short_chunk_result = process_chunk(audio, duration=1.0)

# Process longer chunks for accuracy
long_chunk_result = process_chunk(audio, duration=3.0)

# Combine results
final_result = combine_with_confidence(short_chunk_result, long_chunk_result)
```

**Benefits:**
- Fast response + high accuracy
- Better handling of edge cases
- More robust to different speech patterns

## Testing Recommendations

After this fix, test the following scenarios:

1. **Continuous Speech**
   - User talks continuously for 30+ seconds
   - Should transcribe all speech with no gaps

2. **Rapid Speaker Changes**
   - Alternate between podcast and user every 2-3 seconds
   - Should correctly identify each speaker

3. **Overlapping Speech**
   - Play podcast while user talks simultaneously
   - Should detect user's voice even with background

4. **Variable Noise Levels**
   - Test in quiet and noisy environments
   - Verify threshold is appropriate for both

5. **Different Speech Patterns**
   - Short utterances (1-2 words)
   - Long sentences
   - Pauses between words

## Summary

This fix addresses the core issue of speaker transition detection by:

1. ✅ **Reducing chunk size from 3s to 1.5s** - faster response, smaller mixing window
2. ✅ **Increasing overlap from 1s to 0.75s** - better transition coverage
3. ✅ **Enhanced logging** - better visibility into detection process

**Expected Outcome:** User's voice should now be detected within 1.5-2.25 seconds of speaking, even immediately after background audio stops, without requiring a silence gap.

---

**Document Version:** 1.0  
**Date:** October 22, 2025  
**Status:** Implemented, Ready for Testing
