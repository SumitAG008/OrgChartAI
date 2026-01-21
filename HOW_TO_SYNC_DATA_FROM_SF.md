# How to Sync Data from SuccessFactors to OrgChartAI

## 🎯 Complete Sync Process

This guide shows you **exactly how** to sync data from SuccessFactors to your OrgChartAI application after you've configured field mappings.

---

## 📋 Prerequisites

Before syncing, make sure you have:

1. ✅ **Connection Created** - SuccessFactors connection saved in HRIS Connections
2. ✅ **Field Mappings Configured** - All required fields mapped (source → target)
3. ✅ **Mappings Saved** - Clicked "Save Mapping" button
4. ✅ **Backend Services Running**:
   - HRIS Service: `http://localhost:8002`
   - Org Service: `http://localhost:8000`

---

## 🔄 Sync Process Overview

```
SuccessFactors API
    ↓
HRIS Service (Port 8002)
    ├─ Fetch data from SF using saved credentials
    ├─ Apply field mappings
    ├─ Transform data using transformation functions
    └─ Send to Org Service
    ↓
Org Service (Port 8000)
    ├─ Resolve relationships (parent-child, reports-to)
    ├─ Store in PostgreSQL database
    └─ Build org chart structure
    ↓
Frontend (React)
    └─ Display org chart
```

---

## 🚀 Step-by-Step Sync Process

### **Step 1: Verify Mappings Are Saved**

1. Go to **HRIS Connections** → Select your connection
2. Click **"Mapping"** tab
3. Verify you see **"Your Saved Mappings"** section with your mappings listed
4. Each mapping should show:
   - Source entity (e.g., `FODepartment`)
   - Target entity (e.g., `org_unit`)
   - Field count (e.g., "5 fields mapped")

---

### **Step 2: Start Sync from UI (Recommended)**

**Location:** `HRIS Connections` → Connection Card → **"Sync History"** tab

1. Click on your SuccessFactors connection card
2. Go to **"Sync History"** tab
3. Click **"Start Sync"** or **"Sync Now"** button
4. Select sync type:
   - **Full Sync**: Sync all data (first time)
   - **Incremental Sync**: Only sync changes since last sync
5. Select entities to sync:
   - ✅ Organizational Units
   - ✅ Positions
   - ✅ Employees
6. Click **"Start Sync"**

**What happens:**
- System uses saved connection credentials
- Fetches data from SuccessFactors API
- Applies your saved field mappings
- Transforms data using transformation functions
- Stores in PostgreSQL database
- Shows progress in "Sync History" tab

---

### **Step 3: Start Sync via API (Alternative)**

If UI sync is not available, use the API directly:

#### **3.1 Full Sync (All Entities)**

```bash
POST http://localhost:8002/api/v1/hris/sync/start
Content-Type: application/json

{
  "connection_id": "conn-1768822729401",
  "sync_type": "full",
  "entities": ["org_unit", "position", "employee"]
}
```

#### **3.2 Sync Specific Entity**

```bash
# Sync only org units
POST http://localhost:8002/api/v1/hris/sync/start
Content-Type: application/json

{
  "connection_id": "conn-1768822729401",
  "sync_type": "full",
  "entities": ["org_unit"]
}
```

#### **3.3 Incremental Sync**

```bash
POST http://localhost:8002/api/v1/hris/sync/start
Content-Type: application/json

{
  "connection_id": "conn-1768822729401",
  "sync_type": "incremental",
  "entities": ["org_unit", "position", "employee"],
  "since": "2024-01-19T00:00:00Z"
}
```

---

## 🔍 How Sync Works Internally

### **Phase 1: Fetch Data from SuccessFactors**

```python
# HRIS Service fetches data using saved credentials
# Example: Fetch org units

GET {api_url}/odata/v2/FODepartment
Headers:
  Authorization: Basic {base64(username@companyID:password)}
  
Response:
{
  "d": {
    "results": [
      {
        "externalCode": "DEPT001",
        "name": "Engineering",
        "description": "Engineering Department",
        "status": "active",
        ...
      }
    ]
  }
}
```

### **Phase 2: Apply Field Mappings**

```python
# System uses your saved mappings
# Example mapping:
#   externalCode → code
#   name → name
#   description → description
#   status → status (with status_active transformation)
#   type → type (with constant('Department') transformation)

# Transformed record:
{
  "code": "DEPT001",
  "name": "Engineering",
  "description": "Engineering Department",
  "status": "Active",  # Transformed
  "type": "Department",  # Constant value
  "hris_id": "DEPT001",
  "hris_source": "successfactors"
}
```

### **Phase 3: Send to Org Service**

```python
# HRIS Service sends transformed data to Org Service
POST http://localhost:8000/api/v1/org-units/bulk
Content-Type: application/json

{
  "records": [
    {
      "code": "DEPT001",
      "name": "Engineering",
      "status": "Active",
      "hris_id": "DEPT001",
      ...
    }
  ]
}
```

### **Phase 4: Store in Database**

```sql
-- Org Service stores in PostgreSQL
INSERT INTO org_unit (
  code, name, type, status,
  hris_id, hris_source,
  created_at, updated_at
) VALUES (
  'DEPT001', 'Engineering', 'Department', 'Active',
  'DEPT001', 'successfactors',
  NOW(), NOW()
)
ON CONFLICT (hris_id) DO UPDATE SET
  name = EXCLUDED.name,
  status = EXCLUDED.status,
  updated_at = NOW();
```

---

## 📊 Check Sync Status

### **Via API**

```bash
# Get sync status
GET http://localhost:8002/api/v1/hris/sync/{sync_id}

# Response:
{
  "sync_id": "abc-123",
  "status": "completed",
  "started_at": "2024-01-19T10:00:00Z",
  "connection_id": "conn-1768822729401",
  "entities": ["org_unit", "position", "employee"],
  "total_records": 150,
  "processed_records": 150,
  "failed_records": 0,
  "errors": []
}
```

### **Via UI**

1. Go to **HRIS Connections** → Your connection
2. Click **"Sync History"** tab
3. View sync jobs with:
   - Status (Pending, Running, Completed, Failed)
   - Records processed
   - Errors (if any)
   - Timestamp

---

## ✅ Verify Data Was Synced

### **Check Database**

```sql
-- Check org units
SELECT COUNT(*) FROM org_unit WHERE hris_source = 'successfactors';

-- Check positions
SELECT COUNT(*) FROM position WHERE hris_source = 'successfactors';

-- Check employees
SELECT COUNT(*) FROM employee WHERE hris_source = 'successfactors';

-- View synced org units
SELECT code, name, type, status, hris_id, created_at
FROM org_unit
WHERE hris_source = 'successfactors'
ORDER BY created_at DESC
LIMIT 10;
```

### **Check Frontend**

1. Go to **Org Chart** view
2. You should see synced organizational units, positions, and employees
3. Hierarchy should be built from parent-child relationships

---

## 🐛 Troubleshooting

### **Error: "No mappings configured"**

**Solution:** Make sure you've saved field mappings in the Mapping tab.

### **Error: "Failed to authenticate with SuccessFactors"**

**Solution:** 
- Check connection credentials
- Verify API URL is correct
- Test connection first

### **Error: "Failed to send data to org-service"**

**Solution:**
- Ensure Org Service is running on port 8000
- Check network connectivity
- Verify org-service endpoints are accessible

### **No data appears after sync**

**Solution:**
1. Check sync status for errors
2. Verify mappings are correct
3. Check database for records:
   ```sql
   SELECT * FROM org_unit WHERE hris_source = 'successfactors' LIMIT 5;
   ```
4. Verify org chart is loading from database

---

## 📝 Quick Reference

| Step | Action | Location |
|------|--------|----------|
| 1 | Create Connection | HRIS Connections → Add Connection |
| 2 | Configure Mappings | HRIS Connections → Mapping Tab |
| 3 | Save Mappings | Click "Save Mapping" button |
| 4 | Start Sync | HRIS Connections → Sync History Tab → Start Sync |
| 5 | Check Status | HRIS Connections → Sync History Tab |
| 6 | View Data | Org Chart view |

---

## 🎉 Success Indicators

✅ Sync status shows "Completed"  
✅ Processed records > 0  
✅ No errors in sync history  
✅ Data visible in Org Chart view  
✅ Database contains records with `hris_source = 'successfactors'`

---

**Need Help?** Check the sync history tab for detailed error messages and logs.
