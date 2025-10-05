@echo off
chcp 65001 >nul
echo ========================================
echo   AI Soul Companion - Backend
echo ========================================
echo.

cd /d "%~dp0"

REM Create virtual environment
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [3/4] Installing dependencies...
pip install -q -r requirements.txt

REM Copy .env if not exists
if not exist ".env" (
    echo [4/4] Creating .env file...
    copy .env.example .env >nul
)

echo.
echo ========================================
echo   Starting FastAPI Server
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
