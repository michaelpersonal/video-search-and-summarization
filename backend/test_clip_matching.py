#!/usr/bin/env python3

import os
import json
import numpy as np
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from ai_service import AIService, get_clip_features_from_bytes

def test_clip_matching():
    """Test CLIP-based semantic matching"""
    print("🧪 Testing CLIP semantic matching...")
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.is_model_available():
        print("❌ AI service not available")
        return
    
    print("✅ AI service initialized")
    
    # Test with one of the stored images
    test_image_path = "images/6/IMG_3701.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print(f"📸 Testing with: {test_image_path}")
    
    # Read image as bytes (simulating camera upload)
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    
    # Get CLIP features for uploaded image
    query_features = get_clip_features_from_bytes(image_data)
    
    if query_features is None:
        print("❌ Could not extract CLIP features from uploaded image")
        return
    
    print(f"✅ Extracted CLIP features from uploaded image")
    
    # Test similarity with all stored images
    print("\n🔍 Testing semantic similarity with all stored images:")
    print("-" * 80)
    
    similarities = []
    for i, stored_feature in enumerate(ai_service.stored_features):
        stored_features = torch.tensor(stored_feature['clip_features'], dtype=torch.float32)
        
        # Compute similarity
        similarity = F.cosine_similarity(query_features, stored_features, dim=1)
        normalized_similarity = (similarity + 1) / 2
        
        part_info = ai_service.mapping[i]
        similarities.append((normalized_similarity.item(), part_info))
        
        print(f"{part_info['material_number']:>10}: {normalized_similarity.item():.4f}")
        print(f"   Cosine similarity: {similarity.item():.4f}")
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    print("\n📊 Results sorted by similarity:")
    print("-" * 80)
    for i, (sim, part_info) in enumerate(similarities):
        print(f"{i+1:2d}. {part_info['material_number']:>10}: {sim:.4f}")
    
    # Analyze the best match
    if similarities:
        best_sim, best_part = similarities[0]
        print(f"\n🔍 Analysis of best match ({best_part['material_number']}):")
        print("-" * 80)
        print(f"Similarity score: {best_sim:.4f}")
        
        # Check if this should be considered a match
        if best_sim > 0.8:
            print("✅ This should be considered a high-confidence match!")
        elif best_sim > 0.6:
            print("✅ This should be considered a good match!")
        elif best_sim > 0.4:
            print("⚠️ This should be considered a moderate match!")
        else:
            print("❌ This should not be considered a match!")
    
    # Test with different thresholds
    print(f"\n🎯 Testing different thresholds:")
    print("-" * 80)
    thresholds = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    
    for threshold in thresholds:
        matches = [sim for sim, _ in similarities if sim >= threshold]
        print(f"Threshold {threshold:.1f}: {len(matches)} matches")
        if matches:
            print(f"  Best match: {similarities[0][1]['material_number']} ({similarities[0][0]:.4f})")

if __name__ == "__main__":
    test_clip_matching() 