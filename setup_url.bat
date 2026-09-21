@echo off
:: Self-elevate to admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process 'cmd.exe' -ArgumentList '/c copy /Y \"c:\Create project\hosts_backup.txt\" \"C:\Windows\System32\drivers\etc\hosts\"' -Verb RunAs -Wait"
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Could not get admin rights. Please run this manually:
        echo   1. Open Command Prompt as Administrator
        echo   2. Run: copy /Y "c:\Create project\hosts_backup.txt" "C:\Windows\System32\drivers\etc\hosts"
        pause
        exit /b 1
    )
    echo.
    echo =============================================
    echo    SUCCESS! Hosts mapping has been set up.
    echo.
    echo    RECOMMENDED URL (For Camera ^& Mic):
    echo    http://localhost:5000
    echo.
    echo    CUSTOM URL:
    echo    http://aismartinterviewer:5000
    echo.
    echo    NOTE: Chrome ^& Edge require localhost or HTTPS
    echo    for camera and microphone permissions.
    echo =============================================
    echo.
    pause
    exit /b
)

:: If already admin, copy directly
copy /Y "c:\Create project\hosts_backup.txt" "C:\Windows\System32\drivers\etc\hosts"
echo.
echo =============================================
echo    SUCCESS! Hosts mapping has been set up.
echo.
echo    RECOMMENDED URL (For Camera ^& Mic):
echo    http://localhost:5000
echo.
echo    CUSTOM URL:
echo    http://aismartinterviewer:5000
echo.
echo    NOTE: Chrome ^& Edge require localhost or HTTPS
echo    for camera and microphone permissions.
echo =============================================
echo.
pause
