# Complete Database & SuccessFactors Sync Setup Guide

## 📍 Where Are The Tables?

### **PostgreSQL (Neon Database)**

Your tables are **NOT created yet** - that's why you're seeing errors! You need to run the SQL schemas in your Neon database.

**Current Status:**
- ✅ You can see `neon_auth` schema (authentication tables)
- ❌ Missing `public` schema tables (application tables)
- ❌ Missing functional chart tables

**Tables Location:**
- **Schema**: `public` (default schema in PostgreSQL)
- **Database**: `neondb` (your Neon database)
- **Tables to Create**:
  1. Main org chart tables (`schema.sql`)
  2. Functional chart tables (`functional_chart_schema.sql`)

### **Neo4j (Optional - For Advanced Graph Queries)**

Neo4j is **optional** and used for:
- Complex relationship queries
- Org chart pathfinding
- Skill matching
- Scenario planning

**Current Status:** Not configured yet (optional feature)

---

## 🚀 Step 1: Create PostgreSQL Tables

### **Option A: Using Neon Console (Recommended)**

1. **Go to Neon Console**: https://console.neon.tech
2. **Select your database**: `neondb`
3. **Open SQL Editor**
4. **Run Main Schema**:
   - Copy entire contents of `database/schema.sql`
   - Paste into SQL Editor
   - Click **Run** or press `Ctrl+Enter`
5. **Run Functional Chart Schema**:
   - Copy entire contents of `database/functional_chart_schema.sql`
   - Paste into SQL Editor
   - Click **Run**

### **Option B: Using psql Command Line**

```powershell
# Connect to Neon database
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"

# Run main schema
\i database/schema.sql

# Run functional chart schema
\i database/functional_chart_schema.sql
```

### **Option C: Using Batch Script**

```powershell
# From project root
.\setup-database-quick.bat
```

### **Verify Tables Created**

After running schemas, verify in Neon Console:

```sql
-- Check main tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'org_unit', 'position', 'employee', 
    'job', 'location', 'cost_center'
)
ORDER BY table_name;

-- Check functional chart tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'function_category', 'function', 
    'accountability', 'accountability_assignment'
)
ORDER BY table_name;
```

**Expected Result:** You should see all tables listed.

---

## 🔄 Step 2: SuccessFactors Data Sync Flow

### **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    SuccessFactors (HRIS)                      │
│  - Employees (User entity)                                   │
│  - Positions (Position entity)                               │
│  - Org Units (OrgUnit entity)                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ OData API
                        │ (OAuth 2.0)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              HRIS Service (Port 8002)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SuccessFactors Client                                │  │
│  │  - Authenticate                                       │  │
│  │  - Fetch Users/Positions/OrgUnits                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Transformer                                     │  │
│  │  - Map SF fields → Internal format                   │  │
│  │  - Validate data                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP API
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              Org Service (Port 8000)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Sync Endpoint                                        │  │
│  │  - Receive transformed data                           │  │
│  │  - Store in PostgreSQL                               │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ SQL INSERT/UPDATE
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL (Neon)                               │
│  - org_unit table                                            │
│  - position table                                            │
│  - employee table                                            │
│  - job table                                                 │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ Query via API
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              Frontend (React)                                │
│  - Fetch org chart data                                      │
│  - Render org chart visualization                            │
│  - Display in 26+ structure types                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 Step 3: Connect SuccessFactors

### **3.1 Start HRIS Service**

```powershell
# Terminal 1: Start HRIS Service
cd backend\hris-service
uvicorn main:app --reload --port 8002
```

### **3.2 Create Connection via Frontend**

1. **Open Frontend**: http://localhost:5173
2. **Click Sidebar**: "HRIS Connections"
3. **Click**: "Add New Connection"
4. **Fill Form**:
   - **Name**: "Production SuccessFactors"
   - **Type**: "SuccessFactors"
   - **Company ID**: Your SuccessFactors company ID
   - **API URL**: 
     - Europe: `https://api.successfactors.eu`
     - North America: `https://api.successfactors.com`
   - **Username**: Your API user
   - **Password**: Your API password
5. **Click**: "Test Connection"
6. **If successful**: Click "Save Connection"

### **3.3 Test Connection via API**

```bash
curl -X POST http://localhost:8002/api/v1/hris/successfactors/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "YOUR_COMPANY_ID",
    "username": "api_user",
    "password": "api_password",
    "api_url": "https://api.successfactors.eu"
  }'
```

---

## 📥 Step 4: Sync Data from SuccessFactors

### **4.1 Fetch Data (Test)**

```bash
# Fetch employees
curl "http://localhost:8002/api/v1/hris/successfactors/users?company_id=YOUR_ID&username=api_user&password=api_pass&limit=10"

# Fetch positions
curl "http://localhost:8002/api/v1/hris/successfactors/positions?company_id=YOUR_ID&username=api_user&password=api_pass&limit=10"

# Fetch org units
curl "http://localhost:8002/api/v1/hris/successfactors/org-units?company_id=YOUR_ID&username=api_user&password=api_pass&limit=10"
```

### **4.2 Start Full Sync**

```bash
# Start sync job
curl -X POST http://localhost:8002/api/v1/hris/sync/start \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "your-connection-uuid",
    "sync_type": "full",
    "entities": ["employees", "positions", "org_units"]
  }'
```

**Response:**
```json
{
  "sync_id": "uuid-here",
  "status": "pending",
  "started_at": "2024-01-15T10:00:00Z",
  "connection_id": "connection-uuid",
  "entities": ["employees", "positions", "org_units"]
}
```

### **4.3 Check Sync Status**

```bash
curl "http://localhost:8002/api/v1/hris/sync/{sync_id}"
```

---

## 🔄 Step 5: Data Transformation & Storage

### **SuccessFactors → Internal Format**

The `DataTransformer` service maps SuccessFactors fields:

| SuccessFactors Field | Internal Field | Table |
|---------------------|----------------|-------|
| `User.userId` | `employee_number` | `employee` |
| `User.firstName` | `first_name` | `employee` |
| `User.lastName` | `last_name` | `employee` |
| `User.email` | `email` | `employee` |
| `Position.positionId` | `hris_id` | `position` |
| `Position.positionCode` | `position_code` | `position` |
| `Position.positionTitle` | `position_title` | `position` |
| `Position.reportsToPositionId` | `reports_to_position_id` | `position` |
| `OrgUnit.orgUnitId` | `hris_id` | `org_unit` |
| `OrgUnit.orgUnitCode` | `code` | `org_unit` |
| `OrgUnit.orgUnitName` | `name` | `org_unit` |

### **Data Storage Process**

1. **HRIS Service** fetches raw SuccessFactors data
2. **DataTransformer** converts to internal format
3. **Org Service** receives data via sync endpoint
4. **Database** stores in PostgreSQL tables:
   - `employee` table
   - `position` table
   - `org_unit` table
   - `job` table (if job profiles exist)

---

## 📊 Step 6: View Org Chart

### **After Sync Completes**

1. **Open Frontend**: http://localhost:5173
2. **Click**: "Org Chart" in sidebar
3. **View**: Your org chart should display with real SuccessFactors data!

### **API Endpoint**

```bash
# Get org chart tree
curl "http://localhost:8000/api/v1/org-chart"
```

**Response:**
```json
{
  "id": "root-position-id",
  "name": "CEO",
  "title": "Chief Executive Officer",
  "children": [
    {
      "id": "manager-id",
      "name": "VP Engineering",
      "title": "Vice President",
      "children": [...]
    }
  ]
}
```

---

## 🔄 Step 7: Schedule Automatic Syncs

### **Recommended Sync Schedule**

- **Full Sync**: Daily at 2 AM (overnight)
- **Incremental Sync**: Every 4-6 hours
- **Real-time**: Via webhooks (if SuccessFactors supports)

### **Setup Cron Job (Linux/Mac)**

```bash
# Edit crontab
crontab -e

# Add daily sync at 2 AM
0 2 * * * curl -X POST http://localhost:8002/api/v1/hris/sync/start -H "Content-Type: application/json" -d '{"connection_id":"your-id","sync_type":"full","entities":["employees","positions","org_units"]}'
```

### **Setup Task Scheduler (Windows)**

1. Open **Task Scheduler**
2. Create **Basic Task**
3. **Trigger**: Daily at 2:00 AM
4. **Action**: Start a program
5. **Program**: `curl.exe`
6. **Arguments**: 
   ```
   -X POST http://localhost:8002/api/v1/hris/sync/start -H "Content-Type: application/json" -d "{\"connection_id\":\"your-id\",\"sync_type\":\"full\",\"entities\":[\"employees\",\"positions\",\"org_units\"]}"
   ```

---

## 🗄️ Neo4j Setup (Optional)

### **When to Use Neo4j**

- Complex relationship queries
- Pathfinding (e.g., "Who reports to CEO through 5 levels?")
- Skill matching
- Scenario planning

### **Setup Neo4j**

1. **Install Neo4j Desktop** or use **Neo4j Aura** (cloud)
2. **Create Database**
3. **Update Connection String** in `backend/org-service/app/config.py`:
   ```python
   NEO4J_URI = "bolt://localhost:7687"
   NEO4J_USER = "neo4j"
   NEO4J_PASSWORD = "your-password"
   ```
4. **Run Schema**: Copy `database/neo4j_schema.cypher` into Neo4j Browser

### **Sync PostgreSQL → Neo4j**

Currently, Neo4j sync is **not implemented**. You would need to:
1. Create a sync service that reads from PostgreSQL
2. Creates nodes and relationships in Neo4j
3. Keeps both databases in sync

**Note**: For most use cases, PostgreSQL is sufficient. Neo4j is only needed for advanced graph queries.

---

## ✅ Verification Checklist

- [ ] PostgreSQL tables created (`schema.sql` run)
- [ ] Functional chart tables created (`functional_chart_schema.sql` run)
- [ ] HRIS Service running on port 8002
- [ ] Org Service running on port 8000
- [ ] SuccessFactors connection tested
- [ ] First sync completed successfully
- [ ] Org chart displays in frontend
- [ ] Data persists after refresh

---

## 🐛 Troubleshooting

### **Error: "relation does not exist"**

**Solution**: Run the database schemas (Step 1)

### **Error: "Connection failed"**

**Check**:
- SuccessFactors API credentials correct
- API URL matches your region
- API user has correct permissions
- Network connectivity

### **Error: "No data in org chart"**

**Check**:
- Sync completed successfully
- Data exists in PostgreSQL:
  ```sql
  SELECT COUNT(*) FROM position;
  SELECT COUNT(*) FROM employee;
  SELECT COUNT(*) FROM org_unit;
  ```

### **Data Not Syncing**

**Check**:
- HRIS Service logs
- Sync job status
- Database connection in Org Service

---

## 📚 Next Steps

1. **Run Database Schemas** (Step 1)
2. **Connect SuccessFactors** (Step 3)
3. **Start First Sync** (Step 4)
4. **View Org Chart** (Step 6)
5. **Schedule Automatic Syncs** (Step 7)

---

## 🔗 Related Files

- `database/schema.sql` - Main PostgreSQL schema
- `database/functional_chart_schema.sql` - Functional chart tables
- `database/neo4j_schema.cypher` - Neo4j schema (optional)
- `backend/hris-service/` - HRIS integration service
- `backend/org-service/` - Org chart service
- `SUCCESSFACTORS_INTEGRATION_GUIDE.md` - Detailed SuccessFactors guide
