#!/bin/bash
# Pharmaceutical QMS - Start Backend Server
# This script starts the Flask API server

echo "============================================================"
echo "Pharmaceutical QMS - Backend Server Startup"
echo "============================================================"
echo ""

# Check if database exists
if [ ! -f "backend/qms_database.db" ]; then
    echo "Database not found. Initializing database..."
    cd backend
    python3 init_db.py
    cd ..
    echo ""
fi

echo "Starting API server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

cd backend
python3 api.py
