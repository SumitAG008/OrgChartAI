# Type Mapping & Data Manipulation Guide

## 🎯 Problem: Mapping SuccessFactors Types to Internal Types

When syncing data from SuccessFactors, you need to map:
- **SuccessFactors Entity Types** → **OrgChartAI Internal Types**
  - `FOBusinessUnit` → `BusinessUnit`
  - `FODepartment` → `Department`
  - `FODivision` → `Division`
  - `FOCostCenter` → `CostCenter`

- **SuccessFactors Field Values** → **OrgChartAI Field Values**
  - Status codes: `"A"` → `"Active"`
  - Date formats: `"/Date(1234567890000)/"` → `"2024-01-15"`
  - Type values: `"FOBusinessUnit"` → `"BusinessUnit"`

---

## 🔄 Solution: Transform Functions

### 1. Map Org Unit Type (Entity Type Mapping)

**Use Case**: Map SuccessFactors org unit type field to internal type.

**Transform Function**: `map_org_unit_type`

**Example**:
```
Source Field: orgUnitType = "FOBusinessUnit"
Target Field: type
Transform: map_org_unit_type
Result: "BusinessUnit"
```

**Supported Mappings**:
- `FOBusinessUnit` → `BusinessUnit`
- `FODepartment` → `Department`
- `FODivision` → `Division`
- `FOCostCenter` → `CostCenter`
- `FOLegalEntity` → `LegalEntity`
- `FOTeam` → `Team`
- `FORegion` → `Region`
- Unknown → `CustomOrgUnit` (default)

### 2. Custom Type Mapping

**Use Case**: Map custom values using a dictionary.

**Transform Function**: `map_entity_type('{"A":"Active","I":"Inactive"}')`

**Example**:
```
Source Field: status = "A"
Target Field: status
Transform: map_entity_type('{"A":"Active","I":"Inactive","P":"Planned"}')
Result: "Active"
```

### 3. Status Mapping

**Use Case**: Convert status codes to Active/Inactive.

**Transform Function**: `status_active`

**Example**:
```
Source Field: status = "A"
Target Field: status
Transform: status_active
Result: "Active"
```

---

## 📋 Step-by-Step: Setting Up Type Mapping

### Step 1: Identify the Source Field

In SuccessFactors, find the field that contains the type:
- `orgUnitType` - Org unit type
- `positionType` - Position type
- `status` - Status code

### Step 2: Map in the UI

1. **Select Source Field**: e.g., `orgUnitType`
2. **Select Target Field**: e.g., `type`
3. **Add Transform**: Click "Transform" button
4. **Choose Function**: Select `map_org_unit_type`
5. **Save**: Click "Save Mapping"

### Step 3: Verify the Mapping

**SQL Query**:
```sql
SELECT 
    source_field,
    target_field,
    transform_function
FROM hris_field_mapping
WHERE connection_id = 'your-connection-id'
AND source_field = 'orgUnitType'
AND is_active = TRUE;
```

**Expected Result**:
```
source_field: orgUnitType
target_field: type
transform_function: map_org_unit_type
```

---

## 🔧 Available Transform Functions for Types

### String-Based Type Mapping

| Function | Description | Example |
|----------|-------------|---------|
| `map_org_unit_type` | Map SF org unit types | `FOBusinessUnit` → `BusinessUnit` |
| `map_entity_type('{"A":"Active"}')` | Custom dictionary mapping | `"A"` → `"Active"` |
| `uppercase` | Convert to uppercase | `"department"` → `"DEPARTMENT"` |
| `lowercase` | Convert to lowercase | `"DEPARTMENT"` → `"department"` |
| `title_case` | Convert to title case | `"DEPARTMENT"` → `"Department"` |

### Status Mapping

| Function | Description | Example |
|----------|-------------|---------|
| `status_active` | Convert to Active/Inactive | `"A"` → `"Active"` |
| `boolean` | Convert to true/false | `"1"` → `true` |

---

## 💡 Common Mapping Scenarios

### Scenario 1: Map Org Unit Type

**Problem**: SuccessFactors returns `orgUnitType = "FOBusinessUnit"`, but you need `type = "BusinessUnit"`.

**Solution**:
```
Source: orgUnitType
Target: type
Transform: map_org_unit_type
```

### Scenario 2: Map Status Codes

**Problem**: SuccessFactors returns `status = "A"`, but you need `status = "Active"`.

**Solution**:
```
Source: status
Target: status
Transform: status_active
```

**OR** for custom mapping:
```
Source: status
Target: status
Transform: map_entity_type('{"A":"Active","I":"Inactive","P":"Planned"}')
```

### Scenario 3: Map Department/Division

**Problem**: SuccessFactors entity name is `FODepartment`, but you want to store as `Department` in the `type` field.

**Solution**:
1. Map the entity type during sync (handled by `HierarchyResolver`)
2. OR map a field like `orgUnitType` using `map_org_unit_type`

### Scenario 4: Handle Custom Types

**Problem**: SuccessFactors has custom org unit types not in the standard mapping.

**Solution**:
1. Use `map_entity_type` with a custom dictionary:
   ```
   map_entity_type('{"CustomType1":"Department","CustomType2":"Division"}')
   ```
2. Or add to the `hris_org_unit_type_mapping` table in the database

---

## 🗄️ Database-Level Type Mapping

### Table: `hris_org_unit_type_mapping`

This table stores the mapping between HRIS types and internal types:

```sql
SELECT * FROM hris_org_unit_type_mapping
WHERE hris_source = 'successfactors';
```

**To Add Custom Mappings**:
```sql
INSERT INTO hris_org_unit_type_mapping 
(hris_source, hris_type, internal_type, description)
VALUES 
('successfactors', 'CustomOrgUnit', 'Department', 'Custom SuccessFactors org unit');
```

---

## 🎨 UI Implementation

### In FieldMappingEditor.tsx

When a user selects a transform function, show:

1. **Transform Dropdown**:
   - For `type` field: Show `map_org_unit_type`
   - For `status` field: Show `status_active`, `map_entity_type`
   - For string fields: Show string transforms

2. **Transform Parameters**:
   - If `map_entity_type` selected, show input for dictionary JSON
   - If `date_format` selected, show format dropdowns

3. **Preview**:
   - Show example transformation result
   - e.g., `"FOBusinessUnit"` → `"BusinessUnit"`

---

## 📝 Example: Complete Type Mapping Setup

### For Organizational Units

1. **Map Entity Type** (if using entity name):
   ```
   Source Entity: FOBusinessUnit
   Target Entity: org_unit
   Type Field Mapping:
     Source: orgUnitType (or use entity name)
     Target: type
     Transform: map_org_unit_type
   ```

2. **Map Status**:
   ```
   Source: status
   Target: status
   Transform: status_active
   ```

3. **Map Dates**:
   ```
   Source: effectiveEndDate
   Target: effective_end_date
   Transform: date_format('SUCCESSFACTORS','YYYY-MM-DD')
   ```

### For Positions

1. **Map Position Type**:
   ```
   Source: positionType
   Target: position_type
   Transform: map_entity_type('{"FT":"FullTime","PT":"PartTime"}')
   ```

2. **Map Status**:
   ```
   Source: status
   Target: status
   Transform: status_active
   ```

---

## ✅ Verification

### Check Transformations Are Applied

**SQL**:
```sql
SELECT 
    entity_type,
    source_field,
    target_field,
    transform_function
FROM hris_field_mapping
WHERE transform_function LIKE '%map%'
AND is_active = TRUE;
```

### Test Transformation

**Python**:
```python
from app.services.transform_functions import TransformFunctions

# Test org unit type mapping
result = TransformFunctions.transform_map_org_unit_type("FOBusinessUnit")
print(result)  # Should output: "BusinessUnit"

# Test status mapping
result = TransformFunctions.transform_status_active("A")
print(result)  # Should output: "Active"
```

---

## 🚀 Quick Reference

| Need | Transform Function |
|------|-------------------|
| Map SF org unit type | `map_org_unit_type` |
| Map custom values | `map_entity_type('{"A":"Active"}')` |
| Convert status | `status_active` |
| Convert case | `uppercase`, `lowercase`, `title_case` |
| Format date | `date_format('SUCCESSFACTORS','YYYY-MM-DD')` |

---

## 📚 Related Files

- **Transform Functions**: `backend/hris-service/app/services/transform_functions.py`
- **Data Transformer**: `backend/hris-service/app/services/data_transformer.py`
- **Hierarchy Resolver**: `backend/hris-service/app/services/hierarchy_resolver.py`
- **Mapping Router**: `backend/hris-service/app/routers/mapping.py`
