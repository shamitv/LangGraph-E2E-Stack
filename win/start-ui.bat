@echo off
REM Start frontend dev server (Vite)
REM Runs from repository root's frontend folder
cd /d %~dp0\..\frontend



pausecall npm run devn:: Ensure node modules installed (uncomment if needed)
:: call npm install