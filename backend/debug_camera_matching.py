#!/usr/bin/env python3

import os
import json
import numpy as np
import cv2
from ai_service import AIService, get_image_features_from_bytes, compute_image_similarity_detailed, deserialize_keypoints

def debug_camera_matching():
    """Debug why camera images are not matching well with stored images"""
    print("🔍 Debugging camera image matching...")
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.is_model_available():
        print("❌ AI service not available")
        return
    
    print("✅ AI service initialized")
    
    # Test with a stored image as if it were a camera upload
    test_image_path = "images/6/IMG_3701.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print(f"📸 Testing with: {test_image_path}")
    
    # Read image as bytes (simulating camera upload)
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
    print("-" * 80)
    
    similarities = []
    for i, stored_feature in enumerate(ai_service.stored_features):
        stored_keypoints = deserialize_keypoints(stored_feature['keypoints'])
        stored_descriptors = stored_feature['descriptors']
        
        similarity, details = compute_image_similarity_detailed(
            query_keypoints, query_descriptors,
            stored_keypoints, stored_descriptors
        )
        
        part_info = ai_service.mapping[i]
        similarities.append((similarity, part_info, details))
        
        print(f"{part_info['material_number']:>10}: {similarity:.4f}")
        print(f"   Keypoints: {len(query_keypoints)} vs {len(stored_keypoints)}")
        print(f"   Good matches: {details['good_matches']} / {details['total_matches']}")
        print(f"   Match ratio: {details['match_ratio']:.4f}")
        print(f"   Absolute score: {details['absolute_score']:.4f}")
        print(f"   Relative score: {details['relative_score']:.4f}")
        print()
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    print("📊 Results sorted by similarity:")
    print("-" * 80)
    for i, (sim, part_info, details) in enumerate(similarities):
        print(f"{i+1:2d}. {part_info['material_number']:>10}: {sim:.4f}")
    
    # Analyze the best match in detail
    if similarities:
        best_sim, best_part, best_details = similarities[0]
        print(f"\n🔍 Detailed analysis of best match ({best_part['material_number']}):")
        print("-" * 80)
        print(f"Similarity score: {best_sim:.4f}")
        print(f"Match ratio: {best_details['match_ratio']:.4f}")
        print(f"Good matches: {best_details['good_matches']} out of {best_details['total_matches']}")
        print(f"Query keypoints: {best_details['query_keypoints']}")
        print(f"Stored keypoints: {best_details['stored_keypoints']}")
        print(f"Absolute score: {best_details['absolute_score']:.4f}")
        print(f"Relative score: {best_details['relative_score']:.4f}")
        
        # Check if this should be considered a match
        if best_sim > 0.9:
            print("✅ This should be considered a perfect match!")
        elif best_sim > 0.7:
            print("✅ This should be considered a good match!")
        elif best_sim > 0.5:
            print("⚠️ This should be considered a moderate match!")
        else:
            print("❌ This should not be considered a match!")
    
    # Test with different similarity calculation methods
    print(f"\n🧪 Testing different similarity calculation methods:")
    print("-" * 80)
    
    if similarities:
        best_sim, best_part, best_details = similarities[0]
        
        # Method 1: Current method
        print(f"Method 1 (Current): {best_sim:.4f}")
        
        # Method 2: Simple match ratio
        simple_ratio = best_details['match_ratio']
        print(f"Method 2 (Simple ratio): {simple_ratio:.4f}")
        
        # Method 3: Absolute score only
        absolute_only = best_details['absolute_score']
        print(f"Method 3 (Absolute only): {absolute_only:.4f}")
        
        # Method 4: Relative score only
        relative_only = best_details['relative_score']
        print(f"Method 4 (Relative only): {relative_only:.4f}")
        
        # Method 5: Different sigmoid parameters
        combined_score = 0.7 * absolute_only + 0.3 * relative_only
        sigmoid_1 = 1 / (1 + np.exp(-10 * (combined_score - 0.1)))
        sigmoid_2 = 1 / (1 + np.exp(-5 * (combined_score - 0.05)))
        print(f"Method 5 (Sigmoid 1): {sigmoid_1:.4f}")
        print(f"Method 6 (Sigmoid 2): {sigmoid_2:.4f}")

if __name__ == "__main__":
    debug_camera_matching() 