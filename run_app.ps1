Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host " Starting The Lenny Growth Assistant (PowerShell Launcher)    " -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

# Verify MySQL port 3306
$portCheck = Test-NetConnection -ComputerName localhost -Port 3306 -InformationLevel Quiet
if (-not $portCheck) {
    Write-Warning "MySQL is not responding on localhost:3306."
    if (Test-Path "C:\xampp\mysql_start.bat") {
        Write-Host "Starting XAMPP MySQL..." -ForegroundColor Yellow
        Start-Process "C:\xampp\mysql_start.bat" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    } else {
        Write-Warning "Please start MySQL in XAMPP Control Panel before proceeding."
    }
} else {
    Write-Host "[OK] MySQL is running on port 3306" -ForegroundColor Green
}

# Start Backend
Write-Host "Launching FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

# Start Frontend
Write-Host "Launching Vite Frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "Application launched successfully!" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
