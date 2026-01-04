@echo off
title PDFMaster - Stop Servers

echo Stopping PDFMaster servers...

:: Kill Python processes (backend)
taskkill /F /IM python.exe /T >nul 2>nul

:: Kill Node processes (frontend)
taskkill /F /IM node.exe /T >nul 2>nul

:: Kill any leftover processes on ports 5000 and 5173
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do taskkill /F /PID %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /F /PID %%a >nul 2>nul

echo.
echo PDFMaster servers stopped.
timeout /t 2 >nul
