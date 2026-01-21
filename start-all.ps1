# Start All Services - OrgChartAI
# PowerShell Script

Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting OrgChartAI Services" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Function to start service
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$Path,
        [int]$Port
    )
    
    Write-Host "Starting $ServiceName..." -ForegroundColor Cyan
    
    $script = @"
cd '$Path'
if (-not (Test-Path 'venv')) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -q -r ..\requirements.txt
uvicorn main:app --reload --port $Port
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $script
    Start-Sleep -Seconds 2
}

# Start Org Service
Start-Service -ServiceName "Org Service" -Path "backend\org-service" -Port 8000

# Start AI Service
Start-Service -ServiceName "AI Service" -Path "backend\ai-service" -Port 8001

# Wait a bit
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Cyan
$frontendScript = @"
cd 'frontend'
if (-not (Test-Path 'node_modules')) {
    npm install
}
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Org Service:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "             http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "AI Service:   http://localhost:8001" -ForegroundColor Yellow
Write-Host "             http://localhost:8001/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
