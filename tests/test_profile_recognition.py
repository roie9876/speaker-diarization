#!/usr/bin/env python3
"""
Quick test script to check if your profile can be recognized.
"""

import sys
from pathlib import Path
from src.services.profile_manager import ProfileManager
from src.services.identification_service import IdentificationService
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_profile_recognition(audio_file: str, profile_name: str):
    """Test if a profile can be recognized from an audio file."""
    
    audio_path = Path(audio_file)
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    print(f"🎤 Testing profile recognition...")
    print(f"   Audio file: {audio_file}")
    print(f"   Profile: {profile_name}")
    print()
    
    # Load services
    print("Loading services...")
    profile_mgr = ProfileManager()
    identification = IdentificationService()
    
    # Find profile
    profiles = profile_mgr.list_profiles()
    profile = None
    for p in profiles:
        if p['name'].lower() == profile_name.lower():
            profile = profile_mgr.load_profile(p['id'])
            break
    
    if not profile:
        print(f"❌ Profile '{profile_name}' not found")
        print(f"Available profiles: {', '.join(p['name'] for p in profiles)}")
        return
    
    print(f"✓ Found profile: {profile['name']} (ID: {profile['id'][:8]}...)")
    
    # Extract embedding from audio
    print(f"\n📊 Extracting embedding from audio...")
    try:
        audio_embedding = identification.extract_embedding(audio_path)
        print(f"✓ Extracted embedding (shape: {audio_embedding.shape})")
    except Exception as e:
        print(f"❌ Failed to extract embedding: {e}")
        return
    
    # Compare embeddings
    print(f"\n🔍 Comparing embeddings...")
    profile_embedding = profile['embedding']
    similarity = identification.compare_embeddings(profile_embedding, audio_embedding)
    
    print(f"\n{'='*50}")
    print(f"📈 SIMILARITY SCORE: {similarity:.4f}")
    print(f"{'='*50}")
    
    # Interpretation
    if similarity >= 0.85:
        print("✅ EXCELLENT match! (≥0.85)")
    elif similarity >= 0.75:
        print("✓ GOOD match (0.75-0.85) - should work")
    elif similarity >= 0.65:
        print("⚠️  MODERATE match (0.65-0.75) - might work with lower threshold")
    else:
        print("❌ POOR match (<0.65) - likely different speaker or audio quality issue")
    
    print(f"\n💡 Tips:")
    print(f"   - For best results, use the same microphone for profile and testing")
    print(f"   - Ensure audio is clear and without background noise")
    print(f"   - Longer audio samples (>5s) generally work better")
    print(f"   - Try adjusting threshold slider in UI (currently 0.75)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_profile_recognition.py <audio_file> <profile_name>")
        print("\nExample:")
        print("  python test_profile_recognition.py my_voice.wav roie1")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    profile_name = sys.argv[2]
    
    test_profile_recognition(audio_file, profile_name)
