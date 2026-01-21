# Constant Transformation Function Guide

## 🎯 What is Constant Transformation?

The `constant()` transformation function allows you to set a field to a **fixed value** regardless of what the source field contains. This is useful when you need to:

- Set a default status (e.g., always set `status = 'Active'`)
- Set a fixed type (e.g., always set `type = 'Department'`)
- Set default values that don't come from the source system
- Override source values with a constant

---

## 📋 How to Use Constant Transformation

### Step 1: Map a Field

1. Select your **Target Entity** (e.g., "Organizational Unit")
2. Select your **SF Entity** (e.g., "FODepartment")
3. In the mapping table, find the source field you want to map

### Step 2: Select Target Field

1. In the **"→ Target Field"** dropdown, select the target field
   - Example: Select `status` as the target field

### Step 3: Add Constant Transformation

1. Below the target field dropdown, you'll see **"Data Transformation (Optional)"**
2. Scroll down to **"Constant Value"** section
3. Select a constant:
   - `constant('Active')` - Always set to 'Active'
   - `constant('Inactive')` - Always set to 'Inactive'
   - `constant('Department')` - Always set to 'Department'
   - `constant('BusinessUnit')` - Always set to 'BusinessUnit'
   - `constant('Division')` - Always set to 'Division'
   - `constant('CostCenter')` - Always set to 'CostCenter'
   - `constant('LegalEntity')` - Always set to 'LegalEntity'
   - `constant('Custom')` - For custom values (edit manually)

### Step 4: Save

1. Click **"Save Mapping"**
2. The constant value will be applied during data sync

---

## 💡 Use Cases

### Use Case 1: Set Default Status

**Scenario**: You want all org units to have `status = 'Active'` by default.

**Mapping**:
- Source Field: `orgUnitId` (or any field, value is ignored)
- Target Field: `status`
- Transformation: `constant('Active')`

**Result**: 
- All org units will have `status = 'Active'` regardless of source value

### Use Case 2: Set Fixed Type

**Scenario**: You're mapping FODepartment and want all to be type 'Department'.

**Mapping**:
- Source Field: `orgUnitType`
- Target Field: `type`
- Transformation: `constant('Department')`

**Result**:
- All records will have `type = 'Department'`

### Use Case 3: Set Default Values

**Scenario**: You want to set a default description for all records.

**Mapping**:
- Source Field: `description` (or any field)
- Target Field: `description`
- Transformation: `constant('Imported from SuccessFactors')`

**Result**:
- All records will have `description = 'Imported from SuccessFactors'`

---

## 🔧 Custom Constant Values

### Option 1: Use Predefined Constants

The UI provides common constants:
- `constant('Active')`
- `constant('Inactive')`
- `constant('Department')`
- `constant('BusinessUnit')`
- etc.

### Option 2: Edit Manually

1. Select `constant('Custom')` from dropdown
2. After saving, you can edit the mapping in the database or via API
3. Change `transform_function` to: `constant('YourValue')`

**Example**:
```sql
UPDATE hris_field_mapping
SET transform_function = 'constant(''My Custom Value'')'
WHERE id = 'mapping-id';
```

### Option 3: Use API

When saving via API, you can specify any constant:

```json
{
  "mappings": {
    "org_unit": [
      {
        "source_field": "orgUnitId",
        "target_field": "status",
        "transform_function": "constant('Active')"
      }
    ]
  }
}
```

---

## ⚠️ Important Notes

### 1. Source Value is Ignored

When using `constant()`, the **source field value is completely ignored**. The target field will always be set to the constant value.

**Example**:
- Source: `orgUnitStatus = 'I'` (Inactive)
- Transformation: `constant('Active')`
- Result: `status = 'Active'` (source value 'I' is ignored)

### 2. Constant Value Format

- Use single quotes: `constant('Active')`
- For strings with spaces: `constant('My Value')`
- For numbers: `constant('123')` (will be stored as string)
- For special characters: Escape as needed

### 3. When to Use Constant vs Default

**Use `constant()`**:
- When you want to **always** set a fixed value
- When the value should be the same for all records
- When you want to override source values

**Use `default()`**:
- When you want a fallback value **only if source is empty/null**
- When you want to preserve source values when they exist

**Example**:
- `constant('Active')` → Always 'Active', even if source is 'Inactive'
- `default('Active')` → 'Active' only if source is empty, otherwise use source value

---

## 📊 Examples

### Example 1: Set All Status to Active

```python
# Mapping
source_field: "orgUnitId"
target_field: "status"
transform_function: "constant('Active')"

# Result
status = "Active"  # Always, regardless of source
```

### Example 2: Set Type Based on SF Entity

```python
# For FODepartment mapping
source_field: "orgUnitType"
target_field: "type"
transform_function: "constant('Department')"

# For FOBusinessUnit mapping
source_field: "businessUnitType"
target_field: "type"
transform_function: "constant('BusinessUnit')"
```

### Example 3: Set Default Description

```python
# Mapping
source_field: "description"
target_field: "description"
transform_function: "constant('Imported from SuccessFactors on 2024-01-19')"

# Result
description = "Imported from SuccessFactors on 2024-01-19"  # Always
```

---

## 🔍 Verification

### Check Constant Transformation

1. **In UI**:
   - Select target + SF entity
   - Look at mapping table
   - See "⚠️ Constant Value" warning box
   - Shows the constant value that will be used

2. **In Database**:
   ```sql
   SELECT 
       source_field,
       target_field,
       transform_function
   FROM hris_field_mapping
   WHERE transform_function LIKE 'constant(%'
   AND is_active = TRUE;
   ```

3. **During Sync**:
   - Constant values are applied during data transformation
   - Check sync results to verify constant values are set

---

## 🚀 Quick Reference

| What You Want | Transformation | Result |
|---------------|----------------|--------|
| Always set status to 'Active' | `constant('Active')` | `status = 'Active'` always |
| Always set type to 'Department' | `constant('Department')` | `type = 'Department'` always |
| Set default if empty | `default('Active')` | `status = 'Active'` only if source is empty |
| Override source value | `constant('NewValue')` | Target always = 'NewValue' |

---

## 💡 Tips

1. **Use constants for fixed values** that don't change
2. **Use constants for default status** when all records should have the same status
3. **Use constants for type mapping** when you know the type based on the SF entity
4. **Combine with other mappings** - You can have some fields with constants and others with direct mappings
5. **Test after sync** - Verify constant values are applied correctly

The constant transformation is now available! Use it to set fixed values for any field.
