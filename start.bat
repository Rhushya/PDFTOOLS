@echo off
title PDFMaster Launcher
color 0A

echo ============================================
echo        PDFMaster Application Launcher
echo ============================================
echo.

:: Set project paths
set PROJECT_DIR=%~dp0
set BACKEND_DIR=%PROJECT_DIR%backend
set FRONTEND_DIR=%PROJECT_DIR%frontend

echo [1/2] Starting Backend Server...
start "PDFMaster Backend" cmd /k "cd /d "%BACKEND_DIR%" && echo. && echo ======================================== && echo   PDFMaster Backend Server && echo ======================================== && echo. && echo Starting Flask server on http://localhost:5000 && echo. && python app.py"

:: Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend Server...
start "PDFMaster Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && echo. && echo ======================================== && echo   PDFMaster Frontend Server && echo ======================================== && echo. && npm run dev"

echo.
echo ============================================
echo   Both servers are starting!
echo ============================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:5173 or 5175
echo.
echo   Close this window or press any key to exit.
echo ============================================

pause > nul
