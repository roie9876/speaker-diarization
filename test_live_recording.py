#!/usr/bin/env python3
"""
Record a new test sample and compare with profile.
"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.services.identification_service import IdentificationService
from src.services.profile_manager import ProfileManager
import sounddevice as sd
import soundfile as sf
import tempfile

def record_and_test(profile_name: str, duration: int = 5):
    """Record audio and test against profile."""
    print(f"\n🎙️  Recording {duration} seconds of audio...")
    print("    Speak clearly now!")
    print()
    
    # Record
    sample_rate = 16000
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    print("✅ Recording complete!")
    
    # Save temporarily
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        temp_file = f.name
    
    sf.write(temp_file, audio, sample_rate)
    print(f"   Saved to: {temp_file}")
    
    # Load profile
    profile_mgr = ProfileManager()
    profiles = profile_mgr.list_profiles()
    profile = next((p for p in profiles if p['name'] == profile_name), None)
    
    if not profile:
        print(f"❌ Profile '{profile_name}' not found!")
        return
    
    profile_full = profile_mgr.load_profile(profile['id'])
    profile_emb = profile_full['embedding']
    
    # Extract embedding from recording
    ident = IdentificationService()
    test_emb = ident.extract_embedding(temp_file)
    
    # Compare
    similarity = ident.compare_embeddings(profile_emb, test_emb)
    
    print()
    print("="*60)
    print(f"📊 Comparison Results")
    print("="*60)
    print(f"Profile: {profile_name}")
    print(f"Profile embedding L2 norm: {np.linalg.norm(profile_emb):.6f}")
    print(f"Test embedding L2 norm: {np.linalg.norm(test_emb):.6f}")
    print(f"Test embedding range: [{test_emb.min():.3f}, {test_emb.max():.3f}]")
    print()
    print(f"🎯 Similarity Score: {similarity:.4f}")
    print()
    
    if similarity >= 0.75:
        print("✅ STRONG MATCH - You are recognized!")
    elif similarity >= 0.65:
        print("⚠️  MODERATE MATCH - Close but needs improvement")
        print("   Try: Lower threshold to 0.65 or recreate profile")
    elif similarity >= 0.50:
        print("❌ WEAK MATCH - Poor recognition")
        print("   Try: Recreate profile in same conditions")
    else:
        print("❌ NO MATCH - Different speaker or major issue")
        print("   This suggests:")
        print("   - Different person speaking")
        print("   - Major audio quality difference")
        print("   - Wrong microphone/device")
    
    print("="*60)
    
    return temp_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_live_recording.py <profile_name> [duration]")
        print("Example: python test_live_recording.py roie-ben-haim 5")
        sys.exit(1)
    
    profile_name = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    record_and_test(profile_name, duration)
