#!/bin/bash

# Mini Uber Multi-Dashboard Launcher
echo "🚀 Mini Uber Multi-Dashboard System"
echo "=================================="

# Check if required files exist
required_files=("main.py" "database.py" "user_dashboard.html" "driver_dashboard.html" "admin_dashboard.html")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        echo "Please ensure all files are in the current directory."
        exit 1
    fi
done

echo "✅ All required files found!"

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true  
lsof -ti:8002 | xargs kill -9 2>/dev/null || true
lsof -ti:8003 | xargs kill -9 2>/dev/null || true

echo "🔧 Starting API server..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!
sleep 3

echo "👤 Starting User Dashboard (Port 8001)..."
cd .
python -m http.server 8001 &
USER_PID=$!

echo "🚗 Starting Driver Dashboard (Port 8002)..."
python -m http.server 8002 &
DRIVER_PID=$!

echo "👨‍💼 Starting Admin Dashboard (Port 8003)..."
python -m http.server 8003 &
ADMIN_PID=$!

sleep 2

echo ""
echo "🎉 All servers started successfully!"
echo ""
echo "📱 Access your dashboards:"
echo "   👤 User Dashboard:   http://localhost:8001/user_dashboard.html"
echo "   🚗 Driver Dashboard: http://localhost:8002/driver_dashboard.html"
echo "   👨‍💼 Admin Dashboard:  http://localhost:8003/admin_dashboard.html"
echo "   🔧 API Server:       http://localhost:8000"
echo ""
echo "📝 API Documentation: http://localhost:8000/docs"
echo ""
echo "⚠️  Press Ctrl+C to stop all servers"
echo "=================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all servers..."
    kill $API_PID $USER_PID $DRIVER_PID $ADMIN_PID 2>/dev/null || true
    echo "✅ All servers stopped!"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for user interrupt
wait