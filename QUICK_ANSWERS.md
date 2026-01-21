# Quick Answers to Your Questions

## 1. How to Manipulate Data During Mapping?

**Answer:** Use **Transform Functions** in the mapping UI.

### Steps:
1. In the mapping table, select a source field (e.g., `createdDateTime`)
2. Select a target field (e.g., `effective_start_date`)
3. Click the **"Transform"** button (or dropdown)
4. Choose a transformation:
   - `date_format('SUCCESSFACTORS','YYYY-MM-DD')` - Convert SuccessFactors date format
   - `uppercase` - Convert text to uppercase
   - `status_active` - Convert status codes to Active/Inactive
   - `trim` - Remove whitespace
   - `default('N/A')` - Use default if empty

### Example:
```
Source: createdDateTime = "/Date(1234567890000)/"
Transform: date_format('SUCCESSFACTORS','YYYY-MM-DD')
Result: "2009-02-13"
```

**See:** `MAPPING_DATA_TRANSFORMATION_GUIDE.md` for complete list of transformations.

---

## 2. What Do Field Types Mean?

**Answer:** Field types indicate the **data type** in SuccessFactors.

| Type | Meaning | Example |
|------|---------|---------|
| **String** | Text data | `"John Doe"`, `"Sales"` |
| **Int32/Int64** | Integer numbers | `123`, `456789` |
| **Decimal** | Decimal numbers | `123.45` |
| **Boolean** | True/False | `true`, `false` |
| **DateTime** | Date and time | `2024-01-15T10:30:00` |
| **DateTimeOffset** | Date/time with timezone | `2024-01-15T10:30:00+00:00` |
| **Guid** | Unique identifier | `550e8400-e29b-41d4...` |

**In the UI:** Field types are shown in the "Type" column of the mapping table.

---

## 3. Last Modified Date & Record Status

**Answer:** OrgChartAI uses multiple fields to track record status:

### Primary Status Fields:

1. **`status`** (Primary)
   - Values: `Active`, `Inactive`, `Planned`
   - Direct status indicator

2. **`effective_end_date`** (Time-based)
   - `NULL` = Currently active
   - `Date in past` = Inactive/deleted
   - `Date in future` = Planned

3. **`updated_at`** (Audit only)
   - Tracks when record was last changed
   - **NOT used for status** - only for audit trail

4. **`termination_date`** (Employees only)
   - When employee left organization
   - If set, `status` should be `Inactive`

### SuccessFactors Mapping:

| SF Field | OrgChartAI Field | Purpose |
|----------|------------------|---------|
| `effectiveEndDate` | `effective_end_date` | End date (NULL = active) |
| `status` | `status` | Active/Inactive |
| `lastModifiedDateTime` | `updated_at` | Last change (audit) |
| `terminationDate` | `termination_date` | Employee termination |

### Logic:
- **ACTIVE**: `status='Active'` AND `effective_end_date IS NULL`
- **INACTIVE**: `status='Inactive'` OR `effective_end_date < NOW()`

---

## 4. Settings & Sync History Tabs

### Settings Tab:
- **Connection Configuration**: Edit name, API URL, credentials
- **Authentication**: Change auth method, update credentials
- **Sync Configuration**: Set sync frequency, enable auto-sync
- **Advanced**: Data validation, conflict resolution

### Sync History Tab:
- **Sync Logs**: Date, time, status (Success/Failed/Partial)
- **Records Synced**: Count of org units, positions, employees
- **Details**: Entities synced, mappings applied, errors
- **Statistics**: Total synced, success rate, last sync

**Location:** In the Connection Card, click "Settings" or "Sync History" tabs.

---

## 5. Where Are Mappings Saved? (No Data in Neon DB)

**Answer:** Mappings are saved in PostgreSQL (Neon) in the `hris_field_mapping` table.

### Why You Might Not See Data:

1. **Wrong Connection ID**
   - Each connection has a unique `connection_id`
   - Query: `SELECT * FROM hris_field_mapping WHERE connection_id = 'conn-xxxxx'`

2. **Inactive Mappings**
   - Only `is_active = TRUE` mappings are shown
   - Old mappings are deactivated when new ones are saved

3. **Entity Type Filter**
   - Mappings are grouped by `entity_type` (`org_unit`, `position`, `employee`)
   - Query specific type: `WHERE entity_type = 'org_unit'`

4. **Table Doesn't Exist**
   - Run: `SELECT * FROM hris_field_mapping LIMIT 1;`
   - If error, run: `python backend/hris-service/setup_mapping_tables.py`

### Verify Mappings:

**API Endpoint:**
```
GET /api/v1/hris/connections/{connection_id}/mapping/verify
```

**SQL Query:**
```sql
SELECT 
    entity_type,
    source_field,
    target_field,
    mapping_type,
    transform_function,
    created_at
FROM hris_field_mapping
WHERE connection_id = 'conn-1768837168885'
AND is_active = TRUE
ORDER BY entity_type, source_field;
```

### Database Tables:

- **`hris_field_mapping`**: Stores individual field mappings
- **`hris_mapping_config`**: Stores mapping configuration metadata

**Both tables are in your Neon PostgreSQL database.**

---

## Quick Reference

| Question | Answer |
|----------|--------|
| **Transform data?** | Use transform functions in mapping UI |
| **Field types?** | String, Int, Decimal, Boolean, DateTime, etc. |
| **Record status?** | `status` + `effective_end_date` |
| **Settings tab?** | Connection config, auth, sync settings |
| **Sync history?** | Shows all sync operations with details |
| **Where saved?** | PostgreSQL `hris_field_mapping` table |
| **Verify mappings?** | Use `/mapping/verify` endpoint or SQL query |

---

## Need More Details?

- **Data Transformation**: See `MAPPING_DATA_TRANSFORMATION_GUIDE.md`
- **Field Mapping**: See `SUCCESSFACTORS_MAPPING_UI_GUIDE.md`
- **Database Schema**: See `database/hris_mapping_schema.sql`
