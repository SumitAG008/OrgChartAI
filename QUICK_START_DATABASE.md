# 🚀 Quick Start: Database Setup & SuccessFactors Sync

## ⚡ TL;DR - 3 Steps

1. **Create Tables** → Run SQL in Neon Console
2. **Start Services** → HRIS Service + Org Service
3. **Sync Data** → Connect SuccessFactors & Sync

---

## Step 1: Create Database Tables (5 minutes)

### **In Neon Console:**

1. Go to: https://console.neon.tech
2. Select database: **neondb**
3. Click: **SQL Editor**
4. **Copy & Paste** `database/schema.sql` → Click **Run** ✅
5. **Copy & Paste** `database/functional_chart_schema.sql` → Click **Run** ✅

**Verify:**
```sql
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('position', 'employee', 'org_unit', 'function_category');
```
**Expected:** Should return `4` (or more)

---

## Step 2: Start Services (2 minutes)

### **Terminal 1: HRIS Service**
```powershell
cd backend\hris-service
uvicorn main:app --reload --port 8002
```

### **Terminal 2: Org Service**
```powershell
cd backend\org-service
uvicorn main:app --reload --port 8000
```

### **Terminal 3: Frontend**
```powershell
cd frontend
npm run dev
```

**Verify:**
- ✅ http://localhost:8002/docs (HRIS Service API)
- ✅ http://localhost:8000/docs (Org Service API)
- ✅ http://localhost:5173 (Frontend)

---

## Step 3: Sync SuccessFactors Data (10 minutes)

### **Option A: Via Frontend UI**

1. Open: http://localhost:5173
2. Click: **"HRIS Connections"** in sidebar
3. Click: **"Add New Connection"**
4. Fill form:
   - **Name**: "Production SuccessFactors"
   - **Type**: "SuccessFactors"
   - **Company ID**: `YOUR_COMPANY_ID`
   - **API URL**: `https://api.successfactors.eu` (or `.com` for US)
   - **Username**: `your_api_user`
   - **Password**: `your_api_password`
5. Click: **"Test Connection"** → Should show ✅
6. Click: **"Save Connection"**
7. Click: **"Start Sync"** → Wait for completion

### **Option B: Via API**

```bash
# 1. Test connection
curl -X POST http://localhost:8002/api/v1/hris/successfactors/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "YOUR_COMPANY_ID",
    "username": "api_user",
    "password": "api_password",
    "api_url": "https://api.successfactors.eu"
  }'

# 2. Start sync
curl -X POST http://localhost:8002/api/v1/hris/sync/start \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "connection-uuid-from-step-1",
    "sync_type": "full",
    "entities": ["employees", "positions", "org_units"]
  }'
```

---

## ✅ Verify Everything Works

### **Check Database Has Data:**
```sql
-- In Neon Console SQL Editor
SELECT COUNT(*) as employees FROM employee;
SELECT COUNT(*) as positions FROM position;
SELECT COUNT(*) as org_units FROM org_unit;
```

**Expected:** Numbers > 0 if sync worked

### **Check Org Chart API:**
```bash
curl http://localhost:8000/api/v1/org-chart
```

**Expected:** JSON with org chart tree structure

### **Check Frontend:**
1. Open: http://localhost:5173
2. Click: **"Org Chart"** in sidebar
3. **Expected:** Org chart displays with your SuccessFactors data!

---

## 🗄️ Database Tables Location

### **PostgreSQL (Neon)**
- **Database**: `neondb`
- **Schema**: `public`
- **Tables**: 
  - `org_unit`, `position`, `employee`, `job`
  - `function_category`, `function`, `accountability`
  - `location`, `cost_center`, `legal_entity`

### **Neo4j (Optional)**
- **Status**: Not configured (optional for advanced queries)
- **Use Case**: Complex relationship queries, pathfinding
- **Setup**: See `DATABASE_AND_SYNC_SETUP.md` Step 7

---

## 🔄 Data Flow

```
SuccessFactors (HRIS)
    ↓ OData API
HRIS Service (Port 8002)
    ↓ Transform & Validate
Org Service (Port 8000)
    ↓ Store
PostgreSQL (Neon)
    ↓ Query
Frontend (React)
    ↓ Display
Org Chart Visualization
```

---

## 🐛 Common Issues

### **"relation does not exist"**
→ **Fix**: Run Step 1 (create tables)

### **"Connection failed"**
→ **Fix**: Check SuccessFactors credentials and API URL

### **"No data in org chart"**
→ **Fix**: 
1. Check sync completed: `SELECT COUNT(*) FROM position;`
2. Restart Org Service
3. Refresh frontend

### **"500 Internal Server Error"**
→ **Fix**: Check service logs for specific error

---

## 📚 Full Documentation

- **Complete Guide**: `DATABASE_AND_SYNC_SETUP.md`
- **SuccessFactors Details**: `SUCCESSFACTORS_INTEGRATION_GUIDE.md`
- **Database Schema**: `database/schema.sql`
- **Functional Chart**: `database/functional_chart_schema.sql`

---

## 🎯 Next Steps After Setup

1. ✅ **Schedule Automatic Syncs** (daily at 2 AM)
2. ✅ **Explore 26+ Org Chart Layouts**
3. ✅ **Use Functional Chart** for accountability mapping
4. ✅ **Try AI Org Generator** for recommendations

---

**Need Help?** Check the full guide: `DATABASE_AND_SYNC_SETUP.md`
