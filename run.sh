#!/bin/bash

# LLM Classifier Testing Framework - Startup Script

echo "🚀 Starting LLM Classifier Testing Framework..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Start Streamlit app
echo ""
echo "✅ Setup complete! Starting the app..."
echo "📊 The app will open in your browser at http://localhost:8501"
echo ""

streamlit run Home.py
