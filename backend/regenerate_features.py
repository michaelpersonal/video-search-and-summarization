#!/usr/bin/env python3

import os
import json
import numpy as np
import cv2

def serialize_keypoints(keypoints):
    """Convert cv2.KeyPoint objects to a serializable list of dicts"""
    return [
        {
            'pt': kp.pt,
            'size': kp.size,
            'angle': kp.angle,
            'response': kp.response,
            'octave': kp.octave,
            'class_id': kp.class_id
        }
        for kp in keypoints
    ]

def get_image_features(image_path):
    """Extract SIFT keypoints and descriptors from image with preprocessing"""
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
        
        print(f"✅ Extracted {len(keypoints)} features from {os.path.basename(image_path)}")
        return keypoints, descriptors
        
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return None, None

def regenerate_features():
    print("🔄 Regenerating image features with improved preprocessing...")
    
    # Path to images directory
    IMAGES_ROOT = os.path.join(os.path.dirname(__file__), "images")
    
    # Output files
    EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings.npy")
    MAPPING_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings_map.json")
    
    # Check if images directory exists
    if not os.path.exists(IMAGES_ROOT):
        print(f"❌ Images directory not found: {IMAGES_ROOT}")
        return
    
    # Get all image files recursively
    image_files = []
    for root, dirs, files in os.walk(IMAGES_ROOT):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                rel_path = os.path.relpath(os.path.join(root, file), IMAGES_ROOT)
                image_files.append(rel_path)
    
    if not image_files:
        print("❌ No image files found in images directory")
        return
    
    print(f"📸 Found {len(image_files)} image files")
    
    features_list = []
    mapping = []
    
    for rel_path in image_files:
        image_path = os.path.join(IMAGES_ROOT, rel_path)
        
        # Get features with new preprocessing
        keypoints, descriptors = get_image_features(image_path)
        
        if keypoints is not None and descriptors is not None:
            # Store keypoints and descriptors
            features_dict = {
                'keypoints': serialize_keypoints(keypoints),
                'descriptors': descriptors
            }
            features_list.append(features_dict)
            
            # Create mapping using filename as material number
            material_number = os.path.splitext(os.path.basename(rel_path))[0]
            
            mapping.append({
                'part_id': len(features_list),
                'material_number': material_number,
                'description': f"Part {material_number}",
                'image_path': f"images/{rel_path}",
                'feature_index': len(features_list) - 1
            })
            print(f"✅ Processed: {material_number} ({rel_path}) - {len(keypoints)} keypoints")
        else:
            print(f"❌ Failed to process: {rel_path}")
    
    if not features_list:
        print("❌ No valid features generated")
        return
    
    # Save features as numpy array
    features_array = np.array(features_list, dtype=object)
    np.save(EMBEDDINGS_FILE, features_array)
    print(f"💾 Saved {len(features_list)} feature sets to {EMBEDDINGS_FILE}")
    
    # Save mapping
    with open(MAPPING_FILE, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"💾 Saved mapping to {MAPPING_FILE}")
    
    print("✅ Feature regeneration complete!")

if __name__ == "__main__":
    regenerate_features() 