@echo off
title PDFMaster - Console Mode
color 0A

echo ============================================
echo   PDFMaster - Console Mode
echo ============================================
echo.

:: Set project paths
set PROJECT_DIR=%~dp0
set BACKEND_DIR=%PROJECT_DIR%backend
set FRONTEND_DIR=%PROJECT_DIR%frontend
set CONDA_ENV=pdfmaster

:: Check if conda is available
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Conda not found! Please run: install.bat
    pause
    exit /b 1
)

:: Initialize conda
call conda init cmd.exe >nul 2>nul
if exist "%UserProfile%\Miniconda3\Scripts\activate.bat" (
    call "%UserProfile%\Miniconda3\Scripts\activate.bat"
) else if exist "%UserProfile%\Anaconda3\Scripts\activate.bat" (
    call "%UserProfile%\Anaconda3\Scripts\activate.bat"
)

echo [1/2] Starting Backend Server (Conda: %CONDA_ENV%)...
start "PDFMaster Backend" cmd /k "cd /d "%BACKEND_DIR%" && call conda activate %CONDA_ENV% && echo. && echo ======================================== && echo   PDFMaster Backend Server && echo ======================================== && echo. && python app.py"

:: Wait for backend
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server...
start "PDFMaster Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && echo. && echo ======================================== && echo   PDFMaster Frontend Server && echo ======================================== && echo. && npm run dev"

echo.
echo ============================================
echo   Servers Started!
echo ============================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:5173
echo.
echo   Check the opened console windows for logs.
echo   Close this window when done.
echo ============================================

pause
