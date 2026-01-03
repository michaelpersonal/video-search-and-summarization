#!/usr/bin/env python3
"""
Setup script for OpenAI API key configuration
"""

import os
import sys

def main():
    print("🔧 OpenAI API Key Setup")
    print("=" * 40)
    
    # Check if API key is already set
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        print(f"✅ OpenAI API key is already set: {current_key[:8]}...")
        response = input("Do you want to update it? (y/N): ").lower()
        if response != 'y':
            print("Setup complete!")
            return
    
    print("\n📋 To get your OpenAI API key:")
    print("1. Visit: https://platform.openai.com/api-keys")
    print("2. Sign up or log in to your account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the generated key")
    print()
    
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. OpenAI API keys start with 'sk-'")
        return
    
    # Create .env file
    env_file = os.path.join('backend', '.env')
    try:
        with open(env_file, 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print(f"✅ API key saved to {env_file}")
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return
    
    # Set environment variable for current session
    os.environ['OPENAI_API_KEY'] = api_key
    print("✅ API key set for current session")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Start the backend: cd backend && python main.py")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Visit http://localhost:3000 to use the app")
    
    print("\n💡 Note: The API key is saved in backend/.env")
    print("   Make sure to add this file to .gitignore to keep it secure!")

if __name__ == "__main__":
    main() 