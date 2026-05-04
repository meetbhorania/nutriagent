#!/bin/bash
# ── NutriAgent Setup Script (Mac / Linux) ─────────────────────────────────
# Run this once after extracting the zip:  bash setup.sh

set -e

echo ""
echo "  ⬡  NutriAgent Setup"
echo "  ─────────────────────────────────────────"
echo ""

# ── 1. Python virtual environment ─────────────────────────────────────────
if [ ! -d "venv" ]; then
  echo "  [1/4] Creating Python virtual environment..."
  python3 -m venv venv
  echo "        ✓ venv created"
else
  echo "  [1/4] Virtual environment already exists, skipping."
fi

# Activate venv
source venv/bin/activate
echo "        ✓ venv activated"

# ── 2. Install Python dependencies ────────────────────────────────────────
echo ""
echo "  [2/4] Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "        ✓ Python deps installed (google-adk, fastapi, uvicorn, etc.)"

# ── 3. Create .env file ────────────────────────────────────────────────────
echo ""
echo "  [3/4] Setting up environment file..."
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "        ✓ .env created from .env.example"
  echo ""
  echo "  ⚠️  ACTION REQUIRED:"
  echo "      Open .env and set your GOOGLE_API_KEY"
  echo "      Get a free key at: https://aistudio.google.com/app/apikey"
else
  echo "        ✓ .env already exists, skipping."
fi

# ── 4. Install frontend dependencies ──────────────────────────────────────
echo ""
echo "  [4/4] Installing frontend (Node) dependencies..."
cd frontend
npm install --silent
cd ..
echo "        ✓ Node deps installed"

# ── Done ──────────────────────────────────────────────────────────────────
echo ""
echo "  ─────────────────────────────────────────"
echo "  ✓ Setup complete!"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Edit .env → paste your GOOGLE_API_KEY"
echo ""
echo "  2. Start the backend (Terminal 1):"
echo "     source venv/bin/activate"
echo "     source .env && uvicorn health_food_agent.agent:app --reload --port 8000"
echo ""
echo "  3. Start the frontend (Terminal 2):"
echo "     cd frontend && npm run dev"
echo ""
echo "  4. Open http://localhost:3000"
echo ""
echo "  ─────────────────────────────────────────"
echo "  TIP: Run 'source .env && adk web' instead of uvicorn"
echo "       to get the full ADK visual agent inspector UI."
echo ""
