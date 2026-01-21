# SuccessFactors Mapping & Data Transfer - Complete Guide ✅

## 📍 Where Mapping Happens in the Application

### **Location 1: After Connection is Created**

**Path:** `HRIS Connections` → Connection Card → **"Mapping"** Tab

After you successfully connect to SuccessFactors, the connection card will have **tabs**:

```
┌─────────────────────────────────────────────────┐
│  SAP SuccessFactors                    [active]  │
├─────────────────────────────────────────────────┤
│  [Overview] [Mapping] [Sync History] [Settings] │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │  Field Mapping Configuration               │ │
│  │                                             │ │
│  │  Entity: [Org Units ▼] [Positions] [Employees]│
│  │                                             │ │
│  │  SuccessFactors Field  →  OrgChartAI Field │ │
│  │  ─────────────────────────────────────────  │ │
│  │  orgUnitName          →  name          ✓    │ │
│  │  orgUnitCode          →  code          ✓    │ │
│  │  orgUnitId            →  hris_id       ✓    │ │
│  │  ...                                        │ │
│  │                                             │ │
│  │  [Save Mapping] [Discover Fields]          │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### **Location 2: During First Sync**

When you click **"Sync"** for the first time, you'll be prompted to configure mapping if not done:

```
┌─────────────────────────────────────────────────┐
│  First Time Sync                                │
├─────────────────────────────────────────────────┤
│  Before syncing, configure field mappings:     │
│                                                 │
│  [Configure Mapping]  [Use Defaults]          │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Complete Data Transfer Flow

### **Step-by-Step Process**

#### **Step 1: Connect (UI Location: HRIS Connections Page)**

```
User Action: Click "+ Add Connection"
↓
Fill in credentials
↓
Click "Test Connection"
↓
Click "Save Connection"
↓
✅ Connection saved to database
```

#### **Step 2: Configure Mapping (UI Location: Connection Card → Mapping Tab)**

```
User Action: Open connection card → Click "Mapping" tab
↓
View default mappings (pre-configured)
↓
(Optional) Customize mappings for custom fields
↓
Click "Save Mapping"
↓
✅ Mappings saved to database
```

#### **Step 3: Sync Data (UI Location: Connection Card → Sync Button)**

```
User Action: Click refresh icon on connection card
↓
Select sync options:
  - Full Sync or Incremental
  - Entities to sync (Org Units, Positions, Employees)
↓
Click "Start Sync"
↓
Backend Process:
  1. HRIS Service authenticates with SuccessFactors
  2. Fetches data via OData API
  3. Transforms data using mappings
  4. Stores in PostgreSQL database
  5. Builds org chart structure
↓
✅ Data appears in Org Chart view
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (React - localhost:3000)                          │
│                                                               │
│  1. HRIS Connections Page                                     │
│     └─ User clicks "Add Connection"                          │
│                                                               │
│  2. Connection Card                                          │
│     ├─ Overview Tab                                           │
│     ├─ Mapping Tab ← CONFIGURE MAPPING HERE                  │
│     ├─ Sync History Tab                                      │
│     └─ Settings Tab                                           │
│                                                               │
│  3. Sync Button (refresh icon)                               │
│     └─ User clicks to start sync                              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP API Calls
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  HRIS SERVICE (Port 8002)                                    │
│                                                               │
│  1. POST /api/v1/hris/successfactors/test-connection        │
│     └─ Tests authentication                                  │
│                                                               │
│  2. POST /api/v1/hris/connections                            │
│     └─ Saves connection                                       │
│                                                               │
│  3. POST /api/v1/hris/connections/{id}/mapping                │
│     └─ Saves field mappings                                   │
│                                                               │
│  4. POST /api/v1/hris/sync/start                             │
│     └─ Starts sync process                                    │
│                                                               │
│  5. SuccessFactorsClient                                     │
│     ├─ Authenticates (Basic Auth: username@companyID:pass)  │
│     ├─ GET /odata/v2/OrgUnit?$select=...                    │
│     ├─ GET /odata/v2/Position?$select=...                   │
│     └─ GET /odata/v2/User?$select=...                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Raw SuccessFactors Data
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  DATA TRANSFORMATION                                         │
│                                                               │
│  DataTransformer Service                                     │
│  Uses mapping configuration to transform:                   │
│                                                               │
│  SuccessFactors Format → OrgChartAI Format                    │
│                                                               │
│  Example:                                                    │
│  {                                                           │
│    "orgUnitName": "Engineering"                              │
│  }                                                           │
│  ↓ (using mapping: orgUnitName → name)                       │
│  {                                                           │
│    "name": "Engineering",                                    │
│    "hris_id": "SF_001",                                      │
│    "hris_source": "successfactors"                           │
│  }                                                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Transformed Data
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  ORG SERVICE (Port 8000)                                     │
│                                                               │
│  POST /api/v1/hris/sync/data                                 │
│  └─ Receives transformed data                                │
│                                                               │
│  Stores in PostgreSQL:                                       │
│  ├─ org_unit table (with hris_id, hris_source)               │
│  ├─ position table (with hris_id, hris_source)              │
│  └─ employee table (with hris_id, hris_source)              │
│                                                               │
│  Resolves relationships:                                     │
│  ├─ parent_org_unit_id (from parent_hris_id)                │
│  ├─ org_unit_id (from org_unit_hris_id)                     │
│  └─ position_id (from position_hris_id)                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Database Queries
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND - Org Chart View                                    │
│                                                               │
│  GET /api/v1/org-chart                                        │
│  └─ Fetches org chart tree                                   │
│                                                               │
│  React renders org chart                                     │
│  └─ Users see their SuccessFactors data!                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗺️ Mapping Storage

### **Database Table: `hris_connection_mapping`**

```sql
CREATE TABLE hris_connection_mapping (
    id UUID PRIMARY KEY,
    connection_id UUID REFERENCES hris_connection(id),
    entity_type TEXT,  -- 'org_unit', 'position', 'employee'
    source_field TEXT,  -- 'orgUnitName' (SuccessFactors field)
    target_field TEXT,  -- 'name' (OrgChartAI field)
    mapping_type TEXT,  -- 'direct', 'transform', 'custom'
    transform_function TEXT,  -- Optional transformation
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### **Default Mappings (Auto-Applied)**

When you first connect, these mappings are **automatically created**:

**OrgUnit:**
- `orgUnitId` → `hris_id`
- `orgUnitCode` → `code`
- `orgUnitName` → `name`
- `orgUnitType` → `type`
- `parentOrgUnitId` → `parent_hris_id`
- `status` → `status`

**Position:**
- `positionId` → `hris_id`
- `positionCode` → `position_code`
- `positionTitle` → `position_title`
- `reportsToPositionId` → `reports_to_hris_id`
- `orgUnitId` → `org_unit_hris_id`

**Employee:**
- `userId` → `employee_number`
- `firstName` → `first_name`
- `lastName` → `last_name`
- `displayName` → `preferred_name`
- `email` → `email`

**You only need to customize if you have custom SuccessFactors fields!**

---

## 🎯 Quick Reference: Where to Find Everything

| Action | UI Location | API Endpoint |
|--------|------------|--------------|
| **Connect** | HRIS Connections → "+ Add Connection" | `POST /api/v1/hris/connections` |
| **Configure Mapping** | Connection Card → "Mapping" Tab | `POST /api/v1/hris/connections/{id}/mapping` |
| **View Mappings** | Connection Card → "Mapping" Tab | `GET /api/v1/hris/connections/{id}/mapping` |
| **Start Sync** | Connection Card → Refresh Icon | `POST /api/v1/hris/sync/start` |
| **View Sync Status** | Connection Card → "Sync History" Tab | `GET /api/v1/hris/sync/{sync_id}` |
| **View Org Chart** | Org Chart View | `GET /api/v1/org-chart` |

---

## ✅ Summary

1. **Connect:** HRIS Connections → Add Connection → Test → Save
2. **Map (Optional):** Connection Card → Mapping Tab → Configure → Save
3. **Sync:** Connection Card → Sync Button → Start Sync
4. **View:** Org Chart → See your SuccessFactors data!

**Mapping happens in the Connection Card's "Mapping" tab after connection is established!**

---

## 📝 Files Created

- ✅ `SUCCESSFACTORS_MAPPING_UI_GUIDE.md` - Complete UI flow guide
- ✅ `frontend/src/components/HRIS/FieldMappingEditor.tsx` - Mapping UI component
- ✅ `MAPPING_AND_DATA_TRANSFER_COMPLETE.md` - This summary

**The mapping UI is ready to be integrated into the connection card!** 🚀
