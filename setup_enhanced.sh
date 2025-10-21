#!/bin/bash

# Enhanced Setup Script for Speaker Diarization System
# Handles macOS-specific issues and provides better error handling

set -e  # Exit on error

echo "🎤 Speaker Diarization System - Enhanced Setup"
echo "================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo ""
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (meets requirement: $REQUIRED_VERSION+)"
else
    echo -e "${RED}✗${NC} Python 3.10+ required, found: $PYTHON_VERSION"
    exit 1
fi

# macOS specific: Check and install portaudio
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "🍎 macOS detected - checking portaudio..."
    
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}⚠${NC}  Homebrew not found"
        echo "   Please install Homebrew from: https://brew.sh"
        echo "   Then run: brew install portaudio"
        echo ""
        read -p "   Continue without portaudio? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        if brew list portaudio &>/dev/null; then
            echo -e "${GREEN}✓${NC} portaudio already installed"
        else
            echo "   Installing portaudio via Homebrew..."
            brew install portaudio
            echo -e "${GREEN}✓${NC} portaudio installed"
        fi
    fi
fi

# Create or update virtual environment
echo ""
echo "🔧 Setting up virtual environment..."

if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC}  Virtual environment exists"
    read -p "   Recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Removing old virtual environment..."
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Virtual environment recreated"
    else
        echo "   Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip, setuptools, wheel
echo ""
echo "📦 Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel --quiet
echo -e "${GREEN}✓${NC} Core tools upgraded"

# Install requirements
echo ""
echo "📦 Installing Python packages (this may take several minutes)..."
echo "   Tip: Get coffee ☕ - this installs PyTorch, pyannote, and 30+ dependencies"
echo ""

if pip install -r requirements.txt; then
    echo ""
    echo -e "${GREEN}✓${NC} All packages installed successfully!"
else
    echo ""
    echo -e "${RED}✗${NC} Package installation failed"
    echo ""
    echo "Common fixes:"
    echo "  1. For pyaudio errors: brew install portaudio"
    echo "  2. For torch errors: pip install torch torchvision torchaudio"
    echo "  3. Try installing problematic packages individually"
    exit 1
fi

# Create required directories
echo ""
echo "📁 Creating required directories..."
mkdir -p data/profiles
mkdir -p data/results
mkdir -p data/temp
mkdir -p logs
mkdir -p tests/fixtures/audio
mkdir -p tests/fixtures/profiles
echo -e "${GREEN}✓${NC} Directories created"

# Check/create .env file
echo ""
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓${NC} .env file created"
        echo ""
        echo -e "${YELLOW}⚠${NC}  IMPORTANT: Edit .env file with your API keys:"
        echo ""
        echo "   Required keys:"
        echo "   - AZURE_SPEECH_KEY: Your Azure Speech Service key"
        echo "   - AZURE_REGION: Your Azure region (e.g., eastus)"
        echo "   - HUGGING_FACE_HUB_TOKEN: Your HuggingFace token"
        echo ""
        echo "   Get tokens:"
        echo "   - Azure: https://portal.azure.com"
        echo "   - HuggingFace: https://huggingface.co/settings/tokens"
        echo ""
        echo "   Accept model agreements:"
        echo "   - https://huggingface.co/pyannote/speaker-diarization-3.1"
        echo "   - https://huggingface.co/pyannote/segmentation-3.0"
    else
        echo -e "${RED}✗${NC} .env.example not found"
        echo "   Create .env file manually with required keys"
    fi
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Verify PyTorch installation
echo ""
echo "🔍 Verifying PyTorch installation..."
if python3 << END
import torch
import sys

print(f"PyTorch version: {torch.__version__}")

if torch.backends.mps.is_available():
    print("✓ MPS (Apple Silicon GPU) available")
    sys.exit(0)
elif torch.cuda.is_available():
    print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
    sys.exit(0)
else:
    print("ℹ  No GPU available - will use CPU (slower)")
    sys.exit(0)
END
then
    echo -e "${GREEN}✓${NC} PyTorch verified"
else
    echo -e "${YELLOW}⚠${NC}  PyTorch check had issues (may still work)"
fi

# Run verification script
echo ""
echo "🧪 Running installation verification..."
if python3 tests/verify_installation.py; then
    echo ""
    echo "================================================"
    echo -e "${GREEN}✅ Setup Complete!${NC}"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "  1. ${YELLOW}Edit .env file${NC} with your API keys"
    echo "     nano .env"
    echo ""
    echo "  2. ${YELLOW}Activate virtual environment${NC} (in new terminal):"
    echo "     source venv/bin/activate"
    echo ""
    echo "  3. ${YELLOW}Run the application${NC}:"
    echo "     streamlit run src/ui/app.py"
    echo ""
    echo "  4. ${YELLOW}Run tests${NC} (optional):"
    echo "     pytest tests/ -v"
    echo ""
    echo "📖 For more info: see docs/QUICK_START.md"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠${NC}  Setup completed with warnings"
    echo "   See verification output above for details"
    echo "   You may need to configure .env before running"
fi
