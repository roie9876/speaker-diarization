#!/usr/bin/env python3
"""Test if profile matches its own enrollment audio."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.profile_manager import ProfileManager
from src.services.identification_service import IdentificationService
from src.utils.audio_utils import load_audio
import numpy as np

def test_profile_self_match():
    """Test if profile embedding matches its enrollment audio."""
    
    print("🧪 PROFILE SELF-MATCH TEST")
    print("="*60)
    
    # Load profile
    pm = ProfileManager()
    profiles = pm.list_profiles()
    
    if not profiles:
        print("❌ No profiles found!")
        return
    
    profile = pm.load_profile(profiles[0]['id'])
    print(f"\n📋 Testing profile: {profile['name']}")
    print(f"   ID: {profile['id']}")
    print(f"   Created: {profile.get('created_date', 'Unknown')}")
    
    # Get profile embedding
    profile_embedding = profile['embedding']
    print(f"   Embedding shape: {profile_embedding.shape}")
    print(f"   Embedding norm: {np.linalg.norm(profile_embedding):.6f}")
    
    # Check if we have enrollment audio in temp
    metadata = profile.get('metadata', {})
    audio_file = metadata.get('audio_file')
    
    if not audio_file:
        print("\n⚠️  No audio file info in profile metadata")
        print("   Cannot test self-match without enrollment audio")
        return
    
    print(f"\n🎤 Looking for enrollment audio: {audio_file}")
    
    # Try to find the audio file
    data_dir = Path("data")
    possible_locations = [
        data_dir / "temp" / audio_file,
        data_dir / audio_file,
        Path(audio_file)
    ]
    
    audio_path = None
    for loc in possible_locations:
        if loc.exists():
            audio_path = loc
            break
    
    if not audio_path:
        print(f"❌ Enrollment audio not found")
        print(f"   Tried: {possible_locations}")
        print("\n💡 SOLUTION: Create new profile and test immediately")
        return
    
    print(f"✅ Found audio: {audio_path}")
    
    # Extract embedding from audio
    print(f"\n🔍 Extracting embedding from enrollment audio...")
    identification = IdentificationService()
    test_embedding = identification.extract_embedding(audio_path)
    
    print(f"   Test embedding shape: {test_embedding.shape}")
    print(f"   Test embedding norm: {np.linalg.norm(test_embedding):.6f}")
    
    # Calculate similarity
    print(f"\n🎯 Calculating similarity...")
    similarity = identification.compare_embeddings(profile_embedding, test_embedding)
    
    print(f"\n{'='*60}")
    print(f"📊 RESULT:")
    print(f"   Similarity: {similarity:.4f}")
    
    if similarity >= 0.90:
        print(f"   ✅ EXCELLENT - Profile matches perfectly!")
    elif similarity >= 0.80:
        print(f"   ✅ GOOD - Profile matches well")
    elif similarity >= 0.70:
        print(f"   ⚠️  FAIR - Profile matches but not strongly")
    else:
        print(f"   ❌ POOR - Profile does NOT match!")
        print(f"      This indicates profile corruption or bug")
    
    print(f"{'='*60}")
    
    # Additional diagnostic
    print(f"\n🔬 DIAGNOSTIC INFO:")
    print(f"   Profile embedding:")
    print(f"     Mean: {profile_embedding.mean():.6f}")
    print(f"     Std:  {profile_embedding.std():.6f}")
    print(f"     Range: [{profile_embedding.min():.4f}, {profile_embedding.max():.4f}]")
    print(f"\n   Test embedding:")
    print(f"     Mean: {test_embedding.mean():.6f}")
    print(f"     Std:  {test_embedding.std():.6f}")
    print(f"     Range: [{test_embedding.min():.4f}, {test_embedding.max():.4f}]")
    
    # Cosine distance
    dot_product = np.dot(profile_embedding, test_embedding)
    print(f"\n   Dot product: {dot_product:.6f}")
    print(f"   Cosine similarity: {similarity:.6f}")
    print(f"   Cosine distance: {1 - similarity:.6f}")

if __name__ == "__main__":
    test_profile_self_match()
