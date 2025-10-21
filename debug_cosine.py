#!/usr/bin/env python3
"""
Debug embedding comparison - raw numpy check.
"""

import json
import numpy as np
from pathlib import Path
from scipy.spatial.distance import cosine

# Load profile
profile_path = Path("/Users/robenhai/speaker diarization/data/profiles/8fff5552-05c6-4c07-9809-a1dace1c92b4.json")
with open(profile_path) as f:
    profile = json.load(f)

profile_emb = np.array(profile['embedding'])

print("Profile Embedding:")
print(f"  Shape: {profile_emb.shape}")
print(f"  Type: {profile_emb.dtype}")
print(f"  Range: [{profile_emb.min():.6f}, {profile_emb.max():.6f}]")
print(f"  L2 Norm: {np.linalg.norm(profile_emb):.6f}")
print(f"  First 10 values: {profile_emb[:10]}")
print()

# Test self-similarity
self_dist = cosine(profile_emb, profile_emb)
self_sim = 1 - self_dist
print(f"Profile vs itself:")
print(f"  Cosine distance: {self_dist:.6f}")
print(f"  Similarity: {self_sim:.6f}")
print(f"  Expected: 1.000000")
print()

# Create a test embedding (random but normalized)
test_emb = np.random.randn(512)
test_emb = test_emb / np.linalg.norm(test_emb)

test_dist = cosine(profile_emb, test_emb)
test_sim = 1 - test_dist
print(f"Profile vs random normalized vector:")
print(f"  Test embedding L2 norm: {np.linalg.norm(test_emb):.6f}")
print(f"  Cosine distance: {test_dist:.6f}")
print(f"  Similarity: {test_sim:.6f}")
print(f"  Expected: ~0.0 (random)")
