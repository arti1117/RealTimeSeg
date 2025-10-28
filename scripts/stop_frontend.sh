#!/bin/bash

echo "🛑 Stopping Frontend Server..."
echo ""

# Find process using port 8080
PID=$(lsof -ti:8080 2>/dev/null)

if [ -z "$PID" ]; then
    echo "✓ No frontend server running on port 8080"
    exit 0
fi

# Show what we're killing
echo "Found process(es): $PID"
ps -p $PID -o pid,cmd 2>/dev/null

# Kill the process
kill $PID 2>/dev/null

# Wait a moment
sleep 1

# Verify it's stopped
if lsof -ti:8080 >/dev/null 2>&1; then
    echo "⚠️  Process still running, forcing kill..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# Final check
if lsof -ti:8080 >/dev/null 2>&1; then
    echo "❌ Failed to stop server"
    exit 1
else
    echo "✅ Frontend server stopped successfully"
    echo "✓ Port 8080 is now free"
fi
