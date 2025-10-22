"""Quick test to verify JSON serialization of quality assessment."""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.identification_service import IdentificationService

def test_json_serialization():
    """Test that quality assessment results can be JSON serialized."""
    
    # Find test audio
    data_dir = Path(__file__).parent.parent / "data"
    audio_files = list(data_dir.rglob("*.wav"))
    
    if not audio_files:
        print("❌ No audio files found")
        return False
    
    audio_file = audio_files[0]
    print(f"Testing with: {audio_file.name}")
    
    # Initialize service
    identification = IdentificationService()
    
    # Extract embedding
    embedding = identification.extract_embedding(audio_file)
    
    # Assess quality
    quality = identification.assess_profile_quality(
        audio_file=audio_file,
        embedding=embedding
    )
    
    # Try to serialize to JSON
    try:
        json_str = json.dumps(quality, indent=2)
        print("\n✅ JSON serialization successful!")
        print(f"\nJSON output (first 300 chars):\n{json_str[:300]}...")
        
        # Try to parse it back
        parsed = json.loads(json_str)
        print("\n✅ JSON deserialization successful!")
        print(f"Overall score: {parsed['overall_score']}")
        print(f"Quality label: {parsed['quality_label']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ JSON serialization failed: {e}")
        print(f"Quality result type: {type(quality)}")
        print(f"Details types: {[(k, type(v)) for k, v in quality.get('details', {}).items()]}")
        return False

if __name__ == "__main__":
    success = test_json_serialization()
    sys.exit(0 if success else 1)
