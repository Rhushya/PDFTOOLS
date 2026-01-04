@echo off
setlocal EnableDelayedExpansion

:: Set project paths
set PROJECT_DIR=%~dp0
set BACKEND_DIR=%PROJECT_DIR%backend
set FRONTEND_DIR=%PROJECT_DIR%frontend
set LOG_DIR=%PROJECT_DIR%logs
set CONDA_ENV=pdfmaster

:: Create logs directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Check if conda is available
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Conda not found! Running installation...
    call install.bat
    exit /b
)

:: Initialize conda
call conda init cmd.exe >nul 2>nul
if exist "%UserProfile%\Miniconda3\Scripts\activate.bat" (
    call "%UserProfile%\Miniconda3\Scripts\activate.bat"
) else if exist "%UserProfile%\Anaconda3\Scripts\activate.bat" (
    call "%UserProfile%\Anaconda3\Scripts\activate.bat"
)

:: Check if conda environment exists
conda env list | findstr /C:"%CONDA_ENV%" >nul 2>nul
if %errorlevel% neq 0 (
    echo Conda environment '%CONDA_ENV%' not found!
    echo Running installation...
    call install.bat
    exit /b
)

:: Create VBS script to run backend silently
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\start_backend.vbs"
echo WshShell.Run "cmd /c cd /d ""%BACKEND_DIR%"" && call conda activate %CONDA_ENV% && python app.py > ""%LOG_DIR%\backend.log"" 2>&1", 0, False >> "%TEMP%\start_backend.vbs"

:: Create VBS script to run frontend silently
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\start_frontend.vbs"
echo WshShell.Run "cmd /c cd /d ""%FRONTEND_DIR%"" && npm run dev > ""%LOG_DIR%\frontend.log"" 2>&1", 0, False >> "%TEMP%\start_frontend.vbs"

:: Start backend silently
cscript //nologo "%TEMP%\start_backend.vbs"

:: Wait for backend
timeout /t 3 /nobreak >nul

:: Start frontend silently
cscript //nologo "%TEMP%\start_frontend.vbs"

:: Wait a bit more
timeout /t 2 /nobreak >nul

:: Open browser
start http://localhost:5173

:: Show tray notification
powershell -WindowStyle Hidden -Command "Add-Type -AssemblyName System.Windows.Forms; $notification = New-Object System.Windows.Forms.NotifyIcon; $notification.Icon = [System.Drawing.SystemIcons]::Information; $notification.Visible = $true; $notification.BalloonTipTitle = 'PDFMaster Started'; $notification.BalloonTipText = 'Backend: http://localhost:5000`nFrontend: http://localhost:5173'; $notification.ShowBalloonTip(5000); Start-Sleep -Seconds 5; $notification.Dispose()"

:: Clean up temp files
del "%TEMP%\start_backend.vbs" 2>nul
del "%TEMP%\start_frontend.vbs" 2>nul
