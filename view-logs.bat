@echo off
title PDFMaster - View Logs

echo ============================================
echo   PDFMaster Server Logs
echo ============================================
echo.
echo [1] View Backend Log
echo [2] View Frontend Log
echo [3] View Both Logs
echo [4] Clear Logs
echo [5] Exit
echo.
set /p choice=Select option (1-5): 

if "%choice%"=="1" (
    if exist logs\backend.log (
        type logs\backend.log
        echo.
        echo --- End of Backend Log ---
        pause
    ) else (
        echo Backend log not found!
        pause
    )
    goto :EOF
)

if "%choice%"=="2" (
    if exist logs\frontend.log (
        type logs\frontend.log
        echo.
        echo --- End of Frontend Log ---
        pause
    ) else (
        echo Frontend log not found!
        pause
    )
    goto :EOF
)

if "%choice%"=="3" (
    echo.
    echo ========== BACKEND LOG ==========
    if exist logs\backend.log (
        type logs\backend.log
    ) else (
        echo Backend log not found!
    )
    echo.
    echo ========== FRONTEND LOG ==========
    if exist logs\frontend.log (
        type logs\frontend.log
    ) else (
        echo Frontend log not found!
    )
    echo.
    pause
    goto :EOF
)

if "%choice%"=="4" (
    del logs\backend.log 2>nul
    del logs\frontend.log 2>nul
    echo Logs cleared!
    timeout /t 2 >nul
    goto :EOF
)

if "%choice%"=="5" (
    goto :EOF
)

echo Invalid choice!
pause
