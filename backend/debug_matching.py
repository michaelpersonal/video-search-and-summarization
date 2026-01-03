#!/usr/bin/env python3

import os
import json
import numpy as np
import cv2
from ai_service import AIService, get_image_features_from_bytes, compute_image_similarity, deserialize_keypoints

def test_matching_with_specific_image():
    print("🔍 Testing matching algorithm with IMG_3701...")
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.is_model_available():
        print("❌ AI service not available")
        return
    
    print("✅ AI service initialized")
    
    # Test with IMG_3701 image
    test_image_path = "images/6/IMG_3701.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print(f"📸 Testing with: {test_image_path}")
    
    # Read image as bytes (simulating upload)
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    
    # Get features for uploaded image
    query_keypoints, query_descriptors = get_image_features_from_bytes(image_data)
    
    if query_keypoints is None or query_descriptors is None:
        print("❌ Could not extract features from uploaded image")
        return
    
    print(f"✅ Extracted {len(query_keypoints)} keypoints from uploaded image")
    
    # Test similarity with all stored images
    print("\n🔍 Testing similarity with all stored images:")
    print("-" * 60)
    
    similarities = []
    for i, stored_feature in enumerate(ai_service.stored_features):
        stored_keypoints = deserialize_keypoints(stored_feature['keypoints'])
        stored_descriptors = stored_feature['descriptors']
        
        similarity = compute_image_similarity(
            query_keypoints, query_descriptors,
            stored_keypoints, stored_descriptors
        )
        
        part_info = ai_service.mapping[i]
        similarities.append((similarity, part_info))
        
        print(f"{part_info['material_number']:>10}: {similarity:.4f} ({len(stored_keypoints)} keypoints)")
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    print("\n📊 Results sorted by similarity:")
    print("-" * 60)
    for i, (sim, part_info) in enumerate(similarities):
        print(f"{i+1:2d}. {part_info['material_number']:>10}: {sim:.4f}")
    
    # Test with different thresholds
    print("\n🎯 Testing different thresholds:")
    print("-" * 60)
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    
    for threshold in thresholds:
        matches = [sim for sim, _ in similarities if sim >= threshold]
        print(f"Threshold {threshold:.1f}: {len(matches)} matches")
        if matches:
            print(f"  Best match: {similarities[0][1]['material_number']} ({similarities[0][0]:.4f})")
    
    # Test the actual analyze_image function
    print("\n🧪 Testing analyze_image function:")
    print("-" * 60)
    
    # Create dummy spare parts data
    spare_parts_data = []
    for sim, part_info in similarities:
        spare_parts_data.append({
            "material_number": part_info["material_number"],
            "description": part_info["description"],
            "category": "Test",
            "manufacturer": "Test",
            "specifications": "Test",
            "image_path": part_info["image_path"]
        })
    
    # Analyze image
    matches = ai_service.analyze_image(image_data, spare_parts_data)
    
    print(f"📋 analyze_image returned {len(matches)} matches:")
    for i, match in enumerate(matches):
        print(f"  {i+1}. {match['material_number']}: {match['confidence_score']:.4f}")

if __name__ == "__main__":
    test_matching_with_specific_image() 