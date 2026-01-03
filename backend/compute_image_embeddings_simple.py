import os
import json
import numpy as np
import cv2

# Path to images directory
IMAGES_ROOT = os.path.join(os.path.dirname(__file__), "images")

# Output files
EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings.npy")
MAPPING_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings_map.json")

# Initialize SIFT detector
sift = cv2.SIFT_create()

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
    """Extract SIFT keypoints and descriptors from image"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            print(f"⚠️ Could not read image: {image_path}")
            return None, None
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect SIFT keypoints and descriptors
        keypoints, descriptors = sift.detectAndCompute(gray, None)
        
        if descriptors is None or len(keypoints) < 10:
            print(f"⚠️ Insufficient SIFT features found in: {image_path}")
            return None, None
        
        print(f"✅ Extracted {len(keypoints)} features from {os.path.basename(image_path)}")
        # Serialize keypoints to make them pickleable
        serialized_keypoints = serialize_keypoints(keypoints)
        return serialized_keypoints, descriptors
        
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return None, None

def find_image_files(root_dir):
    """Recursively find all image files in directory and subdirectories"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                # Get relative path from images root
                rel_path = os.path.relpath(os.path.join(root, file), IMAGES_ROOT)
                image_files.append(rel_path)
    
    return image_files

def main():
    print("🔧 Computing image features for spare parts...")
    
    # Check if images directory exists
    if not os.path.exists(IMAGES_ROOT):
        print(f"❌ Images directory not found: {IMAGES_ROOT}")
        return
    
    # Get all image files recursively
    image_files = find_image_files(IMAGES_ROOT)
    
    if not image_files:
        print("❌ No image files found in images directory")
        return
    
    print(f"📸 Found {len(image_files)} image files")
    
    features_list = []
    mapping = []
    
    for rel_path in image_files:
        image_path = os.path.join(IMAGES_ROOT, rel_path)
        
        # Get features
        keypoints, descriptors = get_image_features(image_path)
        
        if keypoints is not None and descriptors is not None:
            # Store keypoints and descriptors
            features_dict = {
                'keypoints': keypoints,
                'descriptors': descriptors
            }
            features_list.append(features_dict)
            
            # Create a simple mapping using filename as material number
            material_number = os.path.splitext(os.path.basename(rel_path))[0]  # Remove extension
            
            mapping.append({
                'part_id': len(features_list),
                'material_number': material_number,
                'description': f"Part {material_number}",
                'image_path': f"images/{rel_path}",
                'feature_index': len(features_list) - 1
            })
            print(f"✅ Processed: {material_number} ({rel_path})")
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
    
    print(f"✅ Successfully processed {len(features_list)} images")
    
    # Test feature matching between first two images
    if len(features_list) > 1:
        print("🧪 Testing feature matching between first two images...")
        
        # Initialize FLANN matcher
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        
        # Get features from first two images
        kp1, des1 = features_list[0]['keypoints'], features_list[0]['descriptors']
        kp2, des2 = features_list[1]['keypoints'], features_list[1]['descriptors']
        
        # Match features
        matches = flann.knnMatch(des1, des2, k=2)
        
        # Apply Lowe's ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
        
        min_keypoints = min(len(kp1), len(kp2))
        match_ratio = len(good_matches) / min_keypoints if min_keypoints > 0 else 0
        similarity = 1 / (1 + np.exp(-10 * (match_ratio - 0.3)))
        
        print(f"   Match ratio: {match_ratio:.3f}")
        print(f"   Similarity score: {similarity:.3f}")

if __name__ == "__main__":
    main() 