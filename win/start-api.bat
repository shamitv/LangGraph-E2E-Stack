@echo off
REM Start backend dev server (Uvicorn)
REM Runs from repository root's backend folder
cd /d %~dp0\..\backend
REM Activate virtualenv if present
if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
) else (
  echo No virtualenv activation script found. Ensure Python env is activated.
)
REM Install requirements if needed (uncomment to enable)




pauseuvicorn app.main:app --reload --host 0.0.0.0 --port 8000REM Run uvicorn (adjust module:path if different):: call pip install -r requirements.txt