#!/usr/bin/env python3
"""
Installation verification script.
Checks if all required dependencies are properly installed.
"""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher required")
        return False
    
    print("✓ Python version OK")
    return True


def check_imports():
    """Check if all required packages can be imported."""
    packages = {
        'streamlit': 'Streamlit UI framework',
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'librosa': 'Librosa audio processing',
        'soundfile': 'SoundFile audio I/O',
        'pyaudio': 'PyAudio (microphone support)',
        'dotenv': 'python-dotenv',
        'pyannote.audio': 'pyannote.audio (speaker diarization)',
        'azure.cognitiveservices.speech': 'Azure Speech SDK'
    }
    
    print("\n📦 Checking package imports...")
    
    success = True
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✓ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            success = False
    
    return success


def check_pytorch_gpu():
    """Check PyTorch GPU availability."""
    try:
        import torch
        
        print("\n🔍 Checking GPU support...")
        
        if torch.backends.mps.is_available():
            print("✓ MPS (Apple Silicon GPU) available")
            print(f"  Device: {torch.device('mps')}")
            return True
        elif torch.cuda.is_available():
            print("✓ CUDA (NVIDIA GPU) available")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("ℹ️  No GPU available - will use CPU")
            print("  (Processing will be slower but functional)")
            return True
            
    except Exception as e:
        print(f"❌ Error checking GPU: {e}")
        return False


def check_config():
    """Check configuration files."""
    print("\n📋 Checking configuration...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found (template exists)")
            print("   Run: cp .env.example .env")
            print("   Then edit with your API keys")
        else:
            print("❌ .env.example template not found")
        return False
    
    print("✓ .env file exists")
    
    # Check if .env has required keys
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        required_keys = [
            'AZURE_SPEECH_KEY',
            'AZURE_REGION',
            'HUGGING_FACE_HUB_TOKEN'
        ]
        
        missing = []
        placeholder = []
        
        for key in required_keys:
            value = os.getenv(key)
            if not value:
                missing.append(key)
            elif 'your_' in value.lower() or 'here' in value.lower():
                placeholder.append(key)
        
        if missing:
            print(f"❌ Missing environment variables: {', '.join(missing)}")
            return False
        
        if placeholder:
            print(f"⚠️  Placeholder values detected: {', '.join(placeholder)}")
            print("   Please update .env with actual API keys")
            return False
        
        print("✓ All required environment variables set")
        return True
        
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False


def check_directories():
    """Check if required directories exist."""
    print("\n📁 Checking directories...")
    
    directories = [
        'data/profiles',
        'data/results',
        'data/temp',
        'logs'
    ]
    
    success = True
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✓ {directory}")
        else:
            print(f"❌ {directory} missing")
            success = False
    
    if not success:
        print("\n   Run: mkdir -p data/profiles data/results data/temp logs")
    
    return success


def check_audio_devices():
    """Check if audio devices are available."""
    print("\n🎤 Checking audio devices...")
    
    try:
        import pyaudio
        
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        
        if device_count == 0:
            print("⚠️  No audio devices found")
            return False
        
        print(f"✓ Found {device_count} audio device(s)")
        
        # List input devices
        input_devices = []
        for i in range(device_count):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append(info['name'])
        
        if input_devices:
            print(f"  Input devices: {len(input_devices)}")
            for device in input_devices[:3]:  # Show first 3
                print(f"    - {device}")
            if len(input_devices) > 3:
                print(f"    ... and {len(input_devices) - 3} more")
        else:
            print("⚠️  No input devices found (microphone required for live mode)")
        
        p.terminate()
        return True
        
    except Exception as e:
        print(f"❌ Error checking audio devices: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🎤 Speaker Diarization System - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Package Imports", check_imports),
        ("GPU Support", check_pytorch_gpu),
        ("Configuration", check_config),
        ("Directories", check_directories),
        ("Audio Devices", check_audio_devices)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Error running {name} check: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✓" if result else "❌"
        print(f"{status} {name}")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print("✅ All checks passed! System is ready to use.")
        print("\nTo start the application:")
        print("  streamlit run src/ui/app.py")
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed")
        print("\nPlease resolve the issues above before running the application.")
        print("See QUICK_START.md for troubleshooting help.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
