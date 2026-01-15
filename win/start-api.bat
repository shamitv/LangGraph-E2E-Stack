@echo off
REM Start backend dev server (Uvicorn)
REM This script looks for a virtualenv in backend\venv or repo root \venv.

REM Resolve repo root and backend paths (script dir is win\)
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "BACKEND_DIR=%REPO_ROOT%\backend"

cd /d "%BACKEND_DIR%"

REM Activate virtualenv if present in backend or repo root
if exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
  call "%BACKEND_DIR%\venv\Scripts\activate.bat"
) else if exist "%REPO_ROOT%\venv\Scripts\activate.bat" (
  call "%REPO_ROOT%\venv\Scripts\activate.bat"
) else (
  echo No virtualenv activation script found in backend\venv or repo root\venv.
  echo Ensure Python environment is activated or install dependencies manually.
)

REM Install requirements if needed (uncomment to enable)
REM call pip install -r requirements.txt

REM Run uvicorn using the active Python interpreter (works when venv is activated)
python -m uvicorn agent_demo_framework.main:app --reload --host 0.0.0.0 --port 8000

REM Pause so console remains open after server stops
pause