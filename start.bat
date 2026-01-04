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
set CONDA_ENV=pdfmaster

echo [1/2] Starting Backend Server...
start "PDFMaster Backend" powershell -NoExit -Command "cd '%BACKEND_DIR%'; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '  PDFMaster Backend Server' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; Write-Host ''; Write-Host 'Activating conda environment: %CONDA_ENV%' -ForegroundColor Yellow; conda activate %CONDA_ENV%; Write-Host 'Starting Flask server on http://localhost:5000' -ForegroundColor Green; Write-Host ''; python app.py"

:: Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend Server...
start "PDFMaster Frontend" powershell -NoExit -Command "cd '%FRONTEND_DIR%'; Write-Host '========================================' -ForegroundColor Magenta; Write-Host '  PDFMaster Frontend Server' -ForegroundColor Magenta; Write-Host '========================================' -ForegroundColor Magenta; Write-Host ''; Write-Host 'Starting Vite dev server...' -ForegroundColor Green; Write-Host ''; npm run dev"

echo.
echo ============================================
echo   Both servers are starting!
echo ============================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:5173
echo.
echo   Close this window or press any key to exit.
echo ============================================

pause > nul
