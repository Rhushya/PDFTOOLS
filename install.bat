@echo off
title PDFMaster - Installation
color 0B

echo ============================================
echo   PDFMaster - Automated Installation
echo ============================================
echo.

:: Check if conda is installed
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Conda is not installed!
    echo.
    echo Would you like to install Miniconda? (Y/N)
    set /p install_conda=
    
    if /i "%install_conda%"=="Y" (
        echo.
        echo [1/5] Downloading Miniconda installer...
        curl -o miniconda_installer.exe https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
        
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to download Miniconda
            echo Please download manually from: https://docs.conda.io/en/latest/miniconda.html
            pause
            exit /b 1
        )
        
        echo.
        echo [2/5] Installing Miniconda...
        echo Please follow the installer prompts...
        start /wait miniconda_installer.exe /InstallationType=JustMe /RegisterPython=1 /S /D=%UserProfile%\Miniconda3
        
        del miniconda_installer.exe
        
        echo.
        echo [INFO] Conda installed. Please restart this script.
        echo Close this window and run install.bat again.
        pause
        exit /b 0
    ) else (
        echo.
        echo [ERROR] Conda is required for PDFMaster
        echo Please install from: https://docs.conda.io/en/latest/miniconda.html
        pause
        exit /b 1
    )
)

echo [1/4] Conda detected!
echo.

:: Initialize conda for current session
call conda init cmd.exe >nul 2>nul
call "%UserProfile%\Miniconda3\Scripts\activate.bat" 2>nul

echo [2/4] Creating/updating conda environment 'pdfmaster'...
call conda create -n pdfmaster python=3.12 -y
if %errorlevel% neq 0 (
    echo [INFO] Environment already exists, updating...
)

echo.
echo [3/4] Installing backend dependencies in conda environment...
call conda activate pdfmaster
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed
)
cd ..

echo.
echo [4/4] Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies
    echo Make sure Node.js is installed: https://nodejs.org
    pause
    exit /b 1
)
cd ..

echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo Conda environment: pdfmaster
echo.
echo To start PDFMaster, run: start.bat
echo.
pause
