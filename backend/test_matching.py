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

def test_matching():
    print("🧪 Testing SIFT matching algorithm...")
    
    # Load stored features
    try:
        features_data = np.load(EMBEDDINGS_FILE, allow_pickle=True)
        with open(MAPPING_FILE, 'r') as f:
            mapping = json.load(f)
        print(f"✅ Loaded {len(features_data)} feature sets and mapping")
    except Exception as e:
        print(f"❌ Error loading features: {e}")
        return
    
    # Test matching between all pairs of images
    print("\n🔍 Testing all image pairs:")
    print("-" * 80)
    
    for i in range(len(features_data)):
        for j in range(i + 1, len(features_data)):
            # Get features for both images
            stored_keypoints_i = deserialize_keypoints(features_data[i]['keypoints'])
            stored_descriptors_i = features_data[i]['descriptors']
            
            stored_keypoints_j = deserialize_keypoints(features_data[j]['keypoints'])
            stored_descriptors_j = features_data[j]['descriptors']
            
            # Compute similarity
            similarity, match_ratio, good_matches, min_keypoints = compute_image_similarity(
                stored_keypoints_i, stored_descriptors_i,
                stored_keypoints_j, stored_descriptors_j
            )
            
            print(f"{mapping[i]['material_number']} vs {mapping[j]['material_number']}:")
            print(f"  Similarity: {similarity:.4f}")
            print(f"  Match ratio: {match_ratio:.4f}")
            print(f"  Good matches: {good_matches}")
            print(f"  Min keypoints: {min_keypoints}")
            print()
    
    # Test with a very low threshold to see what scores we get
    print("🔍 Testing with very low threshold (0.01):")
    print("-" * 80)
    
    for i in range(len(features_data)):
        for j in range(i + 1, len(features_data)):
            stored_keypoints_i = deserialize_keypoints(features_data[i]['keypoints'])
            stored_descriptors_i = features_data[i]['descriptors']
            
            stored_keypoints_j = deserialize_keypoints(features_data[j]['keypoints'])
            stored_descriptors_j = features_data[j]['descriptors']
            
            similarity, match_ratio, good_matches, min_keypoints = compute_image_similarity(
                stored_keypoints_i, stored_descriptors_i,
                stored_keypoints_j, stored_descriptors_j
            )
            
            if similarity >= 0.01:  # Very low threshold
                print(f"{mapping[i]['material_number']} vs {mapping[j]['material_number']}: {similarity:.4f}")

if __name__ == "__main__":
    test_matching() 