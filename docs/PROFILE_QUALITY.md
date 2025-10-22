# Profile Quality Assessment

## Overview

The Profile Quality Assessment feature evaluates the quality of speaker enrollment profiles to help users create optimal voice fingerprints for accurate speaker identification.

## What It Measures

### 1. Duration Score (25% weight)
- **Ideal**: 30-60 seconds
- **Minimum**: 10+ seconds recommended
- **Why**: Longer audio provides more voice characteristics for better matching

### 2. Audio Level Score (25% weight)
- **Ideal RMS**: 0.05-0.3
- **Peak Level**: < 0.95 (to avoid clipping)
- **Why**: Good audio levels ensure clear voice capture without distortion

### 3. Embedding Quality Score (30% weight)
- **Embedding Norm**: Should be ~1.0 (normalized)
- **Embedding Std**: 0.05-0.5 (shows voice variation)
- **Why**: Well-formed embeddings indicate clear, consistent voice capture

### 4. Signal-to-Noise Ratio (SNR) Score (20% weight)
- **Excellent**: > 20 dB
- **Good**: 15-20 dB
- **Fair**: 10-15 dB
- **Poor**: < 10 dB
- **Why**: Low background noise improves voice isolation

## Quality Labels

| Score Range | Label | Emoji | Recommendation |
|-------------|-------|-------|----------------|
| 0.80-1.00 | Excellent | ✅ | Ready for production use |
| 0.65-0.79 | Good | ✔️ | Should work well in most cases |
| 0.50-0.64 | Fair | ⚠️ | May work, but consider improving |
| 0.00-0.49 | Poor | ❌ | Re-record with better conditions |

## Usage

### During Enrollment

When creating a new profile, the system automatically:
1. Extracts speaker embedding
2. Assesses audio quality
3. Displays quality metrics
4. Provides recommendations
5. Stores quality data with profile

### Example Output

```
Quality Assessment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Overall Quality: Excellent
   Score: 0.87 / 1.00

Component Scores:
• Duration:     0.95  (45.2s - ideal range)
• Audio Level:  0.90  (good volume, no clipping)
• Embedding:    0.85  (well-formed)
• SNR:          0.80  (low background noise)

Recommendations:
✅ Excellent profile quality - ready for use!
```

### In Profile Management

Quality information is displayed for each saved profile:
- Quality emoji and label in profile list
- Overall score visible at a glance
- Detailed breakdown in profile details

## Recommendations Examples

### Good Quality
- ✅ Excellent profile quality - ready for use!

### Improvements Needed
- ⚠️ Audio too short - use 30-60 seconds for best results
- ⚠️ Audio level too low - speak louder or increase microphone gain
- ⚠️ Audio clipping detected - reduce microphone gain or speak softer
- ⚠️ Moderate background noise detected - use quieter environment
- ⚠️ High background noise - find a quieter environment
- 💡 Consider using 30-60 seconds of audio for optimal quality
- 💡 Audio level is low - consider speaking louder
- 💡 High embedding variance - background noise may be present

## Technical Details

### Calculation Method

```python
overall_score = (
    duration_score * 0.25 +
    audio_level_score * 0.25 +
    embedding_score * 0.30 +
    snr_score * 0.20
)
```

### Audio Analysis
- Uses librosa for audio processing
- Calculates RMS (Root Mean Square) for volume
- Estimates SNR using frame-based analysis
- Validates embedding normalization

### Embedding Validation
- Checks L2 norm (should be ~1.0 after normalization)
- Analyzes standard deviation (voice diversity)
- Validates shape and range

## Best Practices for High-Quality Profiles

### Recording Environment
1. **Quiet Room**: Minimize background noise (AC, traffic, people talking)
2. **Good Microphone**: Use quality microphone, not laptop built-in if possible
3. **Consistent Distance**: Keep 6-12 inches from microphone

### Recording Content
1. **Duration**: 30-60 seconds is ideal
2. **Natural Speech**: Speak naturally, as you would in meetings
3. **Varied Content**: Include different words/phrases (not just one sentence repeated)
4. **Clear Enunciation**: Speak clearly but naturally

### Audio Settings
1. **Good Volume**: Speak at normal volume, not whispering or shouting
2. **No Clipping**: Audio peaks should stay below 0.95
3. **Proper Gain**: Set microphone gain to avoid both too-quiet and too-loud
4. **Sample Rate**: 16kHz minimum (system will resample if needed)

## Testing

Run the test script to evaluate an existing audio file:

```bash
cd "/Users/robenhai/speaker diarization"
source venv/bin/activate
python tests/test_profile_quality.py
```

## Implementation Files

- `src/services/identification_service.py` - `assess_profile_quality()` method
- `src/services/profile_manager.py` - Stores quality data in profiles
- `src/ui/enrollment_tab.py` - Displays quality UI during enrollment

## Future Enhancements

Potential improvements:
- Real-time quality feedback during recording
- Comparative quality ranking of multiple profiles
- Audio preprocessing suggestions (noise reduction, normalization)
- Profile re-assessment after updates
- Quality trend tracking over time

---

**Created**: October 22, 2025  
**Version**: 1.0  
**Status**: Production Ready
