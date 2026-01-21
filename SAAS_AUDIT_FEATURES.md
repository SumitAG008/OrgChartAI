# SaaS Audit & Versioning Features
## Complete Timestamp Tracking and Change History

---

## 🎯 Overview

This SaaS application includes comprehensive audit trail and versioning capabilities, tracking every change with full timestamp and user information.

---

## 📊 Timestamp Fields in All Tables

Every table includes these standard fields:

### **Standard Audit Fields**

```sql
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
created_by UUID NOT NULL
updated_by UUID
version INTEGER NOT NULL DEFAULT 1
```

### **Effective Dating Fields**

```sql
effective_start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
effective_end_date TIMESTAMP
```

**Key Points:**
- All dates are **TIMESTAMP** (not DATE) for precise tracking
- Supports **multiple changes per day**
- **created_by** is required (NOT NULL)
- **version** increments automatically on updates
- **effective_start_date** and **effective_end_date** use TIMESTAMP

---

## 🔍 Change History Tracking

### **change_history Table**

Tracks **every change** to any record:

```sql
CREATE TABLE change_history (
    id UUID PRIMARY KEY,
    table_name TEXT NOT NULL,           -- Which table
    record_id UUID NOT NULL,            -- Which record
    action TEXT NOT NULL,               -- INSERT, UPDATE, DELETE
    old_values JSONB,                   -- Previous values
    new_values JSONB,                   -- New values
    changed_fields TEXT[],              -- Which fields changed
    changed_by UUID NOT NULL,           -- Who made the change
    changed_at TIMESTAMP NOT NULL,      -- When (precise timestamp)
    change_reason TEXT,                 -- Optional reason
    ip_address INET,                   -- Where from
    user_agent TEXT                     -- Browser/client info
);
```

### **Features**

- **Tracks all changes** - INSERT, UPDATE, DELETE
- **Stores old and new values** as JSONB
- **Lists changed fields** for quick review
- **Includes user context** (who, when, where)
- **Supports multiple changes per day** (TIMESTAMP precision)

---

## 📚 Version History

### **version_history Table**

Maintains **version snapshots** of records:

```sql
CREATE TABLE version_history (
    id UUID PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    version INTEGER NOT NULL,           -- Version number
    data JSONB NOT NULL,                -- Complete record snapshot
    created_at TIMESTAMP NOT NULL,      -- When this version was created
    created_by UUID NOT NULL,           -- Who created this version
    change_summary TEXT                 -- What changed
);
```

### **Features**

- **Complete snapshots** of each version
- **Time-travel queries** - See record at any point in time
- **Version restoration** - Restore to any previous version
- **Change summaries** for quick understanding

---

## 🔄 Automatic Triggers

### **Timestamp Updates**

Automatic triggers update `updated_at` and `version` on every UPDATE:

```sql
CREATE TRIGGER update_org_unit_timestamp
    BEFORE UPDATE ON org_unit
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Result:**
- `updated_at` = CURRENT_TIMESTAMP
- `version` = OLD.version + 1

### **Change History Creation**

Automatic triggers create change history entries:

```sql
CREATE TRIGGER audit_org_unit_changes
    AFTER INSERT OR UPDATE OR DELETE ON org_unit
    FOR EACH ROW
    EXECUTE FUNCTION create_change_history();
```

**Result:**
- Entry in `change_history` table
- Old and new values captured
- Changed fields identified
- User and timestamp recorded

### **Version History Creation**

Automatic triggers create version snapshots:

```sql
CREATE TRIGGER version_org_unit_changes
    AFTER UPDATE ON org_unit
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION create_version_history();
```

**Result:**
- New version entry in `version_history`
- Complete record snapshot saved
- Version number incremented

---

## 📈 API Endpoints for Audit

### **Get Change History**

```http
GET /api/v1/audit/history/{table_name}/{record_id}?limit=100
```

**Response:**
```json
[
  {
    "id": "ch-1",
    "action": "UPDATE",
    "old_values": {"name": "Engineering", "status": "Active"},
    "new_values": {"name": "Engineering", "status": "Inactive"},
    "changed_fields": ["status"],
    "changed_by": "user-uuid",
    "changed_at": "2025-01-15T14:32:15.123Z",
    "change_reason": "Department restructuring"
  }
]
```

### **Get Version at Timestamp**

```http
GET /api/v1/audit/version/{table_name}/{record_id}?timestamp=2025-01-15T10:00:00Z
```

**Response:**
```json
{
  "version": 3,
  "data": {
    "id": "ou-1",
    "name": "Engineering",
    "status": "Active",
    ...
  },
  "created_at": "2025-01-15T09:45:00Z"
}
```

### **Get All Changes Today**

```http
GET /api/v1/audit/changes-today?user_id=user-uuid
```

**Response:**
```json
[
  {
    "table_name": "org_unit",
    "record_id": "ou-1",
    "action": "UPDATE",
    "changed_fields": ["status"],
    "changed_at": "2025-01-15T14:32:15.123Z"
  },
  {
    "table_name": "position",
    "record_id": "pos-1",
    "action": "INSERT",
    "changed_fields": ["position_title", "org_unit_id"],
    "changed_at": "2025-01-15T14:35:22.456Z"
  }
]
```

### **Get All Versions**

```http
GET /api/v1/versions/{table_name}/{record_id}
```

**Response:**
```json
[
  {
    "version": 1,
    "data": {...},
    "created_at": "2025-01-15T09:00:00Z",
    "created_by": "user-uuid"
  },
  {
    "version": 2,
    "data": {...},
    "created_at": "2025-01-15T10:30:00Z",
    "created_by": "user-uuid"
  }
]
```

### **Restore Version**

```http
POST /api/v1/versions/{table_name}/{record_id}/{version}/restore?user_id=user-uuid
```

**Response:**
```json
{
  "status": "restored",
  "version": 3
}
```

---

## 🔐 Audit Middleware

### **Automatic User Tracking**

All API requests automatically track:

- **User ID** from `X-User-ID` header
- **IP Address** from request
- **User Agent** from headers
- **Timestamp** of request

### **Usage**

```python
# In your route handlers
@app.post("/api/v1/org-units")
async def create_org_unit(
    org_unit: OrgUnitCreate,
    user_id: str = Query(..., description="User ID"),
    request: Request,  # Access request state
    db=Depends(get_db)
):
    # user_id is automatically tracked
    # request.state.user_id contains user ID
    # request.state.ip_address contains IP
    return await org_service.create_org_unit(db, org_unit, user_id=user_id)
```

---

## 📊 Multiple Changes Per Day

### **Timestamp Precision**

Using **TIMESTAMP** (not DATE) allows:

- **Multiple changes** tracked precisely
- **Exact time** of each change
- **Chronological ordering** of changes
- **Time-travel queries** to any moment

### **Example**

```sql
-- Same record, multiple changes in one day
INSERT INTO change_history VALUES
  ('ch-1', 'org_unit', 'ou-1', 'UPDATE', ..., '2025-01-15 09:15:23.123'),
  ('ch-2', 'org_unit', 'ou-1', 'UPDATE', ..., '2025-01-15 14:32:15.456'),
  ('ch-3', 'org_unit', 'ou-1', 'UPDATE', ..., '2025-01-15 16:45:02.789');
```

All three changes are tracked separately with precise timestamps.

---

## 🎯 Use Cases

### **1. Compliance & Audit**

- **Track all changes** for regulatory compliance
- **Who changed what and when**
- **Complete audit trail**
- **Exportable reports**

### **2. Debugging**

- **See what changed** when issues occur
- **Compare versions** to find problems
- **Restore** to working state

### **3. Time-Travel Queries**

- **View org structure** at any point in time
- **Compare** current vs past states
- **Analyze** changes over time

### **4. User Activity**

- **Track user actions**
- **Monitor** who's making changes
- **Identify** patterns and issues

---

## 📋 Implementation Checklist

- [x] All tables have `created_at`, `updated_at` (TIMESTAMP)
- [x] All tables have `created_by`, `updated_by` (UUID)
- [x] All tables have `version` field
- [x] All date fields use TIMESTAMP
- [x] `change_history` table for audit trail
- [x] `version_history` table for versioning
- [x] Automatic triggers for timestamps
- [x] Automatic triggers for change history
- [x] Automatic triggers for version history
- [x] Audit middleware for API tracking
- [x] API endpoints for audit queries
- [x] API endpoints for version management

---

## 🚀 Benefits

1. **Complete Audit Trail** - Every change tracked
2. **Compliance Ready** - Meets regulatory requirements
3. **Debugging Support** - Easy to find what changed
4. **Time-Travel** - View data at any point in time
5. **User Accountability** - Know who did what
6. **Multiple Changes Per Day** - TIMESTAMP precision
7. **Version Control** - Restore to any version

---

**Your SaaS application now has enterprise-grade audit and versioning!** ✅
