import os
import json
import numpy as np
import cv2
from ai_service import AIService

def test_backend_ai_service():
    print("🧪 Testing backend AI service...")
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.is_model_available():
        print("❌ AI service not available")
        return
    
    print("✅ AI service initialized successfully")
    
    # Test with one of the stored images
    test_image_path = os.path.join(os.path.dirname(__file__), "images", "6", "IMG_3701.jpg")
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print(f"📸 Testing with: {test_image_path}")
    
    # Read image as bytes (simulating upload)
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    
    # Create dummy spare parts data
    spare_parts_data = [
        {
            "material_number": "IMG_3701",
            "description": "Test part 1",
            "category": "Test",
            "manufacturer": "Test",
            "specifications": "Test",
            "image_path": "images/6/IMG_3701.jpg"
        }
    ]
    
    # Analyze image
    print("🔍 Analyzing image...")
    matches = ai_service.analyze_image(image_data, spare_parts_data)
    
    print(f"📊 Found {len(matches)} matches:")
    for match in matches:
        print(f"  {match['material_number']}: {match['confidence_score']:.4f} - {match['match_reason']}")

if __name__ == "__main__":
    test_backend_ai_service() 