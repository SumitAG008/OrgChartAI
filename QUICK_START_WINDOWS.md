# Quick Start - Windows

## 🚀 Fastest Way to Get Started

### **Step 1: Setup Database (One Time)**

From project root:
```cmd
setup-database.bat
```

Or manually:
```cmd
cd database
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f schema.sql
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f triggers.sql
```

### **Step 2: Start Services**

**Option A: Use Batch Files (Easiest)**

Double-click these files from project root:
- `start-backend.bat` - Opens in new window
- `start-ai-service.bat` - Opens in new window  
- `start-frontend.bat` - Opens in new window

**Option B: PowerShell (All at Once)**

From project root:
```powershell
.\start-all.ps1
```

**Option C: Manual Commands**

Open 3 separate Command Prompt windows:

**Window 1 - Org Service (with AI):**
```cmd
cd C:\Users\sumit\Documents\OrgChartAI\backend\org-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
pip install -r ..\requirements-ai.txt
uvicorn main:app --reload --port 8000
```

**Window 2 - AI Service:**
```cmd
cd C:\Users\sumit\Documents\OrgChartAI\backend\ai-service
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements-core.txt
pip install -r ..\requirements-ai.txt
uvicorn main:app --reload --port 8001
```

**Window 3 - Frontend:**
```cmd
cd C:\Users\sumit\Documents\OrgChartAI\frontend
npm install
npm run dev
```

### **Step 3: Access Services**

- **Frontend**: http://localhost:3000
- **Org API**: http://localhost:8000/docs
- **AI API**: http://localhost:8001/docs

---

## 📍 Common Path Issues

### **If you're in `backend` directory:**

```cmd
# Don't do this:
cd backend\org-service  ❌

# Do this instead:
cd org-service  ✅
```

### **If you're in project root:**

```cmd
# This works:
cd backend\org-service  ✅
```

### **Always use full path if unsure:**

```cmd
cd C:\Users\sumit\Documents\OrgChartAI\backend\org-service
```

---

## 🔧 Troubleshooting

### **"The system cannot find the path specified"**

**Solution:** Check your current directory:
```cmd
cd
```

Then navigate correctly:
- If in `backend`: `cd org-service`
- If in project root: `cd backend\org-service`
- Or use full path: `cd C:\Users\sumit\Documents\OrgChartAI\backend\org-service`

### **"Python is not recognized"**

**Solution:** Add Python to PATH or use full path:
```cmd
C:\Python311\python.exe -m venv venv
```

### **"Port already in use"**

**Solution:** Kill the process:
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## ✅ Verification

Test that services are running:

```cmd
# Test Org Service
curl http://localhost:8000/health

# Test AI Service  
curl http://localhost:8001/health
```

Or open in browser:
- http://localhost:8000/docs
- http://localhost:8001/docs

---

**You're all set!** 🎉
