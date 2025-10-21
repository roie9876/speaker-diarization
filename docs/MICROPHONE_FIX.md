# Quick Fix: Increase Microphone Volume

## Your Current Status
✅ Microphone is working  
⚠️  Volume is too quiet (RMS: 0.0083, should be > 0.02)

## Steps to Fix:

### 1. Increase Microphone Input Level (macOS)

1. Open **System Preferences** (or **System Settings** on newer macOS)
2. Go to **Sound** → **Input**
3. Select "MacBook Pro Microphone" (or your preferred mic)
4. Drag the **Input volume** slider to **75-100%**

### 2. Test Again

```bash
cd "/Users/robenhai/speaker diarization"
source venv/bin/activate
python test_microphone.py
```

**Target levels:**
- Average RMS: **> 0.02** (currently 0.0083)
- Peak RMS: **> 0.05** (currently 0.0214)

### 3. Restart the App

```bash
streamlit run src/ui/app.py
```

Now with DEBUG logging enabled, you'll see detailed logs showing:
- Audio chunks being processed
- Speech segments detected
- Similarity scores

### 4. Try Live Monitoring Again

- Go to Live Monitoring tab
- Select your profile
- **Lower threshold to 0.65-0.70**
- Start monitoring
- **Speak clearly and loudly**

### What to Look For in Logs:

**Good signs:**
```
Audio chunk: RMS=0.0523, Max=0.3412
Found 2 speech segment(s) in chunk
Segment similarity: 0.723
```

**Bad signs:**
```
Chunk too quiet, skipping  <-- Mic volume too low
No speech segments detected  <-- Diarization can't find speech
```

## Alternative: Use Different Microphone

Your test showed 4 available microphones:
- [1] OWC Thunderbolt 3 Audio Device
- [2] MacBook Pro Microphone (currently used)
- [4] Microsoft Teams Audio
- [5] Speaker Audio Recorder

Try selecting a different one in the Live Monitoring tab if the built-in mic is too quiet.

## Still Having Issues?

Play back the test recording to verify it captured your voice:
```bash
afplay data/temp/mic_test.wav
```

If it's silent or very quiet, the issue is with your Mac's audio settings, not the app.
