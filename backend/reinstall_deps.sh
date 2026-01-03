#!/bin/bash

echo "🔄 Reinstalling backend dependencies..."

# Remove existing virtual environment
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies reinstalled successfully!"
echo ""
echo "You can now start the backend with:"
echo "source venv/bin/activate"
echo "python main.py" 