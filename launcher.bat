@echo off
title PDFMaster Launcher
color 0B

:menu
cls
echo ============================================
echo          PDFMaster Control Panel
echo ============================================
echo.
echo [1] Start PDFMaster (Background Mode)
echo [2] Start PDFMaster (Console Mode)
echo [3] Stop PDFMaster
echo [4] View Logs
echo [5] Install/Update Dependencies
echo [6] Build Desktop App
echo [7] Exit
echo.
set /p choice=Select option (1-7): 

if "%choice%"=="1" (
    call start.bat
    goto menu
)

if "%choice%"=="2" (
    call start-console.bat
    goto :EOF
)

if "%choice%"=="3" (
    call stop.bat
    goto menu
)

if "%choice%"=="4" (
    call view-logs.bat
    goto menu
)

if "%choice%"=="5" (
    call install.bat
    goto menu
)

if "%choice%"=="6" (
    call build-app.bat
    goto :EOF
)

if "%choice%"=="7" (
    goto :EOF
)

echo Invalid choice!
timeout /t 2 >nul
goto menu
