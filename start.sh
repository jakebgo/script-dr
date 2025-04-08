#!/bin/bash

# Script Doctor Startup Script

echo "Starting Script Doctor application..."

# Check if ChromaDB directory exists
if [ ! -d "./chroma_db" ]; then
    echo "ChromaDB directory not found. Running initial setup..."
    python reingest_framework.py
fi

# Start the application
echo "Starting application server..."
python run.py

echo "Application stopped." 