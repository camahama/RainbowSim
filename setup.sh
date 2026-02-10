#!/bin/bash

# RainbowSim Web App Setup Script
# This script automates the build and deployment setup

set -e

echo "================================"
echo "RainbowSim - Build Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Navigate to rainbow_web directory
cd "$(dirname "$0")/rainbow_web"
echo "Working in: $(pwd)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "📦 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate venv: source rainbow_web/venv/bin/activate"
echo "  2. Run locally: python rainbow_web/main.py"
echo "  3. Build for web: pygbag rainbow_web/main.py --build web"
echo ""
echo "For deployment instructions, see: BUILD_INSTRUCTIONS.md"
