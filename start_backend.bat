@echo off
REM Pharmaceutical QMS - Start Backend Server
REM This script starts the Flask API server

echo ============================================================
echo Pharmaceutical QMS - Backend Server Startup
echo ============================================================
echo.

REM Check if database exists
if not exist "backend\qms_database.db" (
    echo Database not found. Initializing database...
    cd backend
    python init_db.py
    cd ..
    echo.
)

echo Starting API server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd backend
python api.py
