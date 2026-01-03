#!/usr/bin/env python3

import os
import cv2
import numpy as np
from ai_service import get_image_features_from_bytes

def test_image_processing_consistency():
    """Test if image processing is consistent between file reading and byte processing"""
    print("🧪 Testing image processing consistency...")
    
    # Test with one of the stored images
    test_image_path = "images/6/IMG_3701.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print(f"📸 Testing with: {test_image_path}")
    
    # Method 1: Read from file (like stored images)
    print("\n📁 Method 1: Reading from file (like stored images)")
    kp1, des1 = get_image_features_from_path(test_image_path)
    
    if kp1 is None or des1 is None:
        print("❌ Failed to extract features from file")
        return
    
    print(f"✅ File method: {len(kp1)} keypoints, descriptors shape: {des1.shape}")
    
    # Method 2: Read as bytes then process (like camera uploads)
    print("\n📦 Method 2: Reading as bytes then processing (like camera uploads)")
    with open(test_image_path, "rb") as f:
        image_bytes = f.read()
    
    kp2, des2 = get_image_features_from_bytes(image_bytes)
    
    if kp2 is None or des2 is None:
        print("❌ Failed to extract features from bytes")
        return
    
    print(f"✅ Bytes method: {len(kp2)} keypoints, descriptors shape: {des2.shape}")
    
    # Compare the results
    print("\n🔍 Comparing results:")
    print(f"Keypoint count difference: {abs(len(kp1) - len(kp2))}")
    print(f"Descriptor shape difference: {des1.shape != des2.shape}")
    
    if des1.shape == des2.shape:
        # Compare descriptor values
        descriptor_diff = np.mean(np.abs(des1 - des2))
        print(f"Average descriptor difference: {descriptor_diff:.6f}")
        
        if descriptor_diff < 0.001:
            print("✅ Processing methods are consistent!")
        else:
            print("⚠️ Processing methods produce different results!")
    else:
        print("❌ Processing methods produce different descriptor shapes!")
    
    # Test similarity between the two methods
    print("\n🔍 Testing similarity between the two processing methods:")
    
    # Initialize FLANN matcher
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    # Match features
    matches = flann.knnMatch(des1, des2, k=2)
    
    # Apply Lowe's ratio test
    good_matches = []
    for match_pair in matches:
        if len(match_pair) == 2:
            m, n = match_pair
            if m.distance < 0.8 * n.distance:
                good_matches.append(m)
    
    min_keypoints = min(len(kp1), len(kp2))
    match_ratio = len(good_matches) / min_keypoints if min_keypoints > 0 else 0
    similarity = 1 / (1 + np.exp(-8 * (match_ratio - 0.15)))
    
    print(f"   Match ratio: {match_ratio:.4f}")
    print(f"   Similarity score: {similarity:.4f}")
    
    if similarity > 0.9:
        print("✅ High similarity - processing methods are equivalent")
    else:
        print("⚠️ Low similarity - processing methods are different!")

def get_image_features_from_path(image_path):
    """Extract SIFT keypoints and descriptors from image file (same as regenerate_features.py)"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            print(f"⚠️ Could not read image: {image_path}")
            return None, None
        
        # Apply preprocessing to make features more robust to lighting changes
        # 1. Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Apply histogram equalization to normalize lighting
        gray = cv2.equalizeHist(gray)
        
        # 3. Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 4. Apply adaptive histogram equalization for better local contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Extract SIFT features with more lenient parameters
        sift = cv2.SIFT_create(
            nfeatures=0,  # No limit on features
            nOctaveLayers=3,
            contrastThreshold=0.04,  # Lower threshold for more features
            edgeThreshold=10,
            sigma=1.6
        )
        
        keypoints, descriptors = sift.detectAndCompute(gray, None)
        
        if descriptors is None or len(keypoints) < 10:
            print(f"⚠️ Insufficient SIFT features found in: {image_path}")
            return None, None
        
        return keypoints, descriptors
        
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return None, None

if __name__ == "__main__":
    test_image_processing_consistency() 