import os
import json
import base64
from typing import List, Dict, Any
from PIL import Image
import io
import numpy as np
import cv2
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not available. Make sure OPENAI_API_KEY is set in environment.")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("Warning: OpenAI library not available. AI features will be disabled.")
    OPENAI_AVAILABLE = False

# Initialize CLIP model and processor
print("🔄 Loading CLIP model for semantic matching...")
try:
    # Try loading with safetensors to avoid PyTorch security restrictions
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", use_safetensors=True)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    print("✅ CLIP model loaded successfully")
    CLIP_AVAILABLE = True
except Exception as e:
    print(f"⚠️ CLIP model not available: {e}")
    print("⚠️ Falling back to SIFT matching")
    CLIP_AVAILABLE = False

# Paths for embeddings
EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings.npy")
MAPPING_FILE = os.path.join(os.path.dirname(__file__), "part_image_embeddings_map.json")
IMAGES_ROOT = os.path.join(os.path.dirname(__file__), "images")

# Initialize FLANN matcher for fallback SIFT
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

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

def get_image_features_from_bytes(image_bytes):
    """Extract SIFT keypoints and descriptors from image bytes with preprocessing"""
    try:
        print(f"🔍 Processing image bytes: {len(image_bytes)} bytes")
        
        # Convert bytes to numpy array
        image_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if img is None:
            print(f"⚠️ Could not decode uploaded image")
            return None, None
        
        print(f"📐 Decoded image shape: {img.shape}")
        
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
        
        print(f"📐 Preprocessed grayscale image shape: {gray.shape}")
        
        # Extract SIFT features with stricter parameters for camera images
        # Use higher contrast threshold to filter out noise
        sift = cv2.SIFT_create(
            nfeatures=5000,  # Limit features to prevent over-matching
            nOctaveLayers=3,
            contrastThreshold=0.06,  # Higher threshold to filter noise
            edgeThreshold=10,
            sigma=1.6
        )
        
        keypoints, descriptors = sift.detectAndCompute(gray, None)
        
        if descriptors is None or len(keypoints) < 10:
            print(f"⚠️ Insufficient SIFT features found in uploaded image: {len(keypoints) if keypoints else 0} keypoints")
            return None, None
        
        # Filter out low-quality keypoints (noise reduction)
        if len(keypoints) > 1000:
            # Sort keypoints by response strength and keep only the strongest
            keypoints_with_responses = [(kp, kp.response) for kp in keypoints]
            keypoints_with_responses.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only the top 1000 strongest keypoints
            filtered_keypoints = [kp for kp, _ in keypoints_with_responses[:1000]]
            
            # Recompute descriptors for filtered keypoints
            sift_filtered = cv2.SIFT_create(
                nfeatures=0,
                nOctaveLayers=3,
                contrastThreshold=0.06,
                edgeThreshold=10,
                sigma=1.6
            )
            _, filtered_descriptors = sift_filtered.compute(gray, filtered_keypoints)
            
            keypoints = filtered_keypoints
            descriptors = filtered_descriptors
            
            print(f"🔧 Filtered from {len(keypoints_with_responses)} to {len(keypoints)} strongest keypoints")
        
        print(f"✅ Successfully extracted {len(keypoints)} keypoints and descriptors shape: {descriptors.shape}")
        return keypoints, descriptors
    except Exception as e:
        print(f"❌ Error processing uploaded image: {e}")
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
        
        return similarity
        
    except Exception as e:
        print(f"❌ Error computing similarity: {e}")
        return 0.0

def compute_image_similarity_detailed(query_keypoints, query_descriptors, stored_keypoints, stored_descriptors):
    """
    Compute similarity with detailed debugging information and more robust matching
    """
    if query_descriptors is None or stored_descriptors is None:
        return 0.0, {}
    
    try:
        # Use FLANN matcher for better performance
        matches = flann.knnMatch(query_descriptors, stored_descriptors, k=2)
        
        # Apply more strict Lowe's ratio test for better quality matches
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                # More strict ratio test (0.7 instead of 0.9) to reduce false positives
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
        
        # Calculate similarity score with multiple metrics
        min_keypoints = min(len(query_keypoints), len(stored_keypoints))
        if min_keypoints == 0:
            return 0.0, {}
        
        # Multiple similarity metrics
        match_ratio = len(good_matches) / min_keypoints
        
        # Normalize by the smaller number of keypoints to avoid bias
        # This helps when comparing images with very different numbers of features
        smaller_keypoints = min(len(query_keypoints), len(stored_keypoints))
        larger_keypoints = max(len(query_keypoints), len(stored_keypoints))
        
        # Adjusted similarity calculation that's more strict about match quality
        if smaller_keypoints > 0:
            # Use a combination of absolute matches and relative ratio
            absolute_score = len(good_matches) / smaller_keypoints
            relative_score = len(good_matches) / larger_keypoints
            
            # Weighted combination favoring the smaller image (camera captures)
            similarity = 0.7 * absolute_score + 0.3 * relative_score
            
            # Apply sigmoid function with stricter parameters for better match quality
            # Require higher match ratios for good similarity scores
            similarity = 1 / (1 + np.exp(-8 * (similarity - 0.15)))
        else:
            similarity = 0.0
        
        # Return detailed info
        details = {
            'total_matches': len(matches),
            'good_matches': len(good_matches),
            'match_ratio': match_ratio,
            'query_keypoints': len(query_keypoints),
            'stored_keypoints': len(stored_keypoints),
            'min_keypoints': min_keypoints,
            'absolute_score': len(good_matches) / smaller_keypoints if smaller_keypoints > 0 else 0,
            'relative_score': len(good_matches) / larger_keypoints if larger_keypoints > 0 else 0
        }
        
        return similarity, details
        
    except Exception as e:
        print(f"❌ Error computing similarity: {e}")
        return 0.0, {}

def get_clip_features_from_bytes(image_bytes):
    """Extract CLIP features from image bytes for semantic matching"""
    try:
        print(f"🔍 Processing image bytes with CLIP: {len(image_bytes)} bytes")
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Process image with CLIP
        inputs = clip_processor(images=image, return_tensors="pt", padding=True)
        
        # Get image features
        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
            # Normalize features
            image_features = F.normalize(image_features, p=2, dim=1)
        
        print(f"✅ Successfully extracted CLIP features: {image_features.shape}")
        return image_features
        
    except Exception as e:
        print(f"❌ Error processing image with CLIP: {e}")
        return None

def get_clip_features_from_path(image_path):
    """Extract CLIP features from image file"""
    try:
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Process image with CLIP
        inputs = clip_processor(images=image, return_tensors="pt", padding=True)
        
        # Get image features
        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
            # Normalize features
            image_features = F.normalize(image_features, p=2, dim=1)
        
        return image_features
        
    except Exception as e:
        print(f"❌ Error processing {image_path} with CLIP: {e}")
        return None

def compute_clip_similarity(query_features, stored_features):
    """
    Compute semantic similarity between two images using CLIP features
    Returns a similarity score between 0 and 1
    """
    if query_features is None or stored_features is None:
        return 0.0
    
    try:
        # Compute cosine similarity
        similarity = F.cosine_similarity(query_features, stored_features, dim=1)
        
        # Convert to 0-1 range (cosine similarity is -1 to 1)
        similarity = (similarity + 1) / 2
        
        return similarity.item()
        
    except Exception as e:
        print(f"❌ Error computing CLIP similarity: {e}")
        return 0.0

def compute_clip_similarity_detailed(query_features, stored_features):
    """
    Compute CLIP similarity with detailed information
    """
    if query_features is None or stored_features is None:
        return 0.0, {}
    
    try:
        # Compute cosine similarity
        similarity = F.cosine_similarity(query_features, stored_features, dim=1)
        
        # Convert to 0-1 range
        similarity_score = (similarity + 1) / 2
        
        # Return detailed info
        details = {
            'cosine_similarity': similarity.item(),
            'normalized_similarity': similarity_score.item(),
            'feature_dimensions': query_features.shape[1]
        }
        
        return similarity_score.item(), details
        
    except Exception as e:
        print(f"❌ Error computing CLIP similarity: {e}")
        return 0.0, {}

class AIService:
    def __init__(self, api_key: str = None):
        # Use CLIP for semantic matching
        print("✅ AIService initialized for CLIP-based semantic matching")
        # Load embeddings and mapping at init
        self.stored_features = None
        self.mapping = None
        self._load_features()

    def _load_features(self):
        try:
            # Load stored features (CLIP embeddings)
            features_data = np.load(EMBEDDINGS_FILE, allow_pickle=True)
            self.stored_features = features_data
            
            with open(MAPPING_FILE, 'r') as f:
                self.mapping = json.load(f)
            print(f"✅ Loaded {len(self.stored_features)} feature sets and mapping")
        except Exception as e:
            print(f"❌ Error loading features or mapping: {e}")
            self.stored_features = None
            self.mapping = None

    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def encode_pil_image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return img_str
    
    def analyze_image(self, image_data: bytes, spare_parts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze uploaded image and find matching spare parts using CLIP semantic similarity
        """
        print(f"🔍 Starting image analysis...")
        print(f"📦 Image data size: {len(image_data)} bytes")

        if self.stored_features is None or self.mapping is None:
            print("❌ Features or mapping not loaded, using fallback analysis")
            return self._fallback_analysis("", spare_parts_data)

        if not CLIP_AVAILABLE:
            print("⚠️ CLIP model not available, but stored features exist")
            print("🔄 Attempting to use stored CLIP features with basic matching")
        
        print(f"🔍 Starting CLIP semantic analysis with {len(self.mapping)} stored images")
        
        # Compute CLIP features for uploaded image
        query_features = get_clip_features_from_bytes(image_data)
        if query_features is None:
            print("❌ Could not compute CLIP features for uploaded image, using fallback")
            return self._fallback_analysis("", spare_parts_data)
        
        print(f"✅ Extracted CLIP features from uploaded image")
        
        # Compute similarity to all stored images
        similarities = []
        similarity_details = []
        for i, stored_feature in enumerate(self.stored_features):
            # Load stored CLIP features
            stored_features = torch.tensor(stored_feature['clip_features'], dtype=torch.float32)
            
            print(f"🔍 Comparing with {self.mapping[i]['material_number']}")
            
            similarity, details = compute_clip_similarity_detailed(
                query_features, stored_features
            )
            similarities.append(similarity)
            similarity_details.append(details)
            
            print(f"   Semantic similarity with {self.mapping[i]['material_number']}: {similarity:.3f}")
            print(f"   Cosine similarity: {details['cosine_similarity']:.3f}")
        
        # Get top matches with semantic threshold
        min_similarity_threshold = 0.9  # CLIP semantic threshold - only return matches above 90%
        print(f"🎯 Using CLIP semantic threshold: {min_similarity_threshold}")
        
        # Find all matches above threshold
        valid_matches = []
        for idx, sim_score in enumerate(similarities):
            if sim_score >= min_similarity_threshold:
                part_info = self.mapping[idx]
                valid_matches.append({
                    "material_number": part_info["material_number"],
                    "confidence_score": float(sim_score),
                    "match_reason": f"CLIP semantic matching: {sim_score:.3f}",
                    "details": similarity_details[idx]
                })
        
        # Sort by confidence score
        valid_matches.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        # Return matches based on confidence
        if valid_matches:
            best_match = valid_matches[0]
            # Since threshold is now 90%, any match above threshold is high-confidence
            matches = [best_match]
            print(f"✅ Found 1 high-confidence semantic match: {best_match['confidence_score']:.3f}")
        else:
            matches = []
            print("⚠️ No semantic matches found above threshold")
        
        # If no valid matches found, return fallback
        if not matches:
            print("⚠️ No matches above threshold. Returning no match.")
            return []
        
        return matches

    def _fallback_analysis(self, ai_response: str, spare_parts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Fallback analysis is now disabled; always return no matches
        print("🔄 Fallback analysis disabled. Returning no matches.")
        return []

    def is_model_available(self) -> bool:
        # Check if features are loaded (CLIP or SIFT fallback)
        return self.stored_features is not None and self.mapping is not None 