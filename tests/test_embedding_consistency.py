#!/usr/bin/env python3
"""
Test if embedding extraction is consistent for same audio at different lengths.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.identification_service import IdentificationService
from src.services.profile_manager import ProfileManager
import numpy as np

def main():
    print("\n" + "="*60)
    print("🔬 Testing Embedding Consistency")
    print("="*60)
    
    # Load the profile
    pm = ProfileManager()
    profiles = pm.list_profiles()
    
    if not profiles:
        print("❌ No profiles found. Create one first.")
        return
    
    profile = pm.load_profile(profiles[0]['id'])
    print(f"\n📊 Profile: {profile['name']}")
    print(f"   Duration: {profile.get('metadata', {}).get('audio_duration', 'unknown')}s")
    print(f"   Embedding L2 norm: {np.linalg.norm(profile['embedding']):.6f}")
    print(f"   Embedding range: [{profile['embedding'].min():.3f}, {profile['embedding'].max():.3f}]")
    
    # Load recent live audio chunks
    temp_dir = Path("/Users/robenhai/speaker diarization/data/temp")
    chunks = sorted(temp_dir.glob("realtime_chunk_*.wav"), 
                   key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    
    if not chunks:
        print("\n❌ No live audio chunks found.")
        return
    
    # Test each chunk
    ident = IdentificationService()
    
    print("\n" + "="*60)
    print("🎤 Testing Recent Live Audio Chunks")
    print("="*60)
    
    similarities = []
    for i, chunk in enumerate(chunks, 1):
        print(f"\n📝 Chunk {i}: {chunk.name[-40:]}")
        
        # Extract embedding from entire chunk
        chunk_emb = ident.extract_embedding(chunk)
        
        # Compare with profile
        similarity = ident.compare_embeddings(profile['embedding'], chunk_emb)
        similarities.append(similarity)
        
        print(f"   Embedding L2 norm: {np.linalg.norm(chunk_emb):.6f}")
        print(f"   Embedding range: [{chunk_emb.min():.3f}, {chunk_emb.max():.3f}]")
        print(f"   Similarity: {similarity:.4f}", end="")
        
        if similarity >= 0.75:
            print(" ✅ MATCH")
        elif similarity >= 0.65:
            print(" ⚠️  CLOSE")
        elif similarity >= 0.50:
            print(" 🔶 MODERATE")
        else:
            print(" ❌ LOW")
    
    if similarities:
        print("\n" + "="*60)
        print("📈 Statistics")
        print("="*60)
        print(f"Average Similarity: {np.mean(similarities):.4f}")
        print(f"Std Dev: {np.std(similarities):.4f}")
        print(f"Min: {np.min(similarities):.4f}")
        print(f"Max: {np.max(similarities):.4f}")
        
        print("\n" + "="*60)
        print("💡 Recommendations")
        print("="*60)
        
        avg = np.mean(similarities)
        if avg >= 0.75:
            print("✅ Excellent! Keep threshold at 0.75")
        elif avg >= 0.65:
            print("⚠️  Good but not great. Try:")
            print(f"   → Lower threshold to {max(0.60, avg - 0.05):.2f}")
            print("   → Or recreate profile speaking MORE clearly/loudly")
        elif avg >= 0.50:
            print("🔶 Moderate match. Issues:")
            print("   → Embeddings are somewhat different")
            print("   → Try threshold of 0.55-0.60")
            print("   → Consider: speaking style, volume, clarity")
        else:
            print("❌ Poor match. This suggests:")
            print("   → Different speaker (most likely)")
            print("   → OR embeddings not working correctly")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
