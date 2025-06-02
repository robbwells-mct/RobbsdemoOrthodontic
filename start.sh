#!/bin/bash

# Robb's Demo - Orthodontics Practice Management System - Quick Start Script
# This script helps developers quickly set up and run the demonstration application

echo "🦷 Robb's Demo - Orthodontics Practice Management System - Quick Start"
echo "===================================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "Please run this script from the project directory"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if python3 -m pip install -r requirements.txt; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if orthodontics_app.py exists
if [ ! -f "orthodontics_app.py" ]; then
    echo "❌ Error: orthodontics_app.py not found"
    echo "Please run this script from the project directory"
    exit 1
fi

# Ask about sample data
echo ""
read -p "❓ Would you like to create sample data for testing? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 Running setup script to create sample data..."
    python3 setup.py
else
    # Ask about starting the application
    echo ""
    read -p "❓ Would you like to start the application now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🚀 Starting the application..."
        echo "Application will be available at: http://localhost:5001"
        echo "Press Ctrl+C to stop the application"
        echo "--------------------------------------------------"
        python3 orthodontics_app.py
    else
        echo ""
        echo "✅ Setup complete!"
        echo "To start the application, run: python3 orthodontics_app.py"
        echo "Then visit: http://localhost:5001"
    fi
fi
