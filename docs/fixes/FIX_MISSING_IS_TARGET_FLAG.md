# Fix: Missing is_target Flag in Transcription Results

**Date**: October 22, 2025  
**Issue**: Transcripts showing as [OTHER] despite segments being detected as TARGET  
**Root Cause**: `is_target` flag not preserved in transcription service  
**Status**: ✅ FIXED

---

## Problem Description

### Symptoms
- Speaker correctly detected as TARGET in logs
- Similarity scores passing threshold (0.427, 0.410 with threshold 0.40)
- Transcription working (Hebrew text detected)
- **BUT**: UI showing "Speaker detected in segments" with NO transcripts displayed
- Logs showing: `Real-time transcript [OTHER]` instead of `[TARGET]`

### Log Evidence
```
2025-10-22 15:29:48,963 - Segment [0.0s-2.6s]: TARGET (similarity: 0.427)
2025-10-22 15:29:54,100 - Real-time transcript [OTHER]: [0.0s] מראה שהוא מזמן....
```

**Issue**: Segment marked TARGET, but transcript marked OTHER

---

## Root Cause Analysis

### Detection Flow (Working)
```python
# In realtime_processor.py line 356-374
identified = self.identification.identify_segments(
    audio_file=temp_file,
    segments=segments,
    target_embedding=target_profile['embedding'],
    threshold=self.threshold
)

# Sets is_target=True for matching segments ✅
```

### Transcription Flow (Broken)
```python
# In transcription_service.py line 415-420
result["speaker_label"] = segment.get("speaker_label", "UNKNOWN")
result["similarity"] = segment.get("similarity", 0.0)
# ❌ MISSING: result["is_target"] = segment.get("is_target", False)
```

**Problem**: The `transcribe_segments` function receives segments with `is_target` flag, but doesn't copy it to the result dictionary.

### Display Flow (Working but No Data)
```python
# In realtime_processor.py line 389-391
is_target = transcript.get("is_target", False)  # Always False!
speaker_type = "TARGET" if is_target else "OTHER"
```

**Result**: All transcripts marked as OTHER, filtered out by UI

---

## Solution

### File: `src/services/transcription_service.py`

**Line 417-418** (after adding similarity):
```python
# Add segment metadata
result["speaker_label"] = segment.get("speaker_label", "UNKNOWN")
result["similarity"] = segment.get("similarity", 0.0)
result["is_target"] = segment.get("is_target", False)  # ✅ ADDED
```

**Line 430** (error handling case):
```python
results.append({
    "start": segment["start"],
    "end": segment["end"],
    "text": "",
    "confidence": 0.0,
    "speaker_label": segment.get("speaker_label", "UNKNOWN"),
    "similarity": segment.get("similarity", 0.0),
    "is_target": segment.get("is_target", False),  # ✅ ADDED
    "language": language
})
```

---

## Testing

### Before Fix
```
Detection: TARGET (similarity: 0.427) ✅
Transcription: "מראה שהוא מזמן...." (15 chars) ✅
Marking: [OTHER] ❌
UI Display: Nothing shown ❌
```

### After Fix (Expected)
```
Detection: TARGET (similarity: 0.427) ✅
Transcription: "מראה שהוא מזמן...." (15 chars) ✅
Marking: [TARGET] ✅
UI Display: Green box with transcript ✅
```

---

## Related Files

- `src/services/transcription_service.py` - Fixed to preserve `is_target` flag
- `src/processors/realtime_processor.py` - Already correct, uses the flag
- `src/ui/live_tab.py` - Already correct, filters by `is_target`

---

## Additional Improvements Made

### 1. UI Reload Configuration Button
Added **🔄 Reload Config** button in Live Monitoring tab to reload .env values without restarting app.

### 2. Configuration Display
Added expandable section showing current settings:
- Similarity Threshold (from .env)
- VAD Threshold (0.3)
- Audio Amplification (3x)

### 3. Dynamic Threshold Slider
Changed threshold slider to:
- Min: 0.3 (was 0.5)
- Default: Load from .env
- Help text shows current .env value

### 4. Audio Amplification
Added 3x amplification in `realtime_processor.py` to boost quiet microphones:
```python
audio_data = audio_data * 3.0
audio_data = np.clip(audio_data, -1.0, 1.0)
```

### 5. Lower VAD Threshold
Reduced VAD sensitivity in `diarization_service.py`:
- onset: 0.4 → 0.3
- offset: 0.4 → 0.3

---

## Validation Checklist

After app restart, verify:
- [ ] Threshold shows 0.40 in UI (from .env)
- [ ] "Current Configuration Values" shows correct settings
- [ ] Speaker detected as TARGET (green) in logs
- [ ] Transcripts appear in UI with green boxes
- [ ] Transcripts marked as [TARGET] not [OTHER]
- [ ] Hebrew/English text displays correctly
- [ ] 🔄 Reload Config button works

---

## User Instructions

1. **Restart the Streamlit app** to load the fix
2. Go to **Live Monitoring** tab
3. Expand **"📊 Current Configuration Values"** - verify shows 0.40 threshold
4. Select your profile
5. Click **Start Monitoring**
6. **Speak clearly** for 5-10 seconds
7. **Expected**: See green boxes with your transcripts
8. If settings change, use **🔄 Reload Config** instead of restarting

---

## Technical Notes

This was a classic "lost flag" bug where:
1. Flag correctly set at source (identification)
2. Flag lost in intermediate processing (transcription)
3. Flag checked at destination (realtime processor + UI)
4. Result: Working detection, working transcription, but invisible to user

The fix ensures the `is_target` flag is **preserved throughout the entire pipeline** from detection → transcription → display.

---

**Status**: ✅ Fixed, ready for testing  
**Priority**: CRITICAL (blocking feature)  
**Impact**: High (main user-facing feature)
