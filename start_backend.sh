#!/bin/bash

echo "🔧 Starting Backend Server..."

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f "backend/.env" ]; then
        echo "📋 Loading OpenAI API key from backend/.env"
        export $(cat backend/.env | xargs)
    else
        echo "⚠️  OpenAI API key not found."
        echo "   Run: python3 setup_openai.py"
        echo "   Or set: export OPENAI_API_KEY='your_api_key'"
        echo ""
        read -p "Do you want to continue without AI features? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Setup cancelled. Please configure OpenAI API key first."
            exit 1
        fi
    fi
fi

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies need to be reinstalled
if [ ! -f "venv/lib/python*/site-packages/openai" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Dependencies already installed."
fi

# Set up database
echo "Setting up database..."
python sample_data.py

# Start server
echo "Starting backend server on http://localhost:8000"
python main.py 