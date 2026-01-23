#!/bin/bash

echo "========================================="
echo "  LiveStream Prototype - Server Starter"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python3 detected: $(python3 --version)"
echo ""

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "========================================="
echo "  🚀 Starting Backend Server..."
echo "========================================="
echo ""
echo "  Backend API: http://localhost:5000"
echo "  Backoffice:  Open ../backoffice/index.html"
echo "  Client:      Open ../client/index.html"
echo ""
echo "  Press Ctrl+C to stop the server"
echo ""
echo "========================================="
echo ""

# Start the server
python app.py
