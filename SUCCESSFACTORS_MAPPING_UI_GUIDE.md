# SuccessFactors Mapping & Data Transfer Guide

## 🎯 Complete Flow: From Connection to Org Chart

This guide shows **exactly where** mapping happens in the UI and **how data flows** from SuccessFactors to your org chart.

---

## 📍 Step-by-Step Process

### **Step 1: Connect SuccessFactors**

**Location:** `HRIS Connections` page

1. Navigate to **"INTEGRATION & AI"** → **"HRIS Connections"** in sidebar
2. Click **"+ Add Connection"** button
3. Fill in connection details:
   - **Authentication Method:** Basic Authentication or OAuth 2.0
   - **Company ID:** `SFHUB003674` (your SuccessFactors company ID)
   - **API Username:** `sfadmin` (your API user)
   - **API Password:** `••••••••` (your password)
   - **API URL:** `https://api.successfactors.eu` (or your region)
4. Click **"Test Connection"** to verify
5. Click **"Save Connection"**

**What happens:**
- Connection is saved to database
- Credentials are encrypted
- Connection status: **"active"** (green badge)

---

### **Step 2: Field Mapping (NEW - After Connection)**

**Location:** `HRIS Connections` → Connection Details → **"Mapping"** tab

After successful connection, you'll see a new **"Mapping"** tab in the connection card.

#### **2.1 Automatic Mapping Discovery**

When you first open the Mapping tab:

```
┌─────────────────────────────────────────────────┐
│  SuccessFactors Field Mapping                    │
├─────────────────────────────────────────────────┤
│                                                   │
│  🔍 Discovering fields from SuccessFactors...     │
│                                                   │
│  ✓ OrgUnit fields discovered (8 fields)         │
│  ✓ Position fields discovered (12 fields)       │
│  ✓ User fields discovered (10 fields)            │
│                                                   │
└─────────────────────────────────────────────────┘
```

#### **2.2 Mapping Configuration UI**

**Location:** Connection Card → **"Mapping"** tab → **"Configure Mapping"** button

```
┌─────────────────────────────────────────────────────────────┐
│  Field Mapping Configuration                                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Entity: OrgUnit                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ SuccessFactors Field  │  →  │ OrgChartAI Field  │ ✓   │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ orgUnitId            │  →  │ hris_id            │ ✓   │  │
│  │ orgUnitCode           │  →  │ code               │ ✓   │  │
│  │ orgUnitName           │  →  │ name               │ ✓   │  │
│  │ orgUnitType           │  →  │ type               │ ✓   │  │
│  │ parentOrgUnitId       │  →  │ parent_hris_id     │ ✓   │  │
│  │ status                │  →  │ status             │ ✓   │  │
│  │ effectiveStartDate    │  →  │ effective_start... │ ✓   │  │
│  │ effectiveEndDate      │  →  │ effective_end_date │ ✓   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Entity: Position                                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ SuccessFactors Field  │  →  │ OrgChartAI Field  │ ✓   │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ positionId            │  →  │ hris_id            │ ✓   │  │
│  │ positionCode           │  →  │ position_code      │ ✓   │  │
│  │ positionTitle          │  →  │ position_title    │ ✓   │  │
│  │ reportsToPositionId   │  →  │ reports_to_hris_id │ ✓   │  │
│  │ orgUnitId              │  →  │ org_unit_hris_id  │ ✓   │  │
│  │ status                 │  →  │ status            │ ✓   │  │
│  │ fte                    │  →  │ fte               │ ✓   │  │
│  │ grade                  │  →  │ grade             │ ✓   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Entity: User (Employee)                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ SuccessFactors Field  │  →  │ OrgChartAI Field  │ ✓   │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ userId                │  →  │ employee_number   │ ✓   │  │
│  │ firstName             │  →  │ first_name        │ ✓   │  │
│  │ lastName              │  →  │ last_name         │ ✓   │  │
│  │ displayName           │  →  │ preferred_name    │ ✓   │  │
│  │ email                 │  →  │ email             │ ✓   │  │
│  │ positionId            │  →  │ position_hris_id  │ ✓   │  │
│  │ status                │  →  │ status            │ ✓   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  [Save Mapping]  [Test Mapping]  [Reset to Default]          │
└─────────────────────────────────────────────────────────────┘
```

#### **2.3 AI-Powered Mapping (Optional)**

If AI mapping is enabled:

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 AI Field Matching                                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  SuccessFactors Field: customField01                         │
│                                                               │
│  AI Suggestions:                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ✓ notes (confidence: 0.92)                            │  │
│  │   description (confidence: 0.78)                       │  │
│  │   comments (confidence: 0.65)                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  [Accept]  [Reject]  [Suggest Another]                      │
└─────────────────────────────────────────────────────────────┘
```

---

### **Step 3: Sync Data**

**Location:** Connection Card → **"Sync"** button (refresh icon)

#### **3.1 Sync Options**

Click the **refresh icon** on the connection card to open sync options:

```
┌─────────────────────────────────────────────────┐
│  Sync SuccessFactors Data                        │
├─────────────────────────────────────────────────┤
│                                                   │
│  Sync Type:                                      │
│  ○ Full Sync (all data)                          │
│  ● Incremental Sync (changes only)               │
│                                                   │
│  Entities to Sync:                               │
│  ☑ Org Units                                     │
│  ☑ Positions                                     │
│  ☑ Employees                                     │
│  ☐ Job Profiles                                  │
│                                                   │
│  Options:                                        │
│  ☑ Update existing records                       │
│  ☑ Create new records                            │
│  ☐ Delete removed records                        │
│                                                   │
│  [Start Sync]  [Cancel]                          │
└─────────────────────────────────────────────────┘
```

#### **3.2 Sync Progress**

During sync, you'll see a progress indicator:

```
┌─────────────────────────────────────────────────┐
│  Syncing SuccessFactors...                       │
├─────────────────────────────────────────────────┤
│                                                   │
│  ⏳ Fetching Org Units...          [████░░] 75%  │
│  ⏳ Fetching Positions...          [███░░░] 60%  │
│  ⏳ Fetching Employees...          [██░░░░] 40%  │
│                                                   │
│  Progress: 58% (1,234 / 2,134 records)           │
│                                                   │
│  [Cancel Sync]                                    │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Data Transfer Flow

### **Complete Data Flow Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: User Initiates Sync                                 │
│  Location: HRIS Connections → Connection Card → Sync Button  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Frontend Calls API                                  │
│  POST /api/v1/hris/sync/start                                │
│  {                                                           │
│    "connection_id": "uuid",                                 │
│    "sync_type": "full",                                      │
│    "entities": ["org_units", "positions", "employees"]      │
│  }                                                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: HRIS Service (Port 8002)                           │
│  ├─ Authenticates with SuccessFactors                       │
│  ├─ Fetches data via OData API                              │
│  │   GET /odata/v2/OrgUnit?$select=...                      │
│  │   GET /odata/v2/Position?$select=...                     │
│  │   GET /odata/v2/User?$select=...                         │
│  └─ Returns raw SuccessFactors data                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Data Transformation                                 │
│  Location: backend/hris-service/app/services/                │
│            data_transformer.py                               │
│                                                               │
│  Uses mapping configuration to transform:                    │
│  SuccessFactors Format → OrgChartAI Format                   │
│                                                               │
│  Example:                                                    │
│  {                                                           │
│    "orgUnitName": "Engineering"  →  "name": "Engineering"  │
│    "orgUnitCode": "ENG"          →  "code": "ENG"           │
│    "orgUnitId": "SF_001"         →  "hris_id": "SF_001"     │
│  }                                                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Store in Database                                   │
│  Location: Org Service (Port 8000)                          │
│  Database: PostgreSQL (Neon)                                │
│                                                               │
│  Tables:                                                     │
│  ├─ org_unit (with hris_id, hris_source)                    │
│  ├─ position (with hris_id, hris_source)                    │
│  └─ employee (with hris_id, hris_source)                   │
│                                                               │
│  Relationships resolved:                                     │
│  ├─ parent_org_unit_id (from parent_hris_id)                │
│  ├─ org_unit_id (from org_unit_hris_id)                     │
│  └─ position_id (from position_hris_id)                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Build Org Chart                                     │
│  Location: Org Service → Chart Builder                      │
│                                                               │
│  Queries database:                                          │
│  ├─ Root positions (reports_to_position_id IS NULL)         │
│  ├─ Recursively builds tree                                 │
│  └─ Attaches employee data                                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 7: Display in Frontend                                │
│  Location: Org Chart View                                    │
│                                                               │
│  GET /api/v1/org-chart                                       │
│  → Returns tree structure                                    │
│  → React renders org chart                                   │
│  → Users see their SuccessFactors data!                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗺️ Mapping Configuration Location

### **Where Mapping is Stored**

1. **Database Table:** `hris_connection_mapping`
   ```sql
   CREATE TABLE hris_connection_mapping (
       id UUID PRIMARY KEY,
       connection_id UUID REFERENCES hris_connection(id),
       entity_type TEXT,  -- 'org_unit', 'position', 'employee'
       source_field TEXT,  -- 'orgUnitName'
       target_field TEXT,  -- 'name'
       mapping_type TEXT,  -- 'direct', 'transform', 'custom'
       transform_function TEXT,  -- Optional transformation
       created_at TIMESTAMP,
       updated_at TIMESTAMP
   );
   ```

2. **UI Location:** 
   - Connection Card → **"Mapping"** tab
   - Or: Connection Card → **"Settings"** → **"Field Mapping"**

3. **API Endpoints:**
   ```
   GET    /api/v1/hris/connections/{id}/mapping
   POST   /api/v1/hris/connections/{id}/mapping
   PUT    /api/v1/hris/connections/{id}/mapping/{mapping_id}
   DELETE /api/v1/hris/connections/{id}/mapping/{mapping_id}
   ```

---

## 🎨 UI Components for Mapping

### **1. Connection Card with Mapping Tab**

```tsx
// Location: frontend/src/components/HRIS/HRISConnectionManager.tsx

<ConnectionCard>
  <Tabs>
    <Tab name="Overview">...</Tab>
    <Tab name="Mapping">  {/* NEW TAB */}
      <FieldMappingEditor
        connectionId={connection.id}
        entityTypes={['org_unit', 'position', 'employee']}
      />
    </Tab>
    <Tab name="Sync History">...</Tab>
  </Tabs>
</ConnectionCard>
```

### **2. Field Mapping Editor Component**

```tsx
// Location: frontend/src/components/HRIS/FieldMappingEditor.tsx

const FieldMappingEditor = ({ connectionId, entityTypes }) => {
  // Fetches mapping configuration
  // Displays field mapping table
  // Allows editing mappings
  // Saves to backend
};
```

---

## 📋 Default Mapping Rules

### **Pre-configured Mappings**

When you first connect, these mappings are **automatically applied**:

#### **OrgUnit Mapping**
```javascript
{
  "orgUnitId": "hris_id",
  "orgUnitCode": "code",
  "orgUnitName": "name",
  "orgUnitType": "type",
  "parentOrgUnitId": "parent_hris_id",
  "status": "status",
  "effectiveStartDate": "effective_start_date",
  "effectiveEndDate": "effective_end_date"
}
```

#### **Position Mapping**
```javascript
{
  "positionId": "hris_id",
  "positionCode": "position_code",
  "positionTitle": "position_title",
  "reportsToPositionId": "reports_to_hris_id",
  "orgUnitId": "org_unit_hris_id",
  "jobCode": "job_code",
  "status": "status",
  "fte": "fte",
  "grade": "grade"
}
```

#### **Employee Mapping**
```javascript
{
  "userId": "employee_number",
  "firstName": "first_name",
  "lastName": "last_name",
  "displayName": "preferred_name",
  "email": "email",
  "positionId": "position_hris_id",
  "status": "status",
  "startDate": "hire_date"
}
```

**These are applied automatically** - you only need to customize if you have custom fields!

---

## 🔧 Custom Field Mapping

### **If SuccessFactors has Custom Fields**

1. **Open Mapping Tab** in connection card
2. **Click "Add Custom Mapping"**
3. **Select Entity Type** (OrgUnit, Position, or Employee)
4. **Enter SuccessFactors Field Name:** `customField01`
5. **Select Target Field:** Use dropdown or AI suggestion
6. **Save Mapping**

The custom mapping is now saved and will be used in all future syncs.

---

## ✅ Verification After Sync

### **Check if Data Transferred Successfully**

1. **Navigate to "Org chart"** view
2. **You should see:**
   - Org units from SuccessFactors
   - Positions with employees
   - Hierarchy structure

3. **Or check database:**
   ```sql
   -- Check org units synced
   SELECT COUNT(*) FROM org_unit 
   WHERE hris_source = 'successfactors';
   
   -- Check positions synced
   SELECT COUNT(*) FROM position 
   WHERE hris_id IS NOT NULL;
   
   -- Check employees synced
   SELECT COUNT(*) FROM employee 
   WHERE hris_source = 'successfactors';
   ```

---

## 🚀 Quick Start Summary

1. **Connect:** HRIS Connections → Add Connection → Test → Save
2. **Map (Optional):** Connection Card → Mapping Tab → Configure
3. **Sync:** Connection Card → Sync Button → Start Sync
4. **View:** Org Chart → See your SuccessFactors data!

---

## 📝 Next Steps

- ✅ Connection UI - **DONE**
- 🔄 Mapping UI - **TO BE IMPLEMENTED** (see below)
- ✅ Sync API - **DONE**
- ✅ Data Transformation - **DONE**
- ✅ Org Chart Display - **DONE**

**The mapping UI component needs to be added to show the mapping configuration interface!**
