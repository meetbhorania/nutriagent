@echo off
REM ── NutriAgent Setup Script (Windows) ─────────────────────────────────
REM Run this once after extracting the zip:  setup.bat

echo.
echo   ^⬡  NutriAgent Setup
echo   ─────────────────────────────────────────
echo.

REM ── 1. Python virtual environment ─────────────────────────────────────
if not exist "venv" (
    echo   [1/4] Creating Python virtual environment...
    python -m venv venv
    echo         ^✓ venv created
) else (
    echo   [1/4] Virtual environment already exists, skipping.
)

call venv\Scripts\activate
echo         ^✓ venv activated

REM ── 2. Install Python deps ──────────────────────────────────────────────
echo.
echo   [2/4] Installing Python dependencies...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo         ^✓ Python deps installed

REM ── 3. .env file ───────────────────────────────────────────────────────
echo.
echo   [3/4] Setting up environment file...
if not exist ".env" (
    copy .env.example .env >nul
    echo         ^✓ .env created from .env.example
    echo.
    echo   ^⚠  ACTION REQUIRED:
    echo       Open .env and set your GOOGLE_API_KEY
    echo       Get a free key at: https://aistudio.google.com/app/apikey
) else (
    echo         ^✓ .env already exists, skipping.
)

REM ── 4. Frontend deps ───────────────────────────────────────────────────
echo.
echo   [4/4] Installing frontend dependencies...
cd frontend
npm install --silent
cd ..
echo         ^✓ Node deps installed

REM ── Done ───────────────────────────────────────────────────────────────
echo.
echo   ─────────────────────────────────────────
echo   ^✓ Setup complete!
echo.
echo   Next steps:
echo.
echo   1. Edit .env and paste your GOOGLE_API_KEY
echo.
echo   2. Backend (Terminal 1):
echo      venv\Scripts\activate
echo      uvicorn health_food_agent.agent:app --reload --port 8000
echo.
echo   3. Frontend (Terminal 2):
echo      cd frontend ^&^& npm run dev
echo.
echo   4. Open http://localhost:3000
echo   ─────────────────────────────────────────
echo.
pause
