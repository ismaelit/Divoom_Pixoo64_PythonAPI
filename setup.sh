#!/bin/bash
# DIVOOM PIXOO 64x64 Controller Setup Script

echo "🚀 DIVOOM PIXOO 64x64 Controller Setup"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Found: $python_version"
else
    echo "❌ Python 3 not found. Please install Python 3.7+"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv pixoo_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source pixoo_env/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if everything is installed correctly
echo "🔍 Verifying installation..."
python -c "import requests, PIL; print('✅ All dependencies installed successfully!')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "To use the PIXOO controller:"
    echo "1. Edit pixoo_controller.py and set your PIXOO IP address"
    echo "2. Run: source pixoo_env/bin/activate"
    echo "3. Run: python pixoo_controller.py"
    echo ""
    echo "Current environment is activated. You can run the controller now!"
else
    echo "❌ Installation verification failed. Please check the error messages above."
    exit 1
fi