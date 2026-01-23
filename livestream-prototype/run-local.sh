#!/bin/bash

# Script untuk download dan jalankan prototype
echo "========================================="
echo "  Download Livestream Prototype"
echo "========================================="
echo ""

# Clone repository
echo "1. Downloading files from Git..."
git clone https://github.com/herrylim2001/stock-prediction-indonesia.git
cd stock-prediction-indonesia
git checkout claude/video-livestream-prototype-UZbhE
cd livestream-prototype

echo ""
echo "2. Installing dependencies..."
cd backend
pip install Flask Flask-CORS Flask-SocketIO python-socketio eventlet

echo ""
echo "3. Starting servers..."
# Start backend
python app.py &
BACKEND_PID=$!

# Start HTTP server
cd ..
python -m http.server 8080 &
HTTP_PID=$!

echo ""
echo "========================================="
echo "  ✅ SERVERS RUNNING!"
echo "========================================="
echo ""
echo "  Backend API: http://localhost:5000"
echo "  Frontend: http://localhost:8080"
echo ""
echo "  📊 Backoffice: http://localhost:8080/backoffice/index.html"
echo "  📱 Client: http://localhost:8080/client/index.html"
echo ""
echo "  Press Ctrl+C to stop servers"
echo "========================================="

# Wait for Ctrl+C
trap "kill $BACKEND_PID $HTTP_PID; exit" INT
wait
