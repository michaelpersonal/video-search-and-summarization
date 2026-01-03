#!/usr/bin/env python3

import os
import cv2
import numpy as np
from ai_service import get_image_features_from_bytes
import json

def test_filtered_features():
    """Test the new feature filtering for camera images"""
    print("🧪 Testing filtered feature extraction...")
    
    # Test with one of the stored images
    test_image_path = "images/6/IMG_3701.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print(f"📸 Testing with: {test_image_path}")
    
    # Read image as bytes (simulating camera upload)
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    
    # Get features with new filtering
    keypoints, descriptors = get_image_features_from_bytes(image_data)
    
    if keypoints is None or descriptors is None:
        print("❌ Failed to extract features")
        return
    
    print(f"✅ Extracted {len(keypoints)} keypoints after filtering")
    print(f"📊 Descriptors shape: {descriptors.shape}")
    
    # Analyze keypoint quality
    responses = [kp.response for kp in keypoints]
    print(f"📈 Keypoint response statistics:")
    print(f"   Min response: {min(responses):.3f}")
    print(f"   Max response: {max(responses):.3f}")
    print(f"   Mean response: {np.mean(responses):.3f}")
    print(f"   Std response: {np.std(responses):.3f}")
    
    # Test similarity with stored features
    print(f"\n🔍 Testing similarity with stored features...")
    
    # Load stored features
    EMBEDDINGS_FILE = "part_image_embeddings.npy"
    MAPPING_FILE = "part_image_embeddings_map.json"
    
    try:
        features_data = np.load(EMBEDDINGS_FILE, allow_pickle=True)
        with open(MAPPING_FILE, 'r') as f:
            mapping = json.load(f)
        print(f"✅ Loaded {len(features_data)} stored feature sets")
    except Exception as e:
        print(f"❌ Error loading stored features: {e}")
        return
    
    # Initialize FLANN matcher
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    # Test similarity with each stored image
    for i, stored_feature in enumerate(features_data):
        stored_keypoints = []
        for kp_dict in stored_feature['keypoints']:
            kp = cv2.KeyPoint(
                x=kp_dict['pt'][0],
                y=kp_dict['pt'][1],
                size=kp_dict['size'],
                angle=kp_dict['angle'],
                response=kp_dict['response'],
                octave=kp_dict['octave'],
                class_id=kp_dict['class_id']
            )
            stored_keypoints.append(kp)
        
        stored_descriptors = stored_feature['descriptors']
        
        # Match features
        matches = flann.knnMatch(descriptors, stored_descriptors, k=2)
        
        # Apply strict Lowe's ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
        
        # Calculate similarity
        min_keypoints = min(len(keypoints), len(stored_keypoints))
        match_ratio = len(good_matches) / min_keypoints if min_keypoints > 0 else 0
        
        smaller_keypoints = min(len(keypoints), len(stored_keypoints))
        larger_keypoints = max(len(keypoints), len(stored_keypoints))
        
        absolute_score = len(good_matches) / smaller_keypoints if smaller_keypoints > 0 else 0
        relative_score = len(good_matches) / larger_keypoints if larger_keypoints > 0 else 0
        
        similarity = 0.7 * absolute_score + 0.3 * relative_score
        similarity = 1 / (1 + np.exp(-8 * (similarity - 0.15)))
        
        part_info = mapping[i]
        print(f"{part_info['material_number']:>10}: {similarity:.4f} (matches: {len(good_matches)}/{len(matches)})")

if __name__ == "__main__":
    test_filtered_features() 