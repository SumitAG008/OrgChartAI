# Complete Data Sync Flow: SuccessFactors API → OrgChart AI

## 🔄 Complete Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SUCCESSFACTORS API                           │
│  (FOLegalEntity, FODepartment, Position, PerPerson, etc.)        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ OData API Calls
                            │ (GET /odata/v2/EntityName)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              HRIS-SERVICE (Port 8002)                           │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  1. SuccessFactorsClient                                        │
│     • Authenticates with SF API                                 │
│     • Fetches raw data from SF entities                         │
│     • Handles pagination                                        │
│                                                                  │
│  2. SyncService                                                 │
│     • Gets field mappings from database                         │
│     • Applies transformations                                   │
│     • Transforms SF data → Internal format                      │
│                                                                  │
│  3. Data Transformation                                         │
│     • Maps fields: externalCode → hris_id                      │
│     • Applies transforms: status_active, lowercase, etc.        │
│     • Validates relationships                                   │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP POST /api/v1/{entity}/bulk
                            │ JSON: {"records": [transformed_data]}
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              ORG-SERVICE (Port 8000)                            │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  1. Bulk Endpoints                                              │
│     • POST /api/v1/org-units/bulk                               │
│     • POST /api/v1/positions/bulk                               │
│     • POST /api/v1/employees/bulk                               │
│                                                                  │
│  2. Upsert Logic                                                │
│     • Checks if record exists by hris_id                       │
│     • Updates existing or creates new                          │
│     • Maintains relationships                                   │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ SQL INSERT/UPDATE
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE (Neon)                          │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  Tables:                                                        │
│  • org_unit (Legal Entities, Departments, etc.)                │
│  • position (Positions from SF)                                 │
│  • employee (People from PerPerson/User)                        │
│                                                                  │
│  Key Fields:                                                    │
│  • hris_id: Links to SF record                                  │
│  • hris_source: "successfactors"                                │
│  • hris_type: "FOLegalEntity", "FODepartment", etc.           │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ SQL SELECT
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              FRONTEND (Port 3000)                                │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  1. React Query                                                  │
│     • GET /api/v1/org-chart                                      │
│     • Fetches hierarchical structure                            │
│                                                                  │
│  2. OrgChartCanvas Component                                     │
│     • Renders tree structure                                    │
│     • Shows nodes with relationships                            │
│     • Displays AI Agents, positions, people                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Step-by-Step Data Flow

### Step 1: User Initiates Sync

**Frontend:** User clicks "Auto Sync" button
```typescript
// frontend/src/components/HRIS/ConnectionCard.tsx
autoSyncMutation.mutate({
  company_id: "SFHUB003674",
  username: "sfadmin",
  password: "***",
  api_url: "https://apisalesdemo2.successfactors.eu"
})
```

**API Call:**
```
POST http://localhost:8002/api/v1/hris/auto-sync/start?connection_id=conn-xxx
Body: {
  "company_id": "SFHUB003674",
  "username": "sfadmin",
  "password": "***",
  "api_url": "https://apisalesdemo2.successfactors.eu"
}
```

### Step 2: Backend Discovers Entities

**HRIS Service:**
```python
# backend/hris-service/app/routers/auto_sync.py

# 1. Fetch $metadata from SuccessFactors
metadata_url = f"{api_url}/odata/v2/$metadata"
metadata_xml = await fetch_metadata(metadata_url)

# 2. Parse entities
parser = MetadataParser(metadata_xml)
entities = parser.get_all_entities()
# Returns: ["FOLegalEntity", "FODepartment", "Position", "PerPerson", ...]

# 3. Filter for org structure entities
org_entities = ["FOLegalEntity", "FODepartment", "FODivision", 
                 "FOBusinessUnit", "FOCostCenter", "Position", 
                 "PerPerson", "User"]
```

### Step 3: Create Default Mappings

**HRIS Service:**
```python
# Create mappings in database
for entity_name in found_entities:
    if entity_name == "FOLegalEntity":
        mappings = [
            {"source": "externalCode", "target": "hris_id"},
            {"source": "name", "target": "name"},
            {"source": "status", "target": "status", "transform": "status_active"},
            {"source": "parent", "target": "parent_id"},
        ]
    # Save to hris_field_mapping table
```

### Step 4: Fetch Data from SuccessFactors

**HRIS Service → SuccessFactors API:**
```python
# backend/hris-service/app/services/successfactors_client.py

# Authenticate
auth_string = f"{username}@{company_id}:{password}"
encoded = base64.b64encode(auth_string.encode()).decode()
headers = {"Authorization": f"Basic {encoded}"}

# Fetch FOLegalEntity
response = await client.get(
    f"{api_url}/odata/v2/FOLegalEntity",
    headers=headers
)

# Returns OData format:
{
  "d": {
    "results": [
      {
        "externalCode": "LE001",
        "name": "Acme Corporation",
        "status": "ACTIVE",
        "parent": null,
        ...
      },
      ...
    ]
  }
}
```

### Step 5: Transform Data

**HRIS Service:**
```python
# backend/hris-service/app/services/sync_service.py

# Apply mappings
for source_record in sf_data:
    transformed = {}
    
    # Map fields
    for mapping in mappings:
        source_value = source_record[mapping["source"]]
        
        # Apply transformation
        if mapping["transform"] == "status_active":
            transformed[mapping["target"]] = "active" if source_value == "ACTIVE" else "inactive"
        else:
            transformed[mapping["target"]] = source_value
    
    # Add metadata
    transformed["hris_id"] = source_record["externalCode"]
    transformed["hris_source"] = "successfactors"
    transformed["hris_type"] = "FOLegalEntity"
    
    transformed_data.append(transformed)

# Result:
[
  {
    "hris_id": "LE001",
    "name": "Acme Corporation",
    "status": "active",
    "parent_id": null,
    "hris_source": "successfactors",
    "hris_type": "FOLegalEntity"
  },
  ...
]
```

### Step 6: Send to Org Service

**HRIS Service → Org Service:**
```python
# backend/hris-service/app/routers/auto_sync.py

async def send_to_org_service(entity_type: str, data: List[Dict]):
    org_service_url = "http://localhost:8000/api/v1"
    
    endpoint_map = {
        "org_unit": f"{org_service_url}/org-units/bulk",
        "position": f"{org_service_url}/positions/bulk",
        "employee": f"{org_service_url}/employees/bulk"
    }
    
    endpoint = endpoint_map[entity_type]
    
    # POST to org-service
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json={"records": data}
        )
```

### Step 7: Org Service Upserts Data

**Org Service:**
```python
# backend/org-service/main.py

@app.post("/api/v1/org-units/bulk")
async def bulk_create_org_units(records: Dict[str, Any], db=Depends(get_db)):
    for record_data in records.get("records", []):
        hris_id = record_data.get("hris_id")
        
        # Check if exists
        existing = await org_service.get_org_unit_by_hris_id(db, hris_id)
        
        if existing:
            # Update
            for key, value in record_data.items():
                setattr(existing, key, value)
            await db.commit()
        else:
            # Create
            db_org_unit = OrgUnit(**record_data)
            db.add(db_org_unit)
            await db.commit()
```

### Step 8: Data Stored in Database

**PostgreSQL (Neon):**
```sql
-- org_unit table
INSERT INTO org_unit (
    id, hris_id, name, status, parent_id, 
    hris_source, hris_type, created_at
) VALUES (
    gen_random_uuid(),
    'LE001',
    'Acme Corporation',
    'active',
    NULL,
    'successfactors',
    'FOLegalEntity',
    NOW()
) ON CONFLICT (hris_id) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    updated_at = NOW();
```

### Step 9: Frontend Fetches Data

**Frontend:**
```typescript
// frontend/src/components/OrgChart/OrgChartCanvas.tsx

const { data: orgChartData } = useQuery({
  queryKey: ['orgChart'],
  queryFn: () => fetchOrgChart()
});

// API Call:
// GET http://localhost:8000/api/v1/org-chart
```

**Org Service Response:**
```json
{
  "tree": {
    "id": "uuid",
    "person": {
      "name": "Acme Corporation",
      "title": "Legal Entity",
      "email": null
    },
    "children": [
      {
        "id": "uuid",
        "person": {
          "name": "Engineering Department",
          "title": "Department"
        },
        "children": [...]
      }
    ]
  }
}
```

### Step 10: Org Chart Renders

**Frontend:**
```typescript
// frontend/src/components/OrgChart/OrgChartRenderer.tsx

<OrgNode
  node={node}
  displayProperties={displayProperties}
  onClick={() => onNodeClick(node)}
/>

// Renders hierarchical tree with:
// - CEO at top
// - Departments below
// - Positions in departments
// - People in positions
// - AI Agents highlighted in purple
```

## 🔧 Entity Mapping

### SuccessFactors → Internal Structure

| SuccessFactors Entity | Internal Entity | Example Fields |
|----------------------|-----------------|----------------|
| `FOLegalEntity` | `org_unit` | name, code, status, parent_id |
| `FODepartment` | `org_unit` | name, code, status, parent_id |
| `FODivision` | `org_unit` | name, code, status, parent_id |
| `FOBusinessUnit` | `org_unit` | name, code, status, parent_id |
| `FOCostCenter` | `org_unit` | name, code, status, parent_id |
| `Position` | `position` | title, code, org_unit_id, status |
| `PerPerson` | `employee` | first_name, last_name, email, status |
| `User` | `employee` | first_name, last_name, email, status |

## 🎯 Key Components

### 1. SuccessFactorsClient
- **Location:** `backend/hris-service/app/services/successfactors_client.py`
- **Purpose:** Handles all SF API interactions
- **Methods:**
  - `authenticate()` - OAuth/Basic Auth
  - `get_legal_entities()` - Fetch FOLegalEntity
  - `get_departments()` - Fetch FODepartment
  - `get_positions()` - Fetch Position
  - `get_per_person()` - Fetch PerPerson

### 2. SyncService
- **Location:** `backend/hris-service/app/services/sync_service.py`
- **Purpose:** Orchestrates data sync
- **Methods:**
  - `fetch_and_transform_data()` - Fetch + transform
  - `sync_entity()` - Sync single entity
  - `sync_all_entities()` - Sync all entities

### 3. DataTransformer
- **Location:** `backend/hris-service/app/services/data_transformer.py`
- **Purpose:** Transforms SF data to internal format
- **Methods:**
  - `transform_successfactors_org_unit()`
  - `transform_successfactors_position()`
  - `transform_successfactors_employee()`

### 4. Org Service Bulk Endpoints
- **Location:** `backend/org-service/main.py`
- **Endpoints:**
  - `POST /api/v1/org-units/bulk`
  - `POST /api/v1/positions/bulk`
  - `POST /api/v1/employees/bulk`

## 🚀 Complete Sync Process

1. **User Action:** Click "Auto Sync" → Enter credentials
2. **Discovery:** Backend fetches `$metadata` → Discovers entities
3. **Mapping:** Creates default field mappings → Saves to database
4. **Fetch:** Calls SF API for each entity → Gets raw data
5. **Transform:** Applies mappings → Transforms to internal format
6. **Send:** POST to org-service bulk endpoints
7. **Upsert:** Org-service checks `hris_id` → Updates or creates
8. **Store:** Data saved to PostgreSQL
9. **Fetch:** Frontend calls `/api/v1/org-chart`
10. **Render:** Org chart displays hierarchical structure

## ✅ Result

**Org Chart displays:**
- Legal Entities (top level)
- Departments (under entities)
- Divisions, Business Units, Cost Centers
- Positions (in org units)
- People (in positions)
- AI Agents (highlighted in purple)

**All synced from SuccessFactors automatically!** 🎉
