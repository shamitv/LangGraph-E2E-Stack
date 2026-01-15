@echo off
REM Start frontend dev server (Vite)
REM Runs from repository root's frontend folder
set "SCRIPT_DIR=%~dp0"
set "FRONTEND_DIR=%SCRIPT_DIR%..\frontend"

cd /d "%FRONTEND_DIR%"

REM Ensure node modules are installed if needed (uncomment to enable)
REM call npm install

REM Start Vite dev server
call npm run dev

REM Pause so console remains open after the dev server stops
pause