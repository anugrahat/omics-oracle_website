#!/bin/bash
# 🚀 Quick deploy script for Omics Oracle web interface

echo "🧬 Omics Oracle - Deployment Setup"
echo "==================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this from the website/ directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd .. && pip install -r requirements.txt
pip install -r website/requirements.txt

# Launch Streamlit
echo "🌐 Launching Streamlit web interface..."
echo "📍 Opening at http://localhost:8501"
echo "🔑 Don't forget to add your OpenAI API key in the sidebar!"
echo ""

cd website && streamlit run app.py
