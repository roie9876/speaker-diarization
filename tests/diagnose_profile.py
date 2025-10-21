#!/usr/bin/env python3
"""
Diagnostic tool to analyze speaker profile and test audio matching.
"""

import json
import sys
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.identification_service import IdentificationService
from src.utils.logger import get_logger

logger = get_logger(__name__)


def analyze_profile(profile_id_or_name: str):
    """Analyze a speaker profile."""
    profile_dir = project_root / "data" / "profiles"
    
    # Find profile
    profile_path = None
    for p in profile_dir.glob("*.json"):
        data = json.load(open(p))
        if data['id'] == profile_id_or_name or data['name'] == profile_id_or_name:
            profile_path = p
            break
    
    if not profile_path:
        print(f"❌ Profile not found: {profile_id_or_name}")
        return
    
    # Load profile
    with open(profile_path) as f:
        profile = json.load(f)
    
    embedding = np.array(profile['embedding'])
    
    print("\n" + "="*60)
    print(f"📊 Profile Analysis: {profile['name']}")
    print("="*60)
    print(f"ID: {profile['id']}")
    print(f"Created: {profile.get('created_date', 'Unknown')}")
    print(f"Duration: {profile.get('metadata', {}).get('audio_duration', 'Unknown')}s")
    print(f"\nEmbedding Shape: {embedding.shape}")
    print(f"Embedding Dimension: {embedding.ndim}D")
    print(f"Value Range: [{embedding.min():.3f}, {embedding.max():.3f}]")
    print(f"Mean: {embedding.mean():.3f}")
    print(f"Std Dev: {embedding.std():.3f}")
    print(f"L2 Norm: {np.linalg.norm(embedding):.3f}")
    
    # Check if normalized
    norm = np.linalg.norm(embedding)
    if abs(norm - 1.0) < 0.01:
        print("✅ Embedding is normalized (L2 norm ≈ 1.0)")
    else:
        print(f"⚠️  Embedding is NOT normalized (L2 norm = {norm:.3f}, should be 1.0)")
    
    print("\n" + "="*60)


def test_live_audio(profile_name: str, num_chunks: int = 5):
    """Test the most recent live audio chunks against profile."""
    profile_dir = project_root / "data" / "profiles"
    temp_dir = project_root / "data" / "temp"
    
    # Find profile
    profile_path = None
    for p in profile_dir.glob("*.json"):
        data = json.load(open(p))
        if data['name'] == profile_name:
            profile_path = p
            break
    
    if not profile_path:
        print(f"❌ Profile not found: {profile_name}")
        return
    
    # Load profile
    with open(profile_path) as f:
        profile = json.load(f)
    
    profile_embedding = np.array(profile['embedding'])
    
    # Find recent audio chunks
    chunks = sorted(temp_dir.glob("realtime_chunk_*.wav"), key=lambda x: x.stat().st_mtime, reverse=True)[:num_chunks]
    
    if not chunks:
        print("❌ No live audio chunks found in data/temp/")
        print("   Start live monitoring first to generate chunks")
        return
    
    print("\n" + "="*60)
    print(f"🎤 Testing Recent Live Audio vs Profile: {profile_name}")
    print("="*60)
    
    # Initialize identification service
    identification = IdentificationService()
    
    scores = []
    for i, chunk in enumerate(chunks, 1):
        print(f"\n🔊 Chunk {i}: {chunk.name}")
        try:
            # Extract embedding
            chunk_embedding = identification.extract_embedding(chunk)
            
            # Compare
            similarity = identification.compare_embeddings(profile_embedding, chunk_embedding)
            scores.append(similarity)
            
            if similarity >= 0.75:
                status = "✅ MATCH"
            elif similarity >= 0.65:
                status = "⚠️  CLOSE"
            else:
                status = "❌ NO MATCH"
            
            print(f"   Similarity: {similarity:.4f} {status}")
            print(f"   Chunk embedding range: [{chunk_embedding.min():.3f}, {chunk_embedding.max():.3f}]")
            print(f"   Chunk L2 norm: {np.linalg.norm(chunk_embedding):.3f}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if scores:
        print("\n" + "="*60)
        print("📈 Summary Statistics:")
        print("="*60)
        print(f"Average Similarity: {np.mean(scores):.4f}")
        print(f"Max Similarity: {np.max(scores):.4f}")
        print(f"Min Similarity: {np.min(scores):.4f}")
        print(f"Std Dev: {np.std(scores):.4f}")
        
        print("\n💡 Recommendations:")
        avg_score = np.mean(scores)
        if avg_score >= 0.75:
            print("✅ Good match! System should recognize you.")
        elif avg_score >= 0.65:
            print("⚠️  Moderate match. Try:")
            print("   - Lower threshold to 0.65")
            print("   - Recreate profile speaking more clearly")
        elif avg_score >= 0.50:
            print("❌ Poor match. Likely issues:")
            print("   - Different voice/speaker")
            print("   - Very different recording conditions")
            print("   - Microphone quality differences")
            print("   → Recreate profile with same microphone and conditions")
        else:
            print("❌ Very poor match. This might be:")
            print("   - A completely different person")
            print("   - Wrong profile loaded")
            print("   - Major audio quality difference")
            print("   → Start fresh: delete profile and recreate")
        
        print("\n" + "="*60)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python diagnose_profile.py <profile_name>              # Analyze profile")
        print("  python diagnose_profile.py <profile_name> test         # Test against live audio")
        print("\nExample:")
        print("  python diagnose_profile.py roie-ben-haim")
        print("  python diagnose_profile.py roie-ben-haim test")
        sys.exit(1)
    
    profile_name = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "test":
        test_live_audio(profile_name)
    else:
        analyze_profile(profile_name)


if __name__ == "__main__":
    main()
