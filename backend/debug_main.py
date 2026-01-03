#!/usr/bin/env python3

import traceback
import sys

def main():
    print("🚀 Starting debug server...")
    
    try:
        print("📦 Importing main...")
        from main import app
        
        print("🔧 Creating FastAPI app...")
        print(f"✅ App created: {app}")
        
        print("🔍 Testing AI service initialization...")
        from ai_service import AIService
        ai_service = AIService()
        print(f"✅ AI service available: {ai_service.is_model_available()}")
        
        print("🌐 Starting server...")
        import uvicorn
        # Run without SSL for debugging
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main() 