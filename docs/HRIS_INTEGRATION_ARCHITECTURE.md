# HRIS Integration Architecture
## System of Record vs System of Insight

---

## 🎯 1. Core Principle: HRIS Is the "System of Record"

Your org-visualization product is a **System of Insight**, not the master.

**HRIS remains the authoritative source for:**
- Organization Units
- Positions
- Jobs
- Employees
- Assignments
- Cost Centers / Locations / Legal Entities

Your product **consumes** this data, **visualizes** it, **enriches** it, and **optionally sends back approved changes**.

---

## 🧱 2. Complete Data Model (Tables)

### **A. Organization Structure Tables**

#### **1. org_unit**

| Field | Description |
|-------|-------------|
| `id` | Unique ID (UUID) |
| `code` | Department/BU code (e.g., "FIN-UK-001") |
| `name` | Name |
| `parent_org_unit_id` | Hierarchy (nullable, self-referencing) |
| `type` | Division, Dept, Region, LegalEntity, CostCenterOwner |
| `cost_center_id` | Link to finance |
| `location_id` | Country/City |
| `legal_entity_id` | Legal entity association |
| `scope` | Global, Regional, Country, Local |
| `tree_id` | Which org tree (for M&A scenarios: "Current", "Future", "Scenario A") |
| `effective_start_date` | For time travel |
| `effective_end_date` | For future changes |
| `status` | Active/Planned/Inactive |

**Key Design Decisions:**
- `parent_org_unit_id = NULL` → top-level org unit
- `tree_id` supports parallel structures for M&A scenarios
- `scope` indicates geographic/operational scope

#### **2. position**

| Field | Description |
|-------|-------------|
| `id` | Unique ID (UUID) |
| `org_unit_id` | Belongs to which unit |
| `job_id` | Generic job profile |
| `position_code` | Unique seat code |
| `position_title` | Display title |
| `position_type` | Permanent/Contract/Temp |
| `reports_to_position_id` | Reporting line (nullable) |
| `fte` | 0-1 (Full-time equivalent) |
| `grade` | Level |
| `is_managerial` | Boolean flag |
| `is_mass_position_template` | Boolean flag |
| `status` | Active/Vacant/Frozen |
| `effective_start_date` | Time travel |
| `effective_end_date` | Future changes |

#### **3. job**

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `job_code` | Standard job code |
| `job_title` | Title |
| `job_family` | e.g., Engineering |
| `job_sub_family` | e.g., Backend |
| `default_grade` | Optional |
| `default_position_type` | Optional |
| `description` | Optional |

### **B. Employee Tables**

#### **4. employee**

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `employee_number` | HRIS ID |
| `first_name` | |
| `last_name` | |
| `preferred_name` | Display name |
| `email` | |
| `employment_type` | Permanent/Contract/Temp |
| `legal_entity_id` | Payroll entity |
| `primary_position_id` | Seat they occupy |
| `hire_date` | |
| `termination_date` | Nullable |
| `status` | Active/OnLeave/Terminated |

#### **5. assignment**

Used for temporary moves, dotted-line reporting, project roles.

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `employee_id` | Employee reference |
| `position_id` | Seat |
| `assignment_type` | Primary/Secondary/Temporary |
| `reports_to_position_id` | Dotted-line (nullable) |
| `start_date` | |
| `end_date` | Nullable |
| `status` | Active/Completed |

### **C. Supporting Tables**

#### **6. location**

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `code` | Location code |
| `name` | Location name |
| `country` | Country code |
| `city` | City name |
| `timezone` | Timezone |

#### **7. cost_center**

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `code` | Cost center code |
| `name` | Cost center name |
| `region` | Region |

#### **8. legal_entity**

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `code` | Legal entity code |
| `name` | Legal entity name |
| `country` | Country of incorporation |

#### **9. org_attribute_definition**

Flexible metadata system (recommended by HR tech frameworks).

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `object_type` | OrganizationUnit, Position, Employee |
| `code` | e.g., "BAND", "SUCCESSION_RISK" |
| `label` | Display label |
| `data_type` | String, Number, Boolean, Date, Enum |
| `allowed_values` | JSON for enums (nullable) |

#### **10. org_attribute_value**

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `object_type` | OrganizationUnit, Position, Employee |
| `object_id` | Reference to object |
| `attribute_definition_id` | Reference to definition |
| `value` | Stringified, interpreted by data_type |

### **D. M&A Mapping Tables**

#### **11. org_unit_mapping**

For mergers, acquisitions, and restructuring scenarios.

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `source_org_unit_id` | From Company A |
| `target_org_unit_id` | To Company B |
| `mapping_type` | Merge/Split/Move |
| `scenario_id` | Which scenario this mapping belongs to |
| `effective_date` | When mapping takes effect |

---

## 🔄 3. How HRIS Sends Data to Your Product (Integration Patterns)

### **Option 1 — API Pull (Your system pulls from HRIS)**

**How it works:**
- HRIS exposes REST/SOAP APIs
- Your system calls:
  - `GET /orgUnits`
  - `GET /positions`
  - `GET /jobs`
  - `GET /employees`
  - `GET /assignments`

**Pros:**
- Real-time, controlled
- You control sync frequency
- Better error handling

**Cons:**
- HRIS must support APIs
- Requires API credentials management
- Rate limiting considerations

**Implementation:**
```typescript
// Scheduled sync job
async function syncFromHRIS() {
  const orgUnits = await hrisClient.getOrgUnits();
  const positions = await hrisClient.getPositions();
  const employees = await hrisClient.getEmployees();
  // Transform and store
}
```

### **Option 2 — HRIS Push (HRIS sends data to you)**

**How it works:**
- HRIS sends JSON/CSV/XML to your endpoint or SFTP
- Triggered daily or hourly
- Your system receives and processes

**Pros:**
- Works with older HRIS systems
- No API dependencies
- Batch processing efficient

**Cons:**
- Not real-time
- File format dependencies
- Requires file parsing logic

**Implementation:**
```typescript
// Webhook endpoint
POST /api/hris/webhook
{
  "source": "workday",
  "dataType": "orgUnits",
  "payload": [...]
}
```

### **Option 3 — Event-Based (Best for M&A, restructuring)**

**How it works:**
- HRIS publishes events:
  - `OrgUnitCreated`
  - `PositionChanged`
  - `EmployeeMoved`
- Your system subscribes to event stream

**Pros:**
- Real-time, scalable
- Event-driven architecture
- Efficient for large orgs

**Cons:**
- Requires modern HRIS
- Event ordering complexity
- Requires message queue infrastructure

**Implementation:**
```typescript
// Event consumer
kafkaConsumer.on('OrgUnitCreated', async (event) => {
  await processOrgUnitChange(event);
});
```

---

## 📤 4. How Your System Sends Data Back to HRIS

Your product should **not overwrite HRIS data directly**.

Instead, follow a **governance workflow**:

### **Step 1 — User proposes a change**

**Examples:**
- Move a department
- Create new positions
- Freeze positions
- Change reporting lines

### **Step 2 — Your system generates a "Change Package"**

**Example JSON:**
```json
{
  "changeType": "PositionMove",
  "positionId": "POS-123",
  "newReportsTo": "POS-001",
  "effectiveDate": "2026-02-01",
  "reason": "Restructure",
  "requestedBy": "user-456",
  "scenarioId": "scenario-789"
}
```

### **Step 3 — HR reviews & approves**

- HRBP or Org Design team approves
- Approval workflow with notifications
- Audit trail maintained

### **Step 4 — HRIS API receives the approved change**

**Endpoints:**
- `POST /applyOrgChange`
- `PUT /updatePosition`
- `PUT /updateOrgUnit`

### **Step 5 — HRIS becomes the new source of truth**

- HRIS updates
- HRIS sends updated data back to your system
- Your visualization refreshes

This aligns with HR ecosystem architecture principles.

---

## 🔀 5. Special Case: Mergers & Acquisitions (M&A)

Your system must support:

### **A. Parallel Structures**

- **"Current State"** → Live HRIS data
- **"Future State"** → Proposed structure
- **"Scenario A"** → Alternative option
- **"Scenario B"** → Another alternative

**Implementation:**
- Use `tree_id` in `org_unit` table
- Each scenario has its own `tree_id`
- Compare scenarios side-by-side

### **B. Mapping Tables**

| Field | Description |
|-------|-------------|
| `source_org_unit_id` | From Company A |
| `target_org_unit_id` | To Company B |
| `mapping_type` | Merge/Split/Move |

### **C. Simulation Mode**

- **No changes sent to HRIS**
- Only after approval → push change package
- Users can experiment without risk

---

## 📊 6. Headcount, Vacancies, Org Intelligence

Your system calculates:

### **Headcount**

Count of employees with:
- `status = Active`
- `assignment_type = Primary`

**SQL Example:**
```sql
SELECT COUNT(*) 
FROM employee e
JOIN assignment a ON e.primary_position_id = a.position_id
WHERE e.status = 'Active' 
  AND a.assignment_type = 'Primary'
  AND a.status = 'Active';
```

### **Vacancies**

Positions where:
- `status = Active`
- AND no active primary assignment

**SQL Example:**
```sql
SELECT p.*
FROM position p
LEFT JOIN assignment a ON p.id = a.position_id 
  AND a.assignment_type = 'Primary' 
  AND a.status = 'Active'
WHERE p.status = 'Active'
  AND a.id IS NULL;
```

### **Span of Control**

Count of direct reports per manager

**SQL Example:**
```sql
SELECT 
  manager.position_id,
  COUNT(direct_report.id) as span_of_control
FROM position manager
LEFT JOIN position direct_report 
  ON direct_report.reports_to_position_id = manager.id
WHERE manager.is_managerial = true
GROUP BY manager.position_id;
```

### **Org Health Metrics**

- Permanent vs Contract ratio
- Attrition impact
- Workforce cost (if HRIS sends comp data)

These insights rely on the clean data model above.

---

## 🚀 7. Recommended Integration Architecture

```
HRIS (System of Record)
        ↓ (API/SFTP/Events)
Org Visualization Engine (Your Product)
        ↓
Scenario Builder / Org Designer
        ↓
Approval Workflow
        ↓
Change Package API
        ↓
HRIS (Applies approved changes)
```

This matches modern HR technology ecosystem patterns.

---

## 🌍 8. Geographic and Legal Entity Structure

### **Where does an org unit "belong"?**

You decide this through three master dimensions:

1. **Legal entity** → who employs/payrolls people
2. **Location / country** → where the org unit operates
3. **Org hierarchy root** → what sits at the very top

### **A. Country / Geography**

In your `org_unit` table, don't store country directly—link it:

- `org_unit.location_id` → `location.id`
- `location` has: `country`, `city`, `timezone`

**This way:**
- A global function (e.g., "Global Engineering") can be "multi-country" via its child units.
- A local department (e.g., "Sales UK") is clearly tied to `location.country = "UK"`.

**You can also add:**
- `org_unit.scope` → Global, Regional, Country, Local

### **B. What is the "top" of the org structure?**

You define the top by parent relationships:

- `org_unit.parent_org_unit_id = NULL` → top-level org unit
- You can have:
  - One root → "Global Group"
  - Or multiple roots → each legal entity as its own tree

**For M&A and holding structures, you can support:**
- `org_unit.tree_id` → which "org tree" it belongs to (e.g., "Current", "Future", "Scenario A").

---

## 📋 9. Data Sync Strategy

### **Initial Load**
1. Full data export from HRIS
2. Transform to your schema
3. Load into database
4. Build org hierarchy
5. Calculate metrics

### **Incremental Sync**
1. Poll for changes (API) or receive events
2. Identify changed records
3. Update database
4. Recalculate affected metrics
5. Refresh visualizations

### **Conflict Resolution**
- HRIS always wins for master data
- Your system maintains scenario/planning data separately
- Merge strategy: Last-write-wins with audit log

---

## 🔐 10. Security & Compliance

### **Data Security**
- Encrypt data in transit (TLS)
- Encrypt data at rest
- Secure credential storage for HRIS connections
- API key rotation

### **Access Control**
- Role-based access to HRIS connections
- Audit logs for all data access
- Data residency compliance

### **Compliance**
- GDPR: Right to deletion
- SOC 2: Security controls
- Data retention policies

---

## 📚 Next Steps

This architecture document provides the foundation for:
- API contract design (request/response schemas)
- Database schema (DDL for PostgreSQL)
- Event model (Kafka topics)
- Scenario planning engine
- M&A simulation UI

**See related documents:**
- `DATABASE_SCHEMA.md` - Complete DDL
- `API_CONTRACTS.md` - API specifications
- `AI_RECOMMENDATION_ENGINE.md` - AI/ML architecture
