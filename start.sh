#!/bin/bash

echo "🚀 Starting Spare Parts Identification System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

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

echo "📦 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "🗄️ Setting up database..."
python sample_data.py

echo "🔧 Starting backend server..."
python main.py &
BACKEND_PID=$!

cd ..

echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🌐 Starting frontend development server..."
npm start &
FRONTEND_PID=$!

cd ..

echo "✅ Application started!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait 