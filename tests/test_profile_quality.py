"""
Test script for profile quality assessment.

Run this to test the quality assessment feature with an existing audio file.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.identification_service import IdentificationService
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_quality_assessment():
    """Test quality assessment on an audio file."""
    
    # Find an example audio file
    data_dir = Path(__file__).parent.parent / "data"
    
    # Try to find any WAV files
    audio_files = list(data_dir.rglob("*.wav"))
    
    if not audio_files:
        print("❌ No audio files found in data/ directory")
        print("Please add a test audio file to test quality assessment")
        return
    
    audio_file = audio_files[0]
    print(f"\n📁 Testing with: {audio_file.name}")
    print(f"   Path: {audio_file}")
    
    # Initialize service
    print("\n🔧 Initializing identification service...")
    identification = IdentificationService()
    
    # Extract embedding
    print("\n🔍 Extracting embedding...")
    try:
        embedding = identification.extract_embedding(audio_file)
        print(f"✅ Embedding extracted: shape={embedding.shape}")
    except Exception as e:
        print(f"❌ Failed to extract embedding: {e}")
        return
    
    # Assess quality
    print("\n📊 Assessing profile quality...")
    try:
        quality = identification.assess_profile_quality(
            audio_file=audio_file,
            embedding=embedding
        )
        
        # Display results
        print("\n" + "="*60)
        print("QUALITY ASSESSMENT RESULTS")
        print("="*60)
        
        print(f"\n{quality['quality_emoji']} Overall Quality: {quality['quality_label']}")
        print(f"   Score: {quality['overall_score']:.3f} / 1.000")
        
        print(f"\n📏 Component Scores:")
        print(f"   • Duration:     {quality['duration_score']:.3f}")
        print(f"   • Audio Level:  {quality['audio_level_score']:.3f}")
        print(f"   • Embedding:    {quality['embedding_score']:.3f}")
        print(f"   • SNR:          {quality['snr_score']:.3f}")
        
        print(f"\n📋 Detailed Metrics:")
        details = quality['details']
        print(f"   • Duration:       {details.get('duration_seconds', 'N/A')}s")
        print(f"   • RMS Level:      {details.get('rms_level', 'N/A')}")
        print(f"   • Peak Level:     {details.get('peak_level', 'N/A')}")
        print(f"   • SNR Estimate:   {details.get('snr_estimate_db', 'N/A')} dB")
        print(f"   • Embedding Norm: {details.get('embedding_norm', 'N/A')}")
        print(f"   • Embedding Std:  {details.get('embedding_std', 'N/A')}")
        
        if quality['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in quality['recommendations']:
                print(f"   {rec}")
        
        print("\n" + "="*60)
        
        # Quality interpretation
        print("\n📖 Quality Interpretation:")
        score = quality['overall_score']
        if score >= 0.8:
            print("   ✅ Excellent - Profile is ready for production use")
        elif score >= 0.65:
            print("   ✔️  Good - Profile should work well in most cases")
        elif score >= 0.5:
            print("   ⚠️  Fair - Profile may work, but consider improving")
        else:
            print("   ❌ Poor - Recommend re-recording with better conditions")
        
        print("\n✅ Quality assessment test completed!\n")
        
    except Exception as e:
        print(f"❌ Quality assessment failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PROFILE QUALITY ASSESSMENT TEST")
    print("="*60)
    
    test_quality_assessment()
