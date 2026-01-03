import uvicorn
import ssl
import os

# Path to the certificate files (copied from frontend)
cert_path = "../frontend/localhost.pem"
key_path = "../frontend/localhost-key.pem"

if __name__ == "__main__":
    # Check if certificate files exist
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("❌ Certificate files not found. Please run the frontend setup first.")
        exit(1)
    
    # SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(cert_path, key_path)
    
    print("🔒 Starting backend server with HTTPS on https://192.168.1.85:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path,
        reload=True
    ) 