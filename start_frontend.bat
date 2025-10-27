@echo off
echo.
echo 🌐 Starting Local Frontend Server...
echo.
echo Frontend will be available at: http://localhost:8080
echo.
echo Setup:
echo 1. Start this frontend server (running now)
echo 2. Start backend in Google Colab
echo 3. Copy ngrok URL from Colab
echo 4. Paste ngrok URL in the 'Backend Server URL' field
echo 5. Click Connect!
echo.
echo Press Ctrl+C to stop the server
echo ================================
echo.

cd frontend
python -m http.server 8080
