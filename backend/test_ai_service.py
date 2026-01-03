#!/usr/bin/env python3

import sys
import traceback

def test_ai_service_import():
    print("🧪 Testing AI service import...")
    
    try:
        print("📦 Importing ai_service...")
        from ai_service import AIService
        print("✅ AIService imported successfully")
        
        print("🔧 Creating AIService instance...")
        ai_service = AIService()
        print("✅ AIService instance created")
        
        print("🔍 Checking if model is available...")
        is_available = ai_service.is_model_available()
        print(f"✅ Model available: {is_available}")
        
        if is_available:
            print(f"📊 Stored features: {len(ai_service.stored_features)}")
            print(f"📋 Mapping entries: {len(ai_service.mapping)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ai_service_import() 