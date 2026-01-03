#!/usr/bin/env python3

import subprocess
import sys
import importlib

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 13:
        print("✅ Python 3.13+ detected - compatible with our dependencies")
    else:
        print("⚠️ Python version might have compatibility issues")
    
    return True

def install_package(package, version_spec=None):
    """Install a package with optional version specification"""
    try:
        if version_spec:
            cmd = [sys.executable, "-m", "pip", "install", f"{package}{version_spec}"]
        else:
            cmd = [sys.executable, "-m", "pip", "install", package]
        
        print(f"📦 Installing {package}{version_spec or ''}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully installed {package}")
            return True
        else:
            print(f"❌ Failed to install {package}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing {package}: {e}")
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} is already installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is not installed")
        return False

def main():
    """Main setup function"""
    print("🔧 Setting up dependencies for CLIP-based semantic matching...")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    print()
    
    # List of packages to install with specific versions for Python 3.13.3
    packages = [
        ("numpy", "<2.0.0"),  # Fix NumPy 2.x compatibility issue
        ("torch", ">=2.6.0"),  # Fix security vulnerability
        ("transformers", ">=4.52.0"),
        ("Pillow", ">=10.0.0"),
        ("opencv-python", ">=4.8.0"),
        ("fastapi", ">=0.104.0"),
        ("uvicorn[standard]", ">=0.24.0"),
        ("python-multipart", ">=0.0.6"),
    ]
    
    print("📋 Checking and installing packages...")
    print("-" * 60)
    
    success_count = 0
    for package, version in packages:
        if not check_package(package.split('[')[0]):  # Remove [standard] for checking
            if install_package(package, version):
                success_count += 1
        else:
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"📊 Installation summary: {success_count}/{len(packages)} packages ready")
    
    if success_count == len(packages):
        print("✅ All dependencies are ready! You can now start the backend server.")
        print("\n🚀 To start the server, run:")
        print("   python start_https.py")
    else:
        print("⚠️ Some packages failed to install. Please check the errors above.")
        print("\n💡 Try running manually:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main() 