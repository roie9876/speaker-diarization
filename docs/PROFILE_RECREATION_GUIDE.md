# Profile Re-creation Guide for Better Live Matching

## Current Issue

- ✅ Multi-speaker detection is working (finds 1-2 speakers per chunk)
- ✅ Threshold is 0.50
- ❌ Your voice similarity: 0.1-0.5 (too low, inconsistent)
- ❌ Only 2 segments > 0.50 threshold
- ❌ Most of your speech rejected

## Root Cause

**Profile doesn't match your live microphone voice!**

Possible reasons:
1. Profile was created with different microphone settings
2. Profile was created in very quiet room, live has background noise
3. Profile audio had different processing/quality
4. Microphone position/distance different

## Solution: Create Better Profile

### Step 1: Record Profile in SAME Conditions as Live Use

**Important:** Record the profile using the **EXACT SAME setup** you'll use for live monitoring:

1. **Go to "Create New Profile" tab**
2. **Select "Record from Microphone"** (don't upload file!)
3. **Use MacBook Pro Microphone** (same as live monitoring)
4. **Record in SAME location** where you'll use live monitoring
5. **Similar background noise** (if you'll have music/talking in background during live, have it during recording too!)
6. **Same distance from mic** (e.g., normal laptop position)
7. **Record 45-60 seconds** of varied speech
   - Say different sentences
   - Vary your tone (normal, louder, quieter)
   - Include pauses
8. **Check quality score** - aim for ≥ 0.75

### Step 2: What to Say During Recording

Speak naturally for 45-60 seconds. Example:

```
שלום, שמי רועי. אני מקליט את הפרופיל שלי עכשיו.
אני אומר משפטים שונים כדי שהמערכת תלמד את הקול שלי.
אני משנה את הטון, מדבר קצת יותר חזק ואחר כך יותר שקט.
זה חשוב שהמערכת תזהה אותי גם כשיש רעש ברקע.
אני ממשיך לדבר עוד קצת כדי שיהיו מספיק דוגמאות.
זה נראה טוב, עוד כמה משפטים ואני אסיים.
תודה רבה על הסבלנות, זה הפרופיל החדש שלי.
```

### Step 3: Test Profile Quality

After creating profile:
1. Check quality score in UI
2. If < 0.75, delete and re-record
3. If ≥ 0.80, proceed to test

### Step 4: Test with Live Monitoring

1. Clear logs: `./clear_logs.sh`
2. Start app
3. Select NEW profile
4. Test live monitoring with podcast scenario
5. Check logs: `python3 analyze_logs.py`

### Expected Results After Good Profile

```
📊 OVERALL STATISTICS
  Target detected: 40-50%      ← Should be much higher!
  Transcribed: 40-50%          ← More transcripts!

🎯 SIMILARITY SCORES
  TARGET segments:
    Min: 0.750                 ← Above threshold!
    Max: 0.920                 ← Strong match!
    Avg: 0.835                 ← Consistently high!
```

## Advanced: Profile Quality Self-Test

After creating profile, immediately test it:

```bash
python3 test_profile_match.py
```

This will:
- Extract embedding from your enrollment audio
- Compare it to the saved profile
- Should show similarity > 0.90 (self-match)

If self-match < 0.90, there's a bug (report it).

## Troubleshooting Low Similarity

### If similarity still low after re-recording:

#### Option 1: Record Multiple Profiles

Create 2-3 profiles of yourself:
- Profile 1: Quiet room, close to mic
- Profile 2: With background music
- Profile 3: Further from mic

Use the one that gives best results.

#### Option 2: Adjust Recording Technique

- **Speak directly toward microphone**
- **Consistent distance** (about 30-50cm)
- **Clear articulation** (not mumbling)
- **Vary pitch and volume** during recording
- **Avoid extreme quiet or loud** (stay in normal range)

#### Option 3: Check Microphone Settings

```bash
# List audio devices
python3 list_audio_devices.py

# Make sure using MacBook Pro Microphone
# Check sample rate (should be 48000 Hz)
```

#### Option 4: Environmental Match

**Key principle:** Record profile in the SAME acoustic environment as live use.

| Profile Recorded | Live Monitoring | Match Quality |
|------------------|-----------------|---------------|
| Quiet room, close mic | Quiet room, close mic | ✅ Excellent |
| Quiet room, close mic | Noisy room, far mic | ❌ Poor |
| With music background | With music background | ✅ Good |
| Quiet | With podcast playing | ⚠️ Fair |

## Quick Fix Test

Before re-creating profile, try lowering threshold even more:

```bash
# Edit .env
SIMILARITY_THRESHOLD=0.35

# Restart app and test
# If many false positives (other speakers detected as you), threshold too low
# If still missing you, profile needs re-recording
```

**Optimal threshold range: 0.50-0.70**

## Summary

1. 🎤 **Delete current profile**
2. 🎙️ **Record new profile** using "Record from Microphone"
3. 📍 **Same conditions** as live monitoring (location, mic, noise level)
4. ⏱️ **45-60 seconds** of varied speech
5. ✅ **Check quality ≥ 0.75**
6. 🧪 **Test live monitoring**
7. 📊 **Analyze logs** - should see 40-50% target detected

**Goal:** Similarity scores consistently 0.75-0.90 for your voice!

---

**Last Updated:** October 22, 2025
