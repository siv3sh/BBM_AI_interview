#!/bin/bash

# PlacementHelper Setup Script
# This script helps you set up the environment for PlacementHelper

echo "🚀 PlacementHelper Environment Setup"
echo "=================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env_template.txt .env
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your API keys:"
    echo "   - GROQ_API_KEY: Get from https://console.groq.com/keys"
    echo "   - GOOGLE_API_KEY: Get from https://aistudio.google.com/app/apikey"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Check Python dependencies
echo "🔍 Checking Python dependencies..."
python -c "
import sys
required_packages = [
    'streamlit', 'pandas', 'plotly', 'numpy', 
    'langchain', 'chromadb', 'torch'
]
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'❌ Missing packages: {missing}')
    print('Run: pip install -r requirements.txt')
else:
    print('✅ All required packages are installed')
"

# Check API keys
echo ""
echo "🔑 Checking API keys..."
python env_config.py

echo ""
echo "🎯 Setup Complete!"
echo "=================="
echo "To start the application:"
echo "  streamlit run home.py"
echo ""
echo "To access the app:"
echo "  http://localhost:8501"
echo ""
echo "📚 For more information, see README.md"
