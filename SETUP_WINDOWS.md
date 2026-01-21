# Windows Setup Guide - OrgChartAI

## 🪟 Windows-Specific Setup Instructions

---

## 📋 Prerequisites

1. **Python 3.11+** - Download from [python.org](https://www.python.org/downloads/)
2. **Node.js 18+** - Download from [nodejs.org](https://nodejs.org/)
3. **PostgreSQL Client** - Or use psql from PostgreSQL installation
4. **Git** - For cloning repository

---

## 🚀 Backend Setup (Windows)

### **Option 1: Command Prompt (CMD)**

**From project root:**
```cmd
cd backend\org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
uvicorn main:app --reload --port 8000
```

**Note:** For AI service, also install AI dependencies:
```cmd
pip install -r ..\requirements-ai.txt
```

**If already in backend directory:**
```cmd
cd org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements.txt
uvicorn main:app --reload --port 8000
```

### **Option 2: PowerShell**

```powershell
cd backend\org-service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
uvicorn main:app --reload --port 8000
```

**Note:** If you get an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Option 3: Git Bash**

```bash
cd backend/org-service
python -m venv venv
source venv/Scripts/activate
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 🤖 AI Service Setup (Windows)

### **Command Prompt (CMD)**

```cmd
cd backend\ai-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements.txt
uvicorn main:app --reload --port 8001
```

### **PowerShell**

```powershell
cd backend\ai-service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
uvicorn main:app --reload --port 8001
```

---

## 🎨 Frontend Setup (Windows)

### **Command Prompt or PowerShell**

```cmd
cd frontend
npm install
npm run dev
```

---

## 🗄️ Database Setup (Windows)

### **Using psql (Command Prompt or PowerShell)**

```cmd
cd database
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f schema.sql
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f triggers.sql
```

### **Using pgAdmin**

1. Open pgAdmin
2. Connect to your database
3. Open Query Tool
4. Copy contents of `schema.sql` and execute
5. Copy contents of `triggers.sql` and execute

---

## 📝 Quick Start Scripts

### **start-backend.bat** (Command Prompt)

Create `start-backend.bat` in project root:

```batch
@echo off
echo Starting Org Service...
cd backend\org-service
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r ..\requirements.txt
uvicorn main:app --reload --port 8000
pause
```

### **start-ai-service.bat** (Command Prompt)

Create `start-ai-service.bat` in project root:

```batch
@echo off
echo Starting AI Service...
cd backend\ai-service
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r ..\requirements.txt
uvicorn main:app --reload --port 8001
pause
```

### **start-frontend.bat** (Command Prompt)

Create `start-frontend.bat` in project root:

```batch
@echo off
echo Starting Frontend...
cd frontend
if not exist node_modules (
    npm install
)
npm run dev
pause
```

### **start-all.ps1** (PowerShell)**

Create `start-all.ps1` in project root:

```powershell
# Start all services
Write-Host "Starting OrgChartAI Services..." -ForegroundColor Green

# Start Org Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend\org-service; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r ..\requirements.txt; uvicorn main:app --reload --port 8000"

# Wait a bit
Start-Sleep -Seconds 2

# Start AI Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend\ai-service; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r ..\requirements.txt; uvicorn main:app --reload --port 8001"

# Wait a bit
Start-Sleep -Seconds 2

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm install; npm run dev"

Write-Host "All services started!" -ForegroundColor Green
Write-Host "Org Service: http://localhost:8000" -ForegroundColor Cyan
Write-Host "AI Service: http://localhost:8001" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
```

---

## 🔧 Troubleshooting

### **Python not found**

```cmd
# Check Python installation
python --version

# If not found, add Python to PATH or use full path:
C:\Python311\python.exe -m venv venv
```

### **PowerShell Execution Policy**

```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Virtual Environment Issues**

```cmd
# Delete and recreate venv
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
```

### **Port Already in Use**

```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### **Module Not Found**

```cmd
# Make sure you're in the correct directory
cd backend\org-service

# Activate venv
venv\Scripts\activate

# Install requirements
pip install -r ..\requirements.txt
```

---

## 📂 Directory Structure (Windows)

```
OrgChartAI\
├── backend\
│   ├── org-service\
│   │   ├── venv\              # Virtual environment
│   │   ├── main.py
│   │   └── app\
│   ├── ai-service\
│   │   ├── venv\              # Virtual environment
│   │   ├── main.py
│   │   └── app\
│   └── requirements.txt
├── frontend\
│   ├── node_modules\
│   ├── src\
│   └── package.json
├── database\
│   ├── schema.sql
│   └── triggers.sql
└── docs\
```

---

## ✅ Verification

### **Check Services**

1. **Org Service**: http://localhost:8000/docs
2. **AI Service**: http://localhost:8001/docs
3. **Frontend**: http://localhost:3000

### **Test Endpoints**

```cmd
# Test Org Service
curl http://localhost:8000/health

# Test AI Service
curl http://localhost:8001/health
```

---

## 🎯 Quick Reference

| Task | Command Prompt | PowerShell |
|------|---------------|------------|
| Create venv | `python -m venv venv` | `python -m venv venv` |
| Activate venv | `venv\Scripts\activate` | `.\venv\Scripts\Activate.ps1` |
| Install deps | `pip install -r ..\requirements.txt` | `pip install -r ..\requirements.txt` |
| Run service | `uvicorn main:app --reload --port 8000` | `uvicorn main:app --reload --port 8000` |
| Deactivate | `deactivate` | `deactivate` |

---

**Windows setup complete!** 🪟✅
