#!/bin/bash

# Start development servers

echo "Starting development environment..."

# Kill any existing Python processes
pkill -f "python src/python/server.py" 2>/dev/null

# Start Python server in background
echo "Starting Python server..."
source venv/bin/activate
python src/python/server.py &
PYTHON_PID=$!

# Wait for Python server to start
sleep 2

# Start Electron app
echo "Starting Electron app..."
npm run dev

# When Electron exits, kill Python server
kill $PYTHON_PID 2>/dev/null