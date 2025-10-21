# Speaker Recognition Troubleshooting Guide

## Problem: System Not Recognizing Your Voice

### Possible Causes & Solutions

#### 1. **No Speech Detected (0 segments)**
**Symptoms:** Logs show "0 segments, 0 speakers"

**Causes:**
- Audio level too low
- Voice Activity Detection (VAD) filtering out speech
- Short audio chunks

**Solutions:**
- ✅ **Increased chunk duration to 5 seconds** (was 3s)
- Speak louder and clearer into the microphone
- Check microphone input level in System Preferences > Sound
- Reduce background noise

#### 2. **Speech Detected But Not Matched**
**Symptoms:** Logs show segments found but similarity score < 0.75

**Causes:**
- Profile created with different audio quality/microphone
- Profile audio too short
- Threshold too strict

**Solutions:**
- **Lower the similarity threshold** in UI (try 0.65-0.70)
- **Re-create profile** with:
  - Same microphone as testing
  - Longer recording (10-15 seconds)
  - Clear speech, normal volume
  - No background noise

#### 3. **Test Your Profile**

Use the test script to check if your profile works:

```bash
cd "/Users/robenhai/speaker diarization"
source venv/bin/activate

# Record a test clip (or use existing audio)
python test_profile_recognition.py test_audio.wav roie1
```

This will show you:
- Similarity score between profile and test audio
- Whether it would match at different thresholds
- Tips for improvement

### Quick Fix Steps

1. **Restart the app:**
   ```bash
   streamlit run src/ui/app.py
   ```

2. **In the app:**
   - Go to **Enrollment** tab
   - Create a NEW profile with:
     - **Record from Microphone** selected
     - Speak clearly for **10-15 seconds**
     - Say varied phrases (count to 10, say your name, etc.)

3. **In Live Monitoring tab:**
   - Select the new profile
   - **Lower threshold to 0.70** (use slider)
   - Click "Start Monitoring"
   - Speak clearly with normal volume

4. **Watch the logs** for:
   ```
   Found X speech segment(s) in chunk
   Segment similarity: 0.XXX
   ```

### Understanding Similarity Scores

- **0.85+** = Excellent match (same person, same recording)
- **0.75-0.85** = Good match (default threshold)
- **0.65-0.75** = Moderate match (might need lower threshold)
- **<0.65** = Poor match (different person or quality issue)

### Debug Mode

To see detailed audio processing info, change in `.env`:
```properties
LOG_LEVEL=DEBUG
```

This will show:
- Audio chunk levels (RMS, Max amplitude)
- Whether chunks are being skipped as "too quiet"
- Exact similarity scores for each segment

### Still Not Working?

Check these files in `data/temp/`:
- Look for `realtime_chunk_*.wav` files
- Play them back to verify they contain your voice
- If files are silent or distorted, it's an audio capture issue

### Advanced: Manual Testing

Test the diarization service directly:

```python
from src.services.diarization_service import DiarizationService

service = DiarizationService()
segments = service.diarize("path/to/your/audio.wav")
print(f"Found {len(segments)} segments")
for seg in segments:
    print(f"  {seg['start']:.1f}s - {seg['end']:.1f}s: {seg['speaker_label']}")
```

If this returns 0 segments, the issue is with the diarization pipeline detecting speech, not with identification.

---

## Changes Made to Fix Recognition Issues

1. ✅ **Increased chunk duration**: 3s → 5s (more audio for diarization)
2. ✅ **Added audio level checking**: Skips silent chunks (RMS < 0.01)
3. ✅ **Enhanced logging**: Shows similarity scores and segment detection
4. ✅ **Fixed diarization API**: Updated for pyannote.audio 4.0+
5. ✅ **Test script**: `test_profile_recognition.py` for debugging

## Recommended Workflow

1. Create profile with microphone recording (10-15s)
2. Test profile with test script
3. If similarity < 0.75, recreate profile or lower threshold
4. Use Live Monitoring with adjusted threshold
5. Monitor logs to see detection in real-time
