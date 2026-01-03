import os
import json
import numpy as np
from sqlalchemy.orm import Session
from database import SessionLocal, create_tables
from models import SparePart
from PIL import Image
import cv2

# Path to images directory (adjust if needed)
IMAGES_ROOT = os.path.join(os.path.dirname(__file__), "images")

# Output files
EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings.npy")
MAPPING_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings_map.json")

# Initialize SIFT detector
sift = cv2.SIFT_create()

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

def main():
    print("🔧 Computing image features for spare parts...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all spare parts with images
        parts_with_images = db.query(SparePart).filter(SparePart.image_path.isnot(None)).all()
        
        if not parts_with_images:
            print("❌ No spare parts with images found in database")
            return
        
        print(f"📸 Found {len(parts_with_images)} parts with images")
        
        features_list = []
        mapping = []
        
        for part in parts_with_images:
            # Handle the image path - remove "images/" prefix if it exists
            image_path_in_db = part.image_path
            if image_path_in_db.startswith("images/"):
                image_path_in_db = image_path_in_db[7:]  # Remove "images/" prefix
            
            image_path = os.path.join(IMAGES_ROOT, image_path_in_db)
            
            if not os.path.exists(image_path):
                print(f"⚠️ Image file not found: {image_path}")
                continue
            
            # Get features
            keypoints, descriptors = get_image_features(image_path)
            
            if keypoints is not None and descriptors is not None:
                # Store keypoints and descriptors
                features_dict = {
                    'keypoints': keypoints,
                    'descriptors': descriptors
                }
                features_list.append(features_dict)
                
                mapping.append({
                    'part_id': part.id,
                    'material_number': part.material_number,
                    'description': part.description,
                    'image_path': part.image_path,
                    'feature_index': len(features_list) - 1
                })
                print(f"✅ Processed: {part.material_number} - {part.description}")
            else:
                print(f"❌ Failed to process: {part.material_number}")
        
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
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 