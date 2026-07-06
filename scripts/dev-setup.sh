#!/bin/bash
set -e

echo "🎵 Somancer Studio — Development Setup"
echo "========================================="

# Check for required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 not found. Please install $1 first."
        exit 1
    fi
}

echo "Checking prerequisites..."
check_command node
check_command python3.11
check_command git

# Install pnpm if not present
if ! command -v pnpm &> /dev/null; then
    echo "📦 Installing pnpm..."
    npm install -g pnpm
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "   Edit .env to configure your environment"
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
cd packages/backend
python3.11 -m venv venv
source venv/bin/activate || . venv/Scripts/activate  # For Git Bash on Windows
pip install -e ".[dev]"
deactivate
cd ../..

# Install Node dependencies
echo "📦 Installing Node dependencies..."
pnpm install

# Setup pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pnpm install husky -D 2>/dev/null || true
npx husky install 2>/dev/null || true
npx husky add .husky/pre-commit "pnpm lint-staged" 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start backend: cd packages/backend && source venv/bin/activate && uvicorn aimusic.main:app --reload"
echo "  2. Start frontend: pnpm dev:desktop"
echo "  3. Or start full stack: docker-compose up -d"
echo ""
echo "For more info, see docs/SETUP.md"
