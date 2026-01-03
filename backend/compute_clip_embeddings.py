#!/usr/bin/env python3

import os
import json
import numpy as np
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

def compute_clip_embeddings():
    """Compute CLIP embeddings for all images in the images directory"""
    print("🔄 Computing CLIP embeddings for semantic matching...")
    
    # Initialize CLIP model
    try:
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        print("✅ CLIP model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading CLIP model: {e}")
        return
    
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
            
            # Store features
            features_dict = {
                'clip_features': image_features.numpy()
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
            print(f"✅ Processed: {material_number} ({rel_path}) - CLIP features: {image_features.shape}")
            
        except Exception as e:
            print(f"❌ Failed to process: {rel_path} - {e}")
    
    if not features_list:
        print("❌ No valid features generated")
        return
    
    # Save features as numpy array
    features_array = np.array(features_list, dtype=object)
    np.save(EMBEDDINGS_FILE, features_array)
    print(f"💾 Saved {len(features_list)} CLIP feature sets to {EMBEDDINGS_FILE}")
    
    # Save mapping
    with open(MAPPING_FILE, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"💾 Saved mapping to {MAPPING_FILE}")
    
    print("✅ CLIP embedding computation complete!")
    
    # Test similarity between first two images
    if len(features_list) > 1:
        print("🧪 Testing CLIP similarity between first two images...")
        
        # Get features from first two images
        features1 = torch.tensor(features_list[0]['clip_features'], dtype=torch.float32)
        features2 = torch.tensor(features_list[1]['clip_features'], dtype=torch.float32)
        
        # Compute similarity
        similarity = F.cosine_similarity(features1, features2, dim=1)
        normalized_similarity = (similarity + 1) / 2
        
        print(f"   Cosine similarity: {similarity.item():.4f}")
        print(f"   Normalized similarity: {normalized_similarity.item():.4f}")

if __name__ == "__main__":
    compute_clip_embeddings() 