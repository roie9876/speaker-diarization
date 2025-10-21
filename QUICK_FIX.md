# Quick Fix Guide

## Issue 1: Wrong Embedding Shape (FIXED ✅)

**Problem**: Profile was created with embedding shape (7680,) instead of (512,)

**Solution**: Code now automatically averages multiple frame embeddings into a single (512,) embedding

**Action Required**: 
1. Delete your current profile "roie-ben-haim" in the Enrollment tab
2. Recreate it with the same audio - it will now have the correct (512,) shape

---

## Issue 2: Microphone Not Working

**Problem**: Audio RMS=0.0000 (no sound being captured)

**Cause**: You selected device=4, but previously device=2 was working

**Solution**:

### Step 1: Check which device is your microphone
```bash
cd "/Users/robenhai/speaker diarization"
source venv/bin/activate
python test_microphone.py
```

This will:
- List all audio devices
- Show which one is your Mac's built-in microphone
- Test recording from it

### Step 2: In Streamlit Live Monitoring tab
- Try different devices from the dropdown
- Look for one that shows "Built-in Microphone" or similar
- Device index 2 worked before, try that first

### Step 3: Verify audio capture
When you select the correct device, you should see:
- Audio RMS > 0.02 when speaking (in logs)
- Progress bar moving in the UI
- "🎤 Detecting: X%" message

---

## Complete Steps to Test

1. **Restart Streamlit** (apply the embedding fixes):
   ```bash
   streamlit run src/ui/app.py
   ```

2. **Delete old profile**:
   - Go to Enrollment tab
   - Delete "roie-ben-haim" profile

3. **Create new profile**:
   - Record 10-15 seconds of clear speech
   - System will now create correct (512,) embedding
   - Check logs for: "Final embedding shape: (512,)"

4. **Test microphone**:
   - Run test_microphone.py to find correct device
   - Note the device index that works

5. **Test live monitoring**:
   - Go to Live Monitoring tab
   - Select your new profile
   - Select correct microphone device
   - Lower threshold to 0.65
   - Start monitoring and speak

6. **Expected results**:
   - Logs show: RMS > 0.02 when speaking
   - Logs show: "Segment similarity: 0.XXX" (real number, not 0.000)
   - If similarity > threshold: Transcription appears!

---

## What Was Fixed

### Embedding Extraction (identification_service.py)
- Now detects when pyannote returns multiple frame embeddings (N, 512)
- Automatically averages them into single embedding (512,)
- Profile creation now produces correct shape

### Embedding Comparison (identification_service.py)
- Added shape validation before comparison
- Added automatic flattening as safety measure
- Better error messages showing both shapes

---

## Still Not Working?

**If similarity scores are still 0.000:**
- Check logs for "Embedding shape mismatch" errors
- Run: `python test_profile_recognition.py audio.wav profile_name`

**If microphone still silent:**
- Check macOS System Preferences > Sound > Input
- Increase input volume to 75-100%
- Make sure correct device is selected

**If similarity scores are real but low (<0.50):**
- Recreate profile with longer, clearer audio (15-20 seconds)
- Speak naturally, avoid background noise
- Lower threshold to 0.60 for testing

---

Last Updated: October 21, 2025
