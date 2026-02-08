#!/bin/bash
set -e  # Exit on error

echo "=== Building Agentic RAG AI ==="

echo "Step 1: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Step 2: Installing Node.js dependencies..."
cd frontend
npm install

echo "Step 3: Building React frontend..."
npm run build

echo "Step 4: Verifying build..."
if [ ! -d "build" ]; then
    echo "ERROR: Frontend build failed - build directory not found"
    exit 1
fi

echo "=== Build completed successfully! ==="
