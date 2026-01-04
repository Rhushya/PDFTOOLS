@echo off
title PDFMaster - Development Mode
echo.
echo ============================================
echo   PDFMaster Development Server
echo ============================================
echo.

cd /d "%~dp0"

:: Start backend in a new window
echo Starting Backend Server...
start "PDFMaster Backend" cmd /k "cd backend && python app.py"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend dev server
echo Starting Frontend Dev Server...
cd frontend
call npm run dev

pause
