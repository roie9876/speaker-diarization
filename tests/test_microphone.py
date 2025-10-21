#!/usr/bin/env python3
"""
Test microphone capture to verify audio is being recorded correctly.
"""

import pyaudio
import numpy as np
import wave
import time
from pathlib import Path

def test_microphone():
    """Test microphone capture and save a recording."""
    
    print("🎤 Microphone Test")
    print("=" * 50)
    
    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    DURATION = 5  # seconds
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # List available devices
    print("\n📋 Available Audio Devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  [{i}] {info['name']} ({info['maxInputChannels']} channels)")
    
    # Get default input device
    default_device = p.get_default_input_device_info()
    device_index = default_device['index']
    device_name = default_device['name']
    
    print(f"\n✓ Using device [{device_index}]: {device_name}")
    print(f"\n🎙️  Recording for {DURATION} seconds...")
    print("   (Speak into your microphone now!)")
    
    # Open stream
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK_SIZE
    )
    
    frames = []
    levels = []
    
    # Record
    start_time = time.time()
    try:
        for i in range(0, int(SAMPLE_RATE / CHUNK_SIZE * DURATION)):
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frames.append(data)
            
            # Calculate level
            audio_data = np.frombuffer(data, dtype=np.float32)
            rms = np.sqrt(np.mean(audio_data**2))
            max_amp = np.max(np.abs(audio_data))
            levels.append((rms, max_amp))
            
            # Progress indicator
            elapsed = time.time() - start_time
            if int(elapsed) != int(elapsed - 0.1):
                print(f"   [{int(elapsed)}s] RMS: {rms:.4f}, Max: {max_amp:.4f}", end='\r')
        
        print()  # New line
        
    except KeyboardInterrupt:
        print("\n⚠️  Recording interrupted")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    print("\n✓ Recording complete!")
    
    # Analyze recording
    print("\n📊 Audio Analysis:")
    avg_rms = np.mean([level[0] for level in levels])
    max_rms = np.max([level[0] for level in levels])
    avg_max = np.mean([level[1] for level in levels])
    max_max = np.max([level[1] for level in levels])
    
    print(f"   Average RMS: {avg_rms:.4f}")
    print(f"   Peak RMS: {max_rms:.4f}")
    print(f"   Average Max: {avg_max:.4f}")
    print(f"   Peak Max: {max_max:.4f}")
    
    # Assessment
    print("\n🔍 Assessment:")
    if avg_rms < 0.001:
        print("   ❌ VERY QUIET - Check microphone connection/permissions")
    elif avg_rms < 0.01:
        print("   ⚠️  QUIET - Speak louder or increase input volume")
    elif avg_rms < 0.05:
        print("   ✓ NORMAL - Audio level is good")
    else:
        print("   ⚠️  LOUD - May be too loud (possible clipping)")
    
    # Save to file
    output_file = Path("data/temp/mic_test.wav")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to bytes
    audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)
    
    # Save as wav
    with wave.open(str(output_file), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        # Convert float32 to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())
    
    print(f"\n💾 Recording saved to: {output_file}")
    print("   Play it back to verify audio quality")
    print(f"\n   To play: afplay {output_file}")
    
    # Tips
    print("\n💡 Tips:")
    print("   - If RMS < 0.01, increase mic input level in System Preferences > Sound")
    print("   - Check microphone permissions for Terminal/Python")
    print("   - Try selecting a different microphone in Live Monitoring")


if __name__ == "__main__":
    try:
        test_microphone()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
