the # Field Mapping & Data Transformation Guide

## 📋 Table of Contents
1. [Data Transformation During Mapping](#data-transformation)
2. [Field Types Explained](#field-types)
3. [Record Status & Date Tracking](#record-status)
4. [Settings & Sync History](#settings-sync)
5. [Verifying Saved Mappings](#verification)

---

## 🔄 Data Transformation During Mapping

### What is Data Transformation?

Data transformation allows you to **manipulate or convert data** from SuccessFactors before it's saved to OrgChartAI. This is useful for:

- **Format conversion**: Date formats, string cases, number formats
- **Data cleaning**: Trimming whitespace, removing special characters
- **Value mapping**: Converting status codes to readable text
- **Calculations**: Rounding numbers, adding days to dates
- **Default values**: Providing fallback values for empty fields

### How to Add Transformations

1. **In the Mapping UI:**
   - Select a source field (e.g., `createdDateTime`)
   - Select a target field (e.g., `effective_start_date`)
   - Click the **"Transform"** button or dropdown
   - Choose a transformation function
   - Enter parameters if needed

2. **Available Transform Functions:**

#### String Transformations
- `uppercase` - Convert to UPPERCASE
- `lowercase` - Convert to lowercase
- `title_case` - Convert to Title Case
- `trim` - Remove leading/trailing whitespace
- `replace('old','new')` - Replace text
- `substring(0,5)` - Extract substring
- `split(',',0)` - Split string and get part

#### Date Transformations
- `date_format('ISO','YYYY-MM-DD')` - Change date format
  - Input formats: `ISO`, `UNIX_TIMESTAMP`, `SUCCESSFACTORS`
  - Output formats: `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`
- `date_add_days(30)` - Add days to date

#### Number Transformations
- `round(2)` - Round to 2 decimal places
- `multiply(1.5)` - Multiply by factor

#### Status Transformations
- `status_active` - Convert to Active/Inactive
- `boolean` - Convert to true/false

#### Default Values
- `default('N/A')` - Use default if empty
- `coalesce('alt1','alt2')` - First non-null value

### Example Transformations

```javascript
// Example 1: Date Format Conversion
Source: createdDateTime = "/Date(1234567890000)/"
Transform: date_format('SUCCESSFACTORS','YYYY-MM-DD')
Result: "2009-02-13"

// Example 2: Status Conversion
Source: status = "A"
Transform: status_active
Result: "Active"

// Example 3: String Cleaning
Source: name = "  John Doe  "
Transform: trim
Result: "John Doe"

// Example 4: Default Value
Source: description = null
Transform: default('No description')
Result: "No description"
```

### Where Transformations Are Applied

Transformations are applied **during data sync** when:
1. Data is fetched from SuccessFactors
2. Field mappings are applied
3. Data is transformed using `transform_function` from `hris_field_mapping` table
4. Transformed data is saved to OrgChartAI database

---

## 📊 Field Types Explained

### What Do Field Types Mean?

Field types indicate the **data type** of a field in SuccessFactors:

| Type | Meaning | Example Values |
|------|---------|---------------|
| **String** | Text data | `"John Doe"`, `"Sales Department"` |
| **Int32** | Integer number | `123`, `456` |
| **Int64** | Large integer | `1234567890` |
| **Decimal** | Decimal number | `123.45`, `99.99` |
| **Boolean** | True/False | `true`, `false` |
| **DateTime** | Date and time | `2024-01-15T10:30:00` |
| **DateTimeOffset** | Date/time with timezone | `2024-01-15T10:30:00+00:00` |
| **Guid** | Unique identifier | `550e8400-e29b-41d4-a716-446655440000` |
| **Binary** | Binary data | `[binary data]` |

### Field Type Indicators in UI

- **String** fields: Can use string transformations
- **Date** fields: Can use date transformations
- **Number** fields: Can use number transformations
- **Boolean** fields: Can use boolean transformations

### Required vs Optional Fields

- **Required fields** (marked with `*`): Must be mapped for the entity to be created
- **Optional fields**: Can be left unmapped
- **Hierarchy fields** (marked with `(Hierarchy)`): Used for parent-child relationships

---

## 📅 Record Status & Date Tracking

### How to Identify Active vs Deleted Records

OrgChartAI uses several fields to track record status:

#### 1. **Status Field** (Primary Indicator)
- **Field**: `status`
- **Values**: `Active`, `Inactive`, `Planned`
- **Purpose**: Current state of the record

#### 2. **Effective Dates** (Time-based Status)
- **`effective_start_date`**: When record becomes active
- **`effective_end_date`**: When record becomes inactive/deleted
  - `NULL` = Currently active
  - `Date in past` = Inactive/deleted
  - `Date in future` = Planned

#### 3. **Last Modified Date** (Change Tracking)
- **Field**: `updated_at` (auto-updated by database)
- **Purpose**: Tracks when record was last changed
- **Not used for status** - only for audit trail

#### 4. **Termination Date** (For Employees)
- **Field**: `termination_date` (in `employee` table)
- **Purpose**: When employee left the organization
- **Relationship**: If `termination_date` is set, `status` should be `Inactive`

### SuccessFactors Date Fields

Common SuccessFactors fields for tracking status:

| SF Field | OrgChartAI Field | Purpose |
|----------|------------------|---------|
| `effectiveStartDate` | `effective_start_date` | Start date |
| `effectiveEndDate` | `effective_end_date` | End date (NULL = active) |
| `lastModifiedDateTime` | `updated_at` | Last change timestamp |
| `status` | `status` | Active/Inactive status |
| `terminationDate` | `termination_date` | Employee termination |

### Logic for Active Records

A record is considered **ACTIVE** if:
```sql
status = 'Active' 
AND (effective_end_date IS NULL OR effective_end_date > CURRENT_DATE)
AND (termination_date IS NULL OR termination_date > CURRENT_DATE)
```

A record is considered **DELETED/INACTIVE** if:
```sql
status = 'Inactive' 
OR effective_end_date < CURRENT_DATE
OR termination_date < CURRENT_DATE
```

### Recommended Mapping

For **Organizational Units**:
- Map `effectiveEndDate` → `effective_end_date`
- Map `status` → `status` (with `status_active` transform if needed)

For **Employees**:
- Map `terminationDate` → `termination_date`
- Map `status` → `status`
- Map `lastModifiedDateTime` → `updated_at` (for audit)

---

## ⚙️ Settings & Sync History

### Settings Tab

The **Settings** tab allows you to:

1. **Connection Configuration**
   - Edit connection name and description
   - Update API credentials
   - Change authentication method
   - Modify API URL

2. **Sync Configuration**
   - Set sync frequency (manual, daily, weekly)
   - Configure sync filters (date ranges, status filters)
   - Enable/disable auto-sync
   - Set sync batch size

3. **Mapping Configuration**
   - View mapping statistics
   - Export/import mappings
   - Reset mappings to default

4. **Advanced Settings**
   - Enable/disable data validation
   - Set conflict resolution rules
   - Configure error handling

### Sync History Tab

The **Sync History** tab shows:

1. **Sync Logs**
   - Date and time of each sync
   - Status (Success, Failed, Partial)
   - Records synced (created, updated, deleted)
   - Duration

2. **Sync Details**
   - Click a sync to see:
     - Entities synced (org units, positions, employees)
     - Field mappings applied
     - Transformations used
     - Errors/warnings

3. **Sync Statistics**
   - Total records synced
   - Success rate
   - Average sync time
   - Last successful sync

4. **Error Logs**
   - Failed syncs with error messages
   - Field mapping errors
   - Data validation errors

### Where Sync History is Stored

- **Table**: `hris_sync_history` (to be created)
- **Fields**: 
  - `connection_id`
  - `sync_type` (full, incremental)
  - `status` (success, failed, partial)
  - `records_synced` (JSON)
  - `started_at`, `completed_at`
  - `error_message`

---

## ✅ Verifying Saved Mappings

### How to Verify Mappings Are Saved

1. **In the UI:**
   - After clicking "Save Mapping", you should see:
     ```
     ✅ Mappings saved successfully!
     📊 X mappings saved
     💾 Storage: PostgreSQL database (hris_field_mapping table)
     ```

2. **In the Database:**
   - Query the `hris_field_mapping` table:
     ```sql
     SELECT * FROM hris_field_mapping 
     WHERE connection_id = 'conn-xxxxx' 
     AND is_active = TRUE;
     ```

3. **Using the API:**
   - GET `/api/v1/hris/connections/{connection_id}/mapping`
   - Returns all saved mappings for the connection

### Why You Might See "No Data" in Neon DB

If mappings are saved but you don't see data:

1. **Check Connection ID**
   - Ensure you're querying with the correct `connection_id`
   - Connection IDs are unique per connection

2. **Check Active Status**
   - Only `is_active = TRUE` mappings are returned
   - Old mappings are deactivated when new ones are saved

3. **Check Entity Type**
   - Mappings are grouped by `entity_type`
   - Query specific entity type: `entity_type = 'org_unit'`

4. **Verify Table Exists**
   - Run: `SELECT * FROM hris_field_mapping LIMIT 1;`
   - If error, tables weren't created properly

### Database Schema

```sql
-- Field Mappings Table
CREATE TABLE hris_field_mapping (
    id UUID PRIMARY KEY,
    connection_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,        -- 'org_unit', 'position', 'employee'
    source_field TEXT NOT NULL,        -- SF field name
    target_field TEXT NOT NULL,        -- OrgChartAI field name
    mapping_type TEXT,                 -- 'direct', 'transform', 'custom'
    transform_function TEXT,           -- e.g., 'date_format(...)'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(connection_id, entity_type, source_field)
);

-- Mapping Config Table
CREATE TABLE hris_mapping_config (
    id UUID PRIMARY KEY,
    connection_id TEXT NOT NULL,
    target_entity_type TEXT NOT NULL,
    source_entity_name TEXT NOT NULL,  -- e.g., 'FOBusinessUnit'
    hris_source TEXT NOT NULL,         -- 'successfactors'
    is_active BOOLEAN DEFAULT TRUE,
    last_synced_at TIMESTAMP
);
```

### Sample Query to View All Mappings

```sql
-- View all active mappings for a connection
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

---

## 🎯 Quick Reference

### Transformation Syntax
```
function_name(param1,param2)
```

### Field Type → Transformation
- **String** → `uppercase`, `lowercase`, `trim`, `replace`
- **Date** → `date_format`, `date_add_days`
- **Number** → `round`, `multiply`
- **Status** → `status_active`, `boolean`

### Record Status Logic
- **Active**: `status='Active'` AND `effective_end_date IS NULL`
- **Inactive**: `status='Inactive'` OR `effective_end_date < NOW()`

### Verification
- Check `hris_field_mapping` table
- Filter by `connection_id` and `is_active = TRUE`
- Use API endpoint: `GET /connections/{id}/mapping`
