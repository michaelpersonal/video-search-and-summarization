#!/usr/bin/env python3

import os
import json
import numpy as np
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from ai_service import AIService, get_clip_features_from_bytes

def test_threshold_no_match():
    """Test the 95% threshold when no match exceeds it"""
    print("🧪 Testing 95% threshold when no match exceeds it...")
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.is_model_available():
        print("❌ AI service not available")
        return
    
    print("✅ AI service initialized")
    
    # Test with a completely different image that should not match any stored images above 95%
    # Let's use IMG_3703 and see if it matches with IMG_3701 (should be below 95%)
    test_image_path = "images/4/IMG_3703.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print(f"📸 Testing with: {test_image_path}")
    
    # Read image as bytes (simulating camera upload)
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    
    # Get CLIP features for uploaded image
    query_features = get_clip_features_from_bytes(image_data)
    
    if query_features is None:
        print("❌ Could not extract CLIP features from uploaded image")
        return
    
    print(f"✅ Extracted CLIP features from uploaded image")
    
    # Test similarity with all stored images
    print("\n🔍 Testing semantic similarity with all stored images:")
    print("-" * 80)
    
    similarities = []
    for i, stored_feature in enumerate(ai_service.stored_features):
        stored_features = torch.tensor(stored_feature['clip_features'], dtype=torch.float32)
        
        # Compute similarity
        similarity = F.cosine_similarity(query_features, stored_features, dim=1)
        normalized_similarity = (similarity + 1) / 2
        
        part_info = ai_service.mapping[i]
        similarities.append((normalized_similarity.item(), part_info))
        
        print(f"{part_info['material_number']:>10}: {normalized_similarity.item():.4f}")
        print(f"   Cosine similarity: {similarity.item():.4f}")
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    print("\n📊 Results sorted by similarity:")
    print("-" * 80)
    for i, (sim, part_info) in enumerate(similarities):
        print(f"{i+1:2d}. {part_info['material_number']:>10}: {sim:.4f}")
    
    # Test the new 95% threshold
    print(f"\n🎯 Testing new 95% threshold:")
    print("-" * 80)
    
    threshold_95 = 0.95
    matches_95 = [sim for sim, _ in similarities if sim >= threshold_95]
    
    print(f"Threshold {threshold_95:.2f}: {len(matches_95)} matches")
    if matches_95:
        print(f"  Best match: {similarities[0][1]['material_number']} ({similarities[0][0]:.4f})")
        print("✅ Found matches above 95% threshold")
    else:
        print("❌ No matches found above 95% threshold")
        print("✅ This is the expected behavior - only very high confidence matches should pass")
    
    # Test the actual analyze_image method
    print(f"\n🧪 Testing analyze_image method with new threshold:")
    print("-" * 80)
    
    # Create dummy spare parts data
    spare_parts_data = [
        {"material_number": "IMG_3701", "description": "Test part 1"},
        {"material_number": "IMG_3702", "description": "Test part 2"},
        {"material_number": "IMG_3703", "description": "Test part 3"},
    ]
    
    results = ai_service.analyze_image(image_data, spare_parts_data)
    
    print(f"Results from analyze_image: {len(results)} matches")
    if results:
        for result in results:
            print(f"  {result['material_number']}: {result['confidence_score']:.4f}")
    else:
        print("  No matches returned - this should trigger fallback analysis")

if __name__ == "__main__":
    test_threshold_no_match() 