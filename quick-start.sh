#!/bin/bash

# RAG Chatbot Quick Start Script
# This script will help you get up and running quickly

set -e

echo "🚀 RAG Chatbot Quick Start"
echo "=========================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip are available"
echo ""

# Navigate to server directory
cd server

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment configuration..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Environment file created from template"
        echo "⚠️  Please edit .env file with your actual API keys and configuration"
    else
        echo "⚠️  No env.example found. Please create .env file manually."
    fi
else
    echo "✅ Environment file already exists"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Edit the .env file with your API keys and configuration"
echo "2. Place your documents in the server/data/ directory"
echo "3. Start the server: uvicorn app.main:app --reload --port 8000"
echo "4. Ingest documents: python -c \"from app.ingest import ingest_folder; print(ingest_folder('./data'))\""
echo "5. Test the API: curl http://localhost:8000/health"
echo ""
echo "📖 For detailed instructions, see server/README.md"
echo "🌐 API documentation will be available at http://localhost:8000/docs"
echo ""
echo "Happy building! 🚀"
