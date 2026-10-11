@echo off
echo ==============================================================
echo  Starting The Lenny Growth Assistant
echo ==============================================================

:: Check if MySQL is running on port 3306
netstat -ano | findstr 3306 >nul
if %errorlevel% neq 0 (
    echo [WARNING] MySQL is not detected on port 3306.
    echo Attempting to start XAMPP MySQL...
    if exist C:\xampp\mysql_start.bat (
        start /b "" C:\xampp\mysql_start.bat
        timeout /t 3 >nul
    ) else (
        echo Please make sure your XAMPP MySQL service is running.
    )
)

echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Lenny Assistant - Backend" cmd /k ".\venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting Vite Frontend on http://localhost:5173 ...
cd frontend
start "Lenny Assistant - Frontend" cmd /k "npm run dev"

echo.
echo Application started!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://127.0.0.1:8000/docs
echo ==============================================================
