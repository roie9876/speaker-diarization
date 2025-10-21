#!/bin/bash

# Speaker Diarization Project - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🎯 Speaker Diarization Project Setup"
echo "===================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Check for required Python version (3.10+)
required_version="3.10"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ Python 3.10+ is required. Please upgrade Python."
    exit 1
fi

# Create virtual environment
echo ""
echo "🔨 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
echo "   (This may take several minutes for first-time setup)"
pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed"

# Check for .env file
echo ""
echo "🔐 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - AZURE_SPEECH_KEY"
    echo "   - HUGGING_FACE_HUB_TOKEN"
else
    echo "✓ .env file exists"
fi

# Verify PyTorch installation
echo ""
echo "🧪 Verifying PyTorch installation..."
python3 -c "import torch; print(f'✓ PyTorch {torch.__version__} installed')"

# Check for GPU support
echo ""
echo "🎮 Checking GPU support..."
if python3 -c "import torch; exit(0 if torch.backends.mps.is_available() else 1)" 2>/dev/null; then
    echo "✓ MPS (Metal Performance Shaders) available - GPU acceleration enabled!"
elif python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
    echo "✓ CUDA available - GPU acceleration enabled!"
else
    echo "⚠️  No GPU detected - will use CPU (slower but functional)"
fi

# Create necessary directories
echo ""
echo "📁 Verifying directory structure..."
mkdir -p data/profiles data/results data/temp logs tests/fixtures
echo "✓ Directory structure verified"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Accept pyannote.audio agreements on Hugging Face:"
echo "      - https://huggingface.co/pyannote/speaker-diarization-3.1"
echo "      - https://huggingface.co/pyannote/segmentation-3.0"
echo "   3. Run the application: streamlit run src/ui/app.py"
echo ""
echo "📚 Documentation: See docs/ directory"
echo "🤖 GitHub Copilot: Instructions in .github/copilot-instructions.md"
echo ""
