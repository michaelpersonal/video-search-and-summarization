import os
import json
import numpy as np
import cv2

# Path to images directory
IMAGES_ROOT = os.path.join(os.path.dirname(__file__), "images")

# Output files
EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings.npy")
MAPPING_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings_map.json")

# Initialize SIFT detector and FLANN matcher
sift = cv2.SIFT_create()
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

def deserialize_keypoints(serialized_keypoints):
    """Convert serialized keypoints back to cv2.KeyPoint objects"""
    keypoints = []
    for kp_dict in serialized_keypoints:
        kp = cv2.KeyPoint(
            x=kp_dict['pt'][0],
            y=kp_dict['pt'][1],
            size=kp_dict['size'],
            angle=kp_dict['angle'],
            response=kp_dict['response'],
            octave=kp_dict['octave'],
            class_id=kp_dict['class_id']
        )
        keypoints.append(kp)
    return keypoints

def get_image_features_from_path(image_path):
    """Extract SIFT keypoints and descriptors from image file"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            print(f"⚠️ Could not read image: {image_path}")
            return None, None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = sift.detectAndCompute(gray, None)
        
        if descriptors is None or len(keypoints) < 10:
            print(f"⚠️ Insufficient SIFT features found in: {image_path}")
            return None, None
            
        print(f"✅ Extracted {len(keypoints)} features from {os.path.basename(image_path)}")
        return keypoints, descriptors
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return None, None

def compute_image_similarity(query_keypoints, query_descriptors, stored_keypoints, stored_descriptors):
    """
    Compute similarity between two images using SIFT feature matching
    Returns a similarity score between 0 and 1
    """
    if query_descriptors is None or stored_descriptors is None:
        return 0.0
    
    try:
        # Use FLANN matcher for better performance
        matches = flann.knnMatch(query_descriptors, stored_descriptors, k=2)
        
        # Apply Lowe's ratio test to filter good matches
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.8 * n.distance:  # Slightly more lenient ratio test
                    good_matches.append(m)
        
        # Calculate similarity score based on number of good matches
        # Normalize by the minimum number of keypoints to avoid bias
        min_keypoints = min(len(query_keypoints), len(stored_keypoints))
        if min_keypoints == 0:
            return 0.0
        
        # Use a more lenient scoring approach
        match_ratio = len(good_matches) / min_keypoints
        
        # Apply sigmoid function to get a score between 0 and 1
        # Adjusted parameters to be more lenient
        similarity = 1 / (1 + np.exp(-8 * (match_ratio - 0.15)))
        
        return similarity, match_ratio, len(good_matches), min_keypoints
        
    except Exception as e:
        print(f"❌ Error computing similarity: {e}")
        return 0.0, 0.0, 0, 0

def test_upload_simulation():
    print("🧪 Testing upload simulation...")
    
    # Load stored features
    try:
        features_data = np.load(EMBEDDINGS_FILE, allow_pickle=True)
        with open(MAPPING_FILE, 'r') as f:
            mapping = json.load(f)
        print(f"✅ Loaded {len(features_data)} feature sets and mapping")
    except Exception as e:
        print(f"❌ Error loading features: {e}")
        return
    
    # Test with one of the stored images as if it were uploaded
    print("\n🔍 Testing with stored image as upload:")
    print("-" * 80)
    
    # Use the first image as the "uploaded" image
    test_image_path = os.path.join(IMAGES_ROOT, mapping[0]['image_path'].replace('images/', ''))
    print(f"Testing with: {test_image_path}")
    
    # Get features for the "uploaded" image
    query_keypoints, query_descriptors = get_image_features_from_path(test_image_path)
    
    if query_keypoints is None or query_descriptors is None:
        print("❌ Could not extract features from test image")
        return
    
    print(f"Query image has {len(query_keypoints)} keypoints")
    
    # Test similarity with all stored images
    similarities = []
    for i, stored_feature in enumerate(features_data):
        stored_keypoints = deserialize_keypoints(stored_feature['keypoints'])
        stored_descriptors = stored_feature['descriptors']
        
        similarity, match_ratio, good_matches, min_keypoints = compute_image_similarity(
            query_keypoints, query_descriptors,
            stored_keypoints, stored_descriptors
        )
        
        similarities.append(similarity)
        print(f"   Similarity with {mapping[i]['material_number']}: {similarity:.4f} (ratio: {match_ratio:.4f}, matches: {good_matches})")
    
    # Test with different thresholds
    thresholds = [0.01, 0.05, 0.1, 0.15, 0.2, 0.3]
    print(f"\n🔍 Testing different thresholds:")
    print("-" * 80)
    
    for threshold in thresholds:
        valid_matches = []
        for idx, sim_score in enumerate(similarities):
            if sim_score >= threshold:
                valid_matches.append((mapping[idx]['material_number'], sim_score))
        
        print(f"Threshold {threshold:.2f}: {len(valid_matches)} matches")
        for material_number, score in valid_matches:
            print(f"  {material_number}: {score:.4f}")

if __name__ == "__main__":
    test_upload_simulation() 