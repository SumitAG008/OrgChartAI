# SuccessFactors to OrgChartAI Data Mapping Guide

Complete guide on how SuccessFactors data maps to OrgChartAI database tables and org chart visualization.

---

## 📊 Data Flow Overview

```
SuccessFactors (OData API)
    ↓
HRIS Service (Port 8002)
    ├─ SuccessFactorsClient (fetches data)
    ├─ DataTransformer (maps fields)
    └─ Sync Endpoint (stores data)
    ↓
Org Service (Port 8000)
    └─ Database (PostgreSQL)
        ├─ org_unit table
        ├─ position table
        ├─ employee table
        └─ job table
    ↓
Frontend (React)
    └─ Org Chart Visualization
```

---

## 🔄 Entity Mapping

### **1. Organization Units (Org Units)**

#### SuccessFactors → OrgChartAI

| SuccessFactors Field | OrgChartAI Field | Database Table | Notes |
|---------------------|------------------|----------------|-------|
| `OrgUnit.orgUnitId` | `hris_id` | `org_unit` | Unique identifier from SF |
| `OrgUnit.orgUnitCode` | `code` | `org_unit` | Org unit code |
| `OrgUnit.orgUnitName` | `name` | `org_unit` | Display name |
| `OrgUnit.orgUnitType` | `type` | `org_unit` | Division, Department, Team, etc. |
| `OrgUnit.parentOrgUnitId` | `parent_org_unit_id` | `org_unit` | Hierarchy relationship |
| `OrgUnit.status` | `status` | `org_unit` | Active/Inactive |
| `OrgUnit.effectiveStartDate` | `effective_start_date` | `org_unit` | When org unit becomes active |
| `OrgUnit.effectiveEndDate` | `effective_end_date` | `org_unit` | When org unit becomes inactive |

#### Example Mapping

**SuccessFactors:**
```json
{
  "orgUnitId": "SF_OU_001",
  "orgUnitCode": "ENG",
  "orgUnitName": "Engineering",
  "orgUnitType": "Department",
  "parentOrgUnitId": "SF_OU_ROOT",
  "status": "active"
}
```

**OrgChartAI Database:**
```sql
INSERT INTO org_unit (
  hris_id, code, name, type, 
  parent_org_unit_id, status,
  created_by, version
) VALUES (
  'SF_OU_001', 'ENG', 'Engineering', 'Department',
  (SELECT id FROM org_unit WHERE hris_id = 'SF_OU_ROOT'),
  'Active',
  '00000000-0000-0000-0000-000000000000',
  1
);
```

---

### **2. Positions**

#### SuccessFactors → OrgChartAI

| SuccessFactors Field | OrgChartAI Field | Database Table | Notes |
|---------------------|------------------|----------------|-------|
| `Position.positionId` | `hris_id` | `position` | Unique identifier from SF |
| `Position.positionCode` | `position_code` | `position` | Position code |
| `Position.positionTitle` | `position_title` | `position` | Job title |
| `Position.reportsToPositionId` | `reports_to_position_id` | `position` | Manager position |
| `Position.orgUnitId` | `org_unit_id` | `position` | Which org unit this position belongs to |
| `Position.jobCode` | `job_id` | `position` | Links to job profile |
| `Position.status` | `status` | `position` | Active/Vacant |
| `Position.effectiveStartDate` | `effective_start_date` | `position` | When position becomes active |
| `Position.effectiveEndDate` | `effective_end_date` | `position` | When position becomes inactive |
| `Position.fte` | `fte` | `position` | Full-time equivalent (0.0-1.0) |
| `Position.grade` | `grade` | `position` | Job grade/level |
| `Position.isManagerial` | `is_managerial` | `position` | Boolean - is this a manager role? |

#### Example Mapping

**SuccessFactors:**
```json
{
  "positionId": "SF_POS_001",
  "positionCode": "ENG001",
  "positionTitle": "Senior Software Engineer",
  "reportsToPositionId": "SF_POS_MGR",
  "orgUnitId": "SF_OU_001",
  "jobCode": "SWE_SENIOR",
  "status": "active",
  "fte": 1.0,
  "grade": "P4"
}
```

**OrgChartAI Database:**
```sql
INSERT INTO position (
  hris_id, position_code, position_title,
  reports_to_position_id, org_unit_id, job_id,
  status, fte, grade, is_managerial,
  created_by, version
) VALUES (
  'SF_POS_001', 'ENG001', 'Senior Software Engineer',
  (SELECT id FROM position WHERE hris_id = 'SF_POS_MGR'),
  (SELECT id FROM org_unit WHERE hris_id = 'SF_OU_001'),
  (SELECT id FROM job WHERE job_code = 'SWE_SENIOR'),
  'Active', 1.0, 'P4', false,
  '00000000-0000-0000-0000-000000000000',
  1
);
```

---

### **3. Employees (Users)**

#### SuccessFactors → OrgChartAI

| SuccessFactors Field | OrgChartAI Field | Database Table | Notes |
|---------------------|------------------|----------------|-------|
| `User.userId` | `employee_number` | `employee` | Employee ID |
| `User.firstName` | `first_name` | `employee` | First name |
| `User.lastName` | `last_name` | `employee` | Last name |
| `User.displayName` | `preferred_name` | `employee` | Display name |
| `User.email` | `email` | `employee` | Email address |
| `User.status` | `status` | `employee` | Active/Inactive |
| `User.custom01` | `employee_number` | `employee` | Alternative employee number field |
| `User.positionId` | `position_id` | `employee` | Current position assignment |
| `User.startDate` | `hire_date` | `employee` | Employment start date |
| `User.endDate` | `termination_date` | `employee` | Employment end date (if applicable) |

#### Example Mapping

**SuccessFactors:**
```json
{
  "userId": "SF_USER_001",
  "firstName": "John",
  "lastName": "Doe",
  "displayName": "John Doe",
  "email": "john.doe@company.com",
  "status": "active",
  "positionId": "SF_POS_001",
  "startDate": "2020-01-15"
}
```

**OrgChartAI Database:**
```sql
INSERT INTO employee (
  employee_number, first_name, last_name,
  preferred_name, email, status,
  position_id, hire_date,
  hris_id, hris_source,
  created_by, version
) VALUES (
  'SF_USER_001', 'John', 'Doe',
  'John Doe', 'john.doe@company.com', 'Active',
  (SELECT id FROM position WHERE hris_id = 'SF_POS_001'),
  '2020-01-15',
  'SF_USER_001', 'successfactors',
  '00000000-0000-0000-0000-000000000000',
  1
);
```

---

### **4. Job Profiles (Optional)**

#### SuccessFactors → OrgChartAI

| SuccessFactors Field | OrgChartAI Field | Database Table | Notes |
|---------------------|------------------|----------------|-------|
| `JobProfile.jobCode` | `job_code` | `job` | Job profile code |
| `JobProfile.jobTitle` | `job_title` | `job` | Standard job title |
| `JobProfile.jobFamily` | `job_family` | `job` | Job family (e.g., "Engineering") |
| `JobProfile.jobSubFamily` | `job_sub_family` | `job` | Sub-family (e.g., "Software Development") |
| `JobProfile.defaultGrade` | `default_grade` | `job` | Default grade for this job |
| `JobProfile.description` | `description` | `job` | Job description |

---

## 🔧 Implementation Details

### **Step 1: Fetch Data from SuccessFactors**

The HRIS Service uses OData API to fetch data:

```python
# backend/hris-service/app/services/successfactors_client.py

# Fetch Org Units
GET /odata/v2/OrgUnit?$select=orgUnitId,orgUnitCode,orgUnitName,orgUnitType,parentOrgUnitId,status

# Fetch Positions
GET /odata/v2/Position?$select=positionId,positionCode,positionTitle,reportsToPositionId,orgUnitId,jobCode,status

# Fetch Users
GET /odata/v2/User?$select=userId,firstName,lastName,displayName,email,status,positionId
```

### **Step 2: Transform Data**

The `DataTransformer` service maps SuccessFactors fields to internal format:

```python
# backend/hris-service/app/services/data_transformer.py

def transform_successfactors_org_unit(org_unit: SuccessFactorsOrgUnit) -> Dict:
    return {
        "code": org_unit.orgUnitCode or org_unit.orgUnitId,
        "name": org_unit.orgUnitName or "",
        "type": org_unit.orgUnitType or "Department",
        "status": "Active" if org_unit.status == "active" else "Inactive",
        "hris_id": org_unit.orgUnitId,
        "hris_source": "successfactors",
        "parent_hris_id": org_unit.parentOrgUnitId
    }
```

### **Step 3: Store in Database**

The sync process stores transformed data:

1. **Create/Link Org Units** (resolve parent relationships)
2. **Create/Link Positions** (resolve org_unit_id and reports_to)
3. **Create/Link Employees** (resolve position_id)

---

## 📋 Sync Process Flow

### **Full Sync Workflow**

```
1. Authenticate with SuccessFactors
   ↓
2. Fetch all Org Units
   ├─ Transform to internal format
   ├─ Resolve parent relationships (using hris_id)
   └─ Insert/Update org_unit table
   ↓
3. Fetch all Positions
   ├─ Transform to internal format
   ├─ Resolve org_unit_id (lookup by hris_id)
   ├─ Resolve reports_to_position_id (lookup by hris_id)
   └─ Insert/Update position table
   ↓
4. Fetch all Users (Employees)
   ├─ Transform to internal format
   ├─ Resolve position_id (lookup by hris_id)
   └─ Insert/Update employee table
   ↓
5. Build Org Chart Tree
   ├─ Query root positions (reports_to_position_id IS NULL)
   ├─ Recursively build hierarchy
   └─ Return tree structure
```

---

## 🎯 Org Chart Building

After data is synced, the org chart is built from the `position` table:

```python
# backend/org-service/app/services/chart_builder.py

# 1. Find root positions (no manager)
root_positions = SELECT * FROM position 
WHERE reports_to_position_id IS NULL 
AND status = 'Active'

# 2. For each root, recursively fetch children
def build_tree(position_id):
    children = SELECT * FROM position 
    WHERE reports_to_position_id = position_id
    AND status = 'Active'
    
    for child in children:
        child.children = build_tree(child.id)
    
    return children

# 3. Attach employee data
position.employee = SELECT * FROM employee 
WHERE position_id = position.id
```

---

## 🔍 Field Resolution Strategy

### **Resolving Foreign Keys**

When syncing, we need to resolve SuccessFactors IDs to internal UUIDs:

```python
# Example: Resolve org_unit_id from SuccessFactors orgUnitId

# 1. First, check if org unit exists by hris_id
existing_org_unit = await db.execute(
    select(OrgUnit).where(OrgUnit.hris_id == sf_org_unit_id)
)

if existing_org_unit:
    org_unit_id = existing_org_unit.id
else:
    # Create new org unit first
    new_org_unit = OrgUnit(
        hris_id=sf_org_unit_id,
        code=sf_code,
        name=sf_name,
        ...
    )
    await db.add(new_org_unit)
    await db.commit()
    org_unit_id = new_org_unit.id
```

### **Handling Parent Relationships**

```python
# Resolve parent_org_unit_id

if sf_parent_org_unit_id:
    parent = await db.execute(
        select(OrgUnit).where(OrgUnit.hris_id == sf_parent_org_unit_id)
    )
    if parent:
        parent_org_unit_id = parent.id
    else:
        # Parent not synced yet - mark for later resolution
        parent_org_unit_id = None
        # Store parent_hris_id for later
        pending_parents.append({
            'child_id': org_unit_id,
            'parent_hris_id': sf_parent_org_unit_id
        })
```

---

## 📝 Sync API Endpoints

### **Start Sync**

```bash
POST /api/v1/hris/sync/start
Content-Type: application/json

{
  "connection_id": "uuid-of-connection",
  "sync_type": "full",  # or "incremental"
  "entities": ["employees", "positions", "org_units"]
}
```

### **Check Sync Status**

```bash
GET /api/v1/hris/sync/{sync_id}
```

### **Fetch Data Directly (Test)**

```bash
# Fetch org units
GET /api/v1/hris/successfactors/org-units?company_id=XXX&username=YYY&password=ZZZ

# Fetch positions
GET /api/v1/hris/successfactors/positions?company_id=XXX&username=YYY&password=ZZZ

# Fetch users
GET /api/v1/hris/successfactors/users?company_id=XXX&username=YYY&password=ZZZ
```

---

## ✅ Verification Checklist

After sync, verify data:

```sql
-- Check org units synced
SELECT COUNT(*) FROM org_unit WHERE hris_source = 'successfactors';

-- Check positions synced
SELECT COUNT(*) FROM position WHERE hris_id IS NOT NULL;

-- Check employees synced
SELECT COUNT(*) FROM employee WHERE hris_source = 'successfactors';

-- Check hierarchy is built
SELECT 
  p.position_title,
  e.first_name || ' ' || e.last_name as employee_name,
  ou.name as org_unit
FROM position p
LEFT JOIN employee e ON e.position_id = p.id
LEFT JOIN org_unit ou ON ou.id = p.org_unit_id
WHERE p.status = 'Active'
LIMIT 10;
```

---

## 🐛 Troubleshooting

### **Issue: Parent relationships not resolved**

**Solution**: Ensure parent org units are synced before children. Sync order:
1. Org Units (top-down)
2. Positions
3. Employees

### **Issue: Duplicate records**

**Solution**: Use `hris_id` as unique identifier. Check for duplicates:
```sql
SELECT hris_id, COUNT(*) 
FROM org_unit 
WHERE hris_source = 'successfactors'
GROUP BY hris_id 
HAVING COUNT(*) > 1;
```

### **Issue: Missing data in org chart**

**Solution**: 
1. Check if positions have `reports_to_position_id` set correctly
2. Verify root positions exist (where `reports_to_position_id IS NULL`)
3. Check position status is 'Active'

---

## 📚 Related Files

- `backend/hris-service/app/services/successfactors_client.py` - OData API client
- `backend/hris-service/app/services/data_transformer.py` - Data transformation
- `backend/hris-service/app/routers/sync.py` - Sync endpoints
- `backend/org-service/app/services/chart_builder.py` - Org chart building
- `SUCCESSFACTORS_INTEGRATION_GUIDE.md` - Connection setup guide

---

## 🚀 Quick Start

1. **Connect SuccessFactors** (via frontend UI or API)
2. **Test Connection** - Verify credentials work
3. **Start Full Sync** - Sync all entities
4. **Verify Data** - Check tables have data
5. **View Org Chart** - Open frontend and see your org structure!

---

**Next Step**: After tables are created, start the HRIS service and begin syncing data!
