@echo off
title PDFMaster - Build Desktop App
echo.
echo ============================================
echo   PDFMaster Desktop App Builder
echo ============================================
echo.

cd /d "%~dp0"

:: Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [1/4] Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Installing backend dependencies...
cd ..\backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some backend dependencies may have failed
)

echo.
echo [3/4] Building frontend...
cd ..\frontend
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build frontend
    pause
    exit /b 1
)

echo.
echo [4/4] Building Windows installer...
call npm run electron:build:win
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build Electron app
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo Installer location: frontend\release\
echo.
echo You can find:
echo   - PDFMaster Setup.exe (Installer)
echo   - PDFMaster.exe (Portable)
echo.
pause
