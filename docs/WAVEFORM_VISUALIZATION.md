# Live Audio Waveform Visualization - Implementation Summary

## ✅ Feature Added: Real-Time Waveform Display

A live audio waveform visualization has been added to the Live Monitoring tab, similar to the recording interface shown in your screenshot.

---

## 📊 What Was Implemented

### Backend Changes (realtime_processor.py)

1. **Waveform Buffer** - Added a rolling 2-second audio buffer:
   ```python
   self.waveform_buffer_size = int(self.sample_rate * 2)  # 2 seconds
   self.waveform_buffer = np.zeros(self.waveform_buffer_size, dtype=np.float32)
   ```

2. **Buffer Updates** - Audio callback now updates the waveform buffer in real-time:
   ```python
   # Rolling window - keeps last 2 seconds of audio
   self.waveform_buffer = np.roll(self.waveform_buffer, -len(audio_data))
   self.waveform_buffer[-len(audio_data):] = audio_data
   ```

3. **Waveform Data Method** - New `get_waveform_data()` method:
   - Downsamples the 2-second buffer to 100-200 points for efficient plotting
   - Preserves audio peaks using max absolute value
   - Returns ready-to-plot array

### Frontend Changes (live_tab.py)

1. **Imports Added**:
   ```python
   import numpy as np
   import plotly.graph_objects as go
   ```

2. **Waveform Visualization** - Added interactive Plotly chart:
   - Shows last 2 seconds of audio
   - Time axis from -2s to 0s (current moment)
   - Amplitude range: -1 to +1
   - Filled area under curve
   - Hover tooltips showing exact values
   - Auto-updating (refreshes with Streamlit rerun)

3. **Chart Styling**:
   - Blue gradient fill (#1f77b4 with 30% opacity)
   - Grid lines for easy reading
   - Zero line highlighted
   - Compact height (200px)
   - Full width responsive

---

## 🎨 Visual Features

### The waveform display shows:
- **Amplitude bars** - Height represents volume
- **Time axis** - Horizontal (last 2 seconds)
- **Fill effect** - Area under waveform
- **Interactive** - Hover to see exact values
- **Real-time** - Updates continuously while monitoring

### Layout:
```
🎙️ Live Audio Waveform
┌────────────────────────────────────┐
│  [Live waveform chart with peaks]  │
│  Time: -2s ────────────────► 0s    │
└────────────────────────────────────┘

📊 Audio Level          🗣️ Speech Detection
[Progress bar]          [Target match status]
```

---

## 🚀 How to Test

### 1. Restart Streamlit:
```bash
cd "/Users/robenhai/speaker diarization"
source venv/bin/activate
streamlit run src/ui/app.py
```

### 2. Go to Live Monitoring Tab

### 3. Select:
- Your profile
- Correct microphone device
- Lower threshold to 0.65

### 4. Start Monitoring

### 5. Speak into the microphone

### 6. Expected Behavior:
- **Waveform** shows live audio bars moving
- **Peaks** when you speak
- **Flat line** when silent
- **Audio Level** progress bar matches waveform intensity
- **Speech Detection** shows "Voice detected" when waveform shows activity

---

## 🔧 Technical Details

### Performance:
- **Buffer Size**: 32,000 samples (2 seconds @ 16kHz)
- **Display Points**: 200 samples (160x downsampling)
- **Update Rate**: Follows Streamlit refresh (~1-2 times/second)
- **Memory**: ~128KB per buffer (minimal overhead)

### Downsampling Algorithm:
```python
# For each window of N samples:
peak = max(abs(window)) * sign(mean(window))
```
This preserves the visual appearance of peaks while reducing data points.

### Data Flow:
```
Microphone Input
    ↓
PyAudio Callback (1024 samples/chunk, ~60Hz)
    ↓
Rolling Buffer Update (last 32,000 samples)
    ↓
get_waveform_data() - Downsample to 200 points
    ↓
Plotly Chart Rendering
    ↓
Streamlit Display (auto-refresh)
```

---

## 🎯 Benefits

1. **Visual Feedback** - Immediate confirmation that microphone is working
2. **Volume Monitoring** - See if you need to speak louder/softer
3. **Silence Detection** - Easily spot when audio isn't being captured
4. **Professional Look** - Modern, interactive visualization
5. **Debugging** - Quickly identify audio issues (flat line = no input)

---

## 🐛 Troubleshooting

### If waveform is flat (no movement):
1. Wrong microphone selected - try different devices
2. Microphone volume too low - increase in System Preferences
3. Mic permissions - check macOS Privacy settings
4. Device=4 may be wrong - try device=2 (worked before)

### If waveform shows but no recognition:
1. Profile embedding issue - recreate profile
2. Threshold too high - lower to 0.60-0.65
3. Check logs for similarity scores

### If "Unable to display waveform" error:
1. Check plotly is installed: `pip show plotly`
2. Check terminal logs for detailed error
3. Numpy/Plotly version conflict (unlikely)

---

## 📝 Code Locations

**Backend**: `/src/processors/realtime_processor.py`
- Lines 73-76: Waveform buffer initialization
- Lines 258-262: Buffer update in audio callback
- Lines 479-520: get_waveform_data() method

**Frontend**: `/src/ui/live_tab.py`
- Lines 10-11: Import statements
- Lines 168-220: Waveform visualization section

---

## 🎨 Customization Options

You can easily customize the waveform appearance by editing `live_tab.py`:

### Change colors:
```python
line=dict(color='#FF6B6B', width=2),  # Red waveform
fillcolor='rgba(255, 107, 107, 0.3)',  # Red fill
```

### Show longer history (4 seconds):
In `realtime_processor.py`:
```python
self.waveform_buffer_size = int(self.sample_rate * 4)
```

### Higher resolution (more points):
In `live_tab.py`:
```python
waveform = realtime_processor.get_waveform_data(num_samples=400)
```

### Taller chart:
```python
fig.update_layout(height=300)  # Default is 200
```

---

## ✨ Future Enhancements (Optional)

Possible additions if you want:
1. **Frequency spectrum** (FFT visualization)
2. **Multiple colors** (different color when target speaker detected)
3. **Zoom controls** (adjust time window)
4. **Peak indicators** (highlight loud sections)
5. **Recording indicator** (red dot when saving)
6. **Playback** (play back recent audio segments)

---

**Created**: October 21, 2025  
**Status**: ✅ Ready to Use  
**Dependencies**: numpy, plotly (already installed)

