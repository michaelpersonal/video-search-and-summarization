#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

def generate_ssl_certificates():
    """Generate self-signed SSL certificates if they don't exist"""
    key_file = "localhost-key.pem"
    cert_file = "localhost.pem"
    
    if not os.path.exists(key_file) or not os.path.exists(cert_file):
        print("🔐 Generating self-signed SSL certificates...")
        try:
            # Generate private key and certificate
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:4096", 
                "-keyout", key_file, "-out", cert_file, "-days", "365", "-nodes",
                "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
            ], check=True)
            print("✅ SSL certificates generated successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to generate SSL certificates. Make sure OpenSSL is installed.")
            return False
        except FileNotFoundError:
            print("❌ OpenSSL not found. Please install OpenSSL or use HTTP version.")
            return False
    else:
        print("✅ SSL certificates already exist")
    
    return True

def main():
    print("🚀 Starting HTTPS server...")
    
    # Generate SSL certificates
    if not generate_ssl_certificates():
        print("⚠️  Falling back to HTTP server...")
        from main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return
    
    # Start HTTPS server
    try:
        from main import app
        import uvicorn
        print("🌐 Starting HTTPS server on https://0.0.0.0:8000")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            ssl_keyfile="localhost-key.pem",
            ssl_certfile="localhost.pem"
        )
    except Exception as e:
        print(f"❌ Error starting HTTPS server: {e}")
        print("⚠️  Falling back to HTTP server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 