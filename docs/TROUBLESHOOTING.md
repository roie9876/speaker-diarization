# Troubleshooting Real-Time Voice Detection

## Quick Start

### 1. Clear Logs
```bash
./clear_logs.sh
```

### 2. Start Application
```bash
streamlit run src/ui/app.py
```

### 3. Test Live Monitoring
- Go to **Live Monitoring** tab
- Select your profile
- Start monitoring
- **Test:** Play podcast → Stop → Start speaking immediately
- Stop monitoring

### 4. Analyze Results
```bash
python3 analyze_logs.py
```

## What You'll See

The analyzer will show:

- **📊 Statistics**: How many chunks detected target vs other
- **🎯 Similarity Scores**: Your voice vs other speakers
- **⚠️ Problem Chunks**: Where your voice was missed
- **💡 Recommendations**: Threshold adjustments, profile improvements

## Common Solutions

### If your voice is not detected:

**Check similarity scores in analysis:**

```
TARGET Min: 0.685  ← Below threshold (0.75)
```

**Solution:** Lower threshold in `.env`:
```bash
SIMILARITY_THRESHOLD=0.65
```

### If profile quality is low:

**Check in app:** Enrollment → Manage Profiles → Click your profile

**If Quality Score < 0.75:**
- Re-record profile with 45-60 seconds of clear speech
- Use same microphone/environment as live monitoring
- Reduce background noise during recording

## Files

- **analyze_logs.py** - Analyzes log file and finds issues
- **clear_logs.sh** - Clears old logs for fresh session
- **logs/realtime_debug.log** - Detailed debug log (created when app runs)
- **docs/TROUBLESHOOTING_REALTIME.md** - Complete troubleshooting guide

## Need More Help?

See full guide: `docs/TROUBLESHOOTING_REALTIME.md`
