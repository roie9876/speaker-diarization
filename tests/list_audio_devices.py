#!/usr/bin/env python3
"""List audio devices and show default."""

import pyaudio

p = pyaudio.PyAudio()

print("Available Audio Input Devices:")
print("="*60)

default_device = p.get_default_input_device_info()['index']

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        is_default = " (DEFAULT)" if i == default_device else ""
        print(f"Device {i}{is_default}:")
        print(f"  Name: {info['name']}")
        print(f"  Channels: {info['maxInputChannels']}")
        print(f"  Sample Rate: {info['defaultSampleRate']} Hz")
        print()

print("="*60)
print(f"Default input device: {default_device}")

p.terminate()
