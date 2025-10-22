# Real-Time Monitoring Troubleshooting Guide

## Problem: Voice Not Detected When Speaking Close to Other Speakers

### Quick Diagnosis Process

#### Step 1: Clear Old Logs and Start Fresh

```bash
# Clear previous logs
./clear_logs.sh

# OR manually:
mkdir -p logs
rm -f logs/realtime_debug.log
```

#### Step 2: Start Application with Debug Logging

The `.env` file is already configured for detailed logging:

```bash
# These settings are already in your .env:
LOG_LEVEL=DEBUG
LOG_FILE=logs/realtime_debug.log
AUDIO_CHUNK_DURATION=1.5
AUDIO_OVERLAP_DURATION=0.75
```

Start the application:

```bash
streamlit run src/ui/app.py
```

#### Step 3: Reproduce the Problem

1. Go to **Live Monitoring** tab
2. Select your profile (**roie-ben-haim**)
3. Start monitoring
4. **Test Scenario:**
   - Play podcast for 3-4 seconds
   - Stop podcast
   - **Immediately** start speaking (no gap)
   - Speak for 5-10 seconds
   - Stop monitoring

#### Step 4: Analyze the Logs

```bash
python3 analyze_logs.py
```

This will show you:
- ✅ **Overall statistics** (chunks processed, target detected, transcribed)
- 🔊 **Audio levels** (RMS min/max/avg)
- 🎯 **Similarity scores** (TARGET vs OTHER)
- ⚠️ **Problem chunks** (speech detected but target missed)
- 📝 **Transcription timeline**
- 💡 **Recommendations** (threshold adjustments, profile quality)

---

## Understanding the Analysis Output

### 1. Overall Statistics

```
📊 OVERALL STATISTICS
  Total chunks processed: 45
  Skipped (too quiet): 12 (26.7%)
  No speech detected: 8 (17.8%)
  Speech but no target: 15 (33.3%)    ← ⚠️ THIS IS THE PROBLEM
  Target detected: 10 (22.2%)         ← ✅ TARGET FOUND
  Transcribed: 10 (22.2%)
```

**What to look for:**
- **High "Speech but no target"** = Your voice is being detected as OTHER speaker
- **Low "Target detected"** = Profile might not match well, or threshold too high

### 2. Similarity Scores

```
🎯 SIMILARITY SCORES
  TARGET segments:
    Count: 12
    Min: 0.758
    Max: 0.892
    Avg: 0.823

  OTHER segments:
    Count: 18
    Min: 0.420
    Max: 0.680    ← ⚠️ CLOSE TO THRESHOLD!
    Avg: 0.550
```

**What to look for:**
- **TARGET Min < 0.75** = Some of your speech falls below threshold → Lower threshold
- **OTHER Max > 0.70** = Other speakers score high → Risk of false positives
- **Small gap between TARGET and OTHER** = Hard to distinguish → Need better profile

### 3. Problem Chunks

```
⚠️ PROBLEM CHUNKS (Speech detected but target missed)
  Found 15 problem chunks:

  Chunk #1 at 2025-10-22 10:15:32
    RMS: 0.0234, Max: 0.1245
    Segments detected: 2
      [0.0s-0.8s] OTHER (similarity: 0.650)  ← Podcast
      [0.9s-1.5s] OTHER (similarity: 0.720)  ← YOUR VOICE but scored as OTHER!
```

**This is the smoking gun!** If you see segments at 0.720 similarity marked as OTHER, but your voice should be TARGET, it means:

1. **Your profile doesn't match well in this acoustic condition**
2. **Background noise is affecting the embedding**
3. **Need to adjust threshold or re-record profile**

---

## Common Issues and Solutions

### Issue 1: Threshold Too High

**Symptoms:**
- TARGET segments have Min similarity < 0.75
- Many "Speech but no target" chunks
- Your voice detected but marked as OTHER with similarity 0.65-0.74

**Solution:**

```bash
# Edit .env file
SIMILARITY_THRESHOLD=0.65  # Lower from 0.75 to 0.65
```

Or adjust in UI (Live Monitoring tab has threshold slider).

**Risk:** May get false positives from similar-sounding speakers.

---

### Issue 2: Profile Quality Issue

**Symptoms:**
- TARGET segments have low similarity (< 0.80)
- Other speakers score too high (> 0.65)
- Small gap between YOUR avg and OTHER avg

**Solution:**

Re-create your profile with better conditions:

1. **Use longer audio (30-60 seconds)**
2. **Record in same environment** where you'll use live monitoring
3. **Speak clearly, varied sentences**
4. **Avoid background noise** during enrollment
5. **Check quality score** - aim for ≥ 0.80 (Excellent or Good)

**Steps:**
1. Go to **Create New Profile**
2. Record 45-60 seconds of speech
3. Check quality assessment
4. If score < 0.75, record again in quieter environment

---

### Issue 3: Acoustic Mismatch

**Symptoms:**
- Profile created in quiet room, but live monitoring in noisy environment
- Profile created with good mic, but live monitoring with laptop mic
- Profile created close to mic, but live monitoring far away

**Solution:**

**Match enrollment conditions to usage conditions:**

| Enrollment | Usage | Result |
|------------|-------|--------|
| Quiet room + good mic | Same | ✅ Perfect |
| Quiet room + good mic | Noisy room + laptop mic | ❌ Poor |
| Noisy environment + laptop mic | Same | ✅ Works |

**Best Practice:** Record profile in the **same conditions** you'll use for monitoring.

---

### Issue 4: Speaker Overlap

**Symptoms:**
- When podcast plays WHILE you talk, both marked as OTHER
- Your voice only detected during pure solo speech

**Current Limitation:**

The diarization algorithm assumes **one speaker at a time**. When multiple people speak simultaneously:
- It picks the dominant speaker
- Your voice might be masked by louder background audio

**Workaround:**

1. **Lower background volume** when speaking
2. **Speak louder** than background audio
3. **Use directional microphone** (focuses on your voice, reduces background)

**Future Enhancement:** Add source separation (cocktail party problem).

---

## Advanced Tuning

### Chunk Duration vs Responsiveness

Current setting: **1.5 seconds**

| Duration | Responsiveness | Accuracy | CPU Load |
|----------|----------------|----------|----------|
| 1.0s | Very fast | Lower | High |
| 1.5s | Fast (current) | Good | Medium |
| 2.5s | Slower | Better | Low |
| 3.0s | Slow | Best | Very low |

**Edit `.env`:**
```bash
AUDIO_CHUNK_DURATION=1.0  # Faster but more CPU
```

---

### Overlap vs Transition Detection

Current setting: **0.75 seconds**

Higher overlap = better at catching speaker transitions, but more processing.

```bash
AUDIO_OVERLAP_DURATION=0.5   # Less overlap, faster
AUDIO_OVERLAP_DURATION=1.0   # More overlap, catches transitions better
```

---

## Step-by-Step Troubleshooting Example

### Scenario: You speak after podcast stops, but not detected

**1. Run monitoring and reproduce issue**

**2. Analyze logs:**

```bash
python3 analyze_logs.py
```

**3. Look at output:**

```
⚠️ PROBLEM CHUNKS
  Chunk #3 at 2025-10-22 10:15:34
    Segments detected: 1
      [0.3s-1.4s] OTHER (similarity: 0.685)  ← YOUR VOICE!
```

**4. Check similarity: 0.685**

This is YOUR voice but scored below threshold (0.75).

**5. Solution:**

Lower threshold to 0.65:

Edit `.env`:
```bash
SIMILARITY_THRESHOLD=0.65
```

**6. Re-test:**

Restart app, try again, check if your voice is now detected.

**7. If still not detected:**

Check if profile quality is good:
```bash
# In Streamlit app:
# Enrollment → Manage Profiles → Click on your profile
# Check Quality Score
```

If quality < 0.75, re-record profile.

---

## Quick Reference Commands

```bash
# Clear logs and start fresh
./clear_logs.sh

# Start application
streamlit run src/ui/app.py

# Analyze logs after monitoring
python3 analyze_logs.py

# View raw log file
tail -f logs/realtime_debug.log

# View last 100 lines
tail -n 100 logs/realtime_debug.log

# Search for specific pattern
grep "TARGET" logs/realtime_debug.log
grep "similarity" logs/realtime_debug.log
```

---

## What to Share for Help

If you still have issues after trying these steps, share:

1. **Log analysis output:**
   ```bash
   python3 analyze_logs.py > analysis.txt
   ```

2. **Your profile quality:**
   - Go to Enrollment → Manage Profiles
   - Click your profile
   - Screenshot the quality section

3. **Test scenario description:**
   - What audio was playing
   - When you started speaking
   - What you said
   - Whether detected or not

4. **Raw log snippet** (last 50 lines during problem):
   ```bash
   tail -n 50 logs/realtime_debug.log > problem_snippet.txt
   ```

---

## Expected Good Results

When working correctly, you should see:

```
📊 OVERALL STATISTICS
  Total chunks processed: 50
  Skipped (too quiet): 15 (30%)     ← Silence is normal
  No speech detected: 5 (10%)       ← Normal
  Speech but no target: 8 (16%)     ← OTHER speakers
  Target detected: 22 (44%)         ← ✅ YOU detected!
  Transcribed: 22 (44%)             ← ✅ YOUR speech transcribed

🎯 SIMILARITY SCORES
  TARGET segments:
    Min: 0.782    ← Above threshold ✅
    Max: 0.935    ← Strong match ✅
    Avg: 0.851    ← Good average ✅

  OTHER segments:
    Max: 0.650    ← Well below threshold ✅
```

---

## Troubleshooting Checklist

- [ ] Cleared old logs (`./clear_logs.sh`)
- [ ] LOG_LEVEL=DEBUG in `.env`
- [ ] Started Streamlit app
- [ ] Selected correct profile
- [ ] Reproduced the issue
- [ ] Stopped monitoring
- [ ] Ran log analysis (`python3 analyze_logs.py`)
- [ ] Checked similarity scores
- [ ] Checked profile quality (≥ 0.75)
- [ ] Adjusted threshold if needed
- [ ] Re-recorded profile if quality low
- [ ] Re-tested after changes

---

**Last Updated:** October 22, 2025  
**Version:** 1.0
