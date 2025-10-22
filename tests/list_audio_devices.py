#!/usr/bin/env python3
"""List available audio input devices."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import pyaudio
    
    print("🎤 AVAILABLE AUDIO INPUT DEVICES")
    print("="*70)
    
    p = pyaudio.PyAudio()
    
    default_device = p.get_default_input_device_info()
    print(f"\n⭐ DEFAULT DEVICE:")
    print(f"   Index: {default_device['index']}")
    print(f"   Name: {default_device['name']}")
    print(f"   Channels: {default_device['maxInputChannels']}")
    print(f"   Sample Rate: {int(default_device['defaultSampleRate'])} Hz")
    
    print(f"\n📋 ALL INPUT DEVICES:")
    print(f"{'='*70}")
    
    input_devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        if info.get('maxInputChannels', 0) > 0:
            input_devices.append(info)
            
            is_default = "(DEFAULT)" if i == default_device['index'] else ""
            print(f"\n[{i}] {info['name']} {is_default}")
            print(f"    Channels: {info['maxInputChannels']}")
            print(f"    Sample Rate: {int(info['defaultSampleRate'])} Hz")
            print(f"    Host API: {p.get_host_api_info_by_index(info['hostApi'])['name']}")
    
    print(f"\n{'='*70}")
    print(f"Total input devices: {len(input_devices)}")
    
    p.terminate()
    
    print(f"\n💡 TIP:")
    print(f"   When using Live Monitoring, make sure to select the SAME device")
    print(f"   that you used when creating the profile!")
    print(f"\n   If profile was created with built-in mic, use built-in mic for live.")
    print(f"   If profile was created with external mic, use external mic for live.")
    
except ImportError:
    print("❌ pyaudio not installed")
    print("   Install with: pip install pyaudio")
