#!/bin/bash

# AICP API Server Startup Script

echo "=========================================="
echo "Starting AICP Research Portal API"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements-api.txt --quiet

# Run the API server
echo "Starting API server..."
python api_server.py
