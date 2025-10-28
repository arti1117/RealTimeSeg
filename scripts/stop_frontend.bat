@echo off
echo.
echo 🛑 Stopping Frontend Server...
echo.

REM Find and kill process using port 8080
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do (
    echo Found process: %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo ❌ Failed to stop server
    ) else (
        echo ✅ Frontend server stopped successfully
        echo ✓ Port 8080 is now free
    )
    goto :done
)

echo ✓ No frontend server running on port 8080

:done
echo.
pause
