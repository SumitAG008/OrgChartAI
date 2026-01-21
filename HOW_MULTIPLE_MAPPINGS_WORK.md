# How Multiple Mappings Work - Complete Guide

## 🎯 Understanding Your Requirements

You want to create **multiple mappings** for the same target entity:

### Example Scenario:
- **Target: Organizational Unit** can receive data from:
  1. `FODepartment` → `org_unit` (Mapping Set 1)
  2. `FOBusinessUnit` → `org_unit` (Mapping Set 2)
  3. `FOLegalEntity` → `org_unit` (Mapping Set 3)
  4. `FODivision` → `org_unit` (Mapping Set 4)
  5. `FOCostCenter` → `org_unit` (Mapping Set 5)
  6. `FORegion` → `org_unit` (Mapping Set 6)
  7. `FOTeam` → `org_unit` (Mapping Set 7)

- **Target: Employee** can receive data from:
  1. `PerPerson` → `employee` (Mapping Set 1)
  2. `PerAddress` → `employee` (for address fields) (Mapping Set 2)
  3. `PerEmail` → `employee` (for email) (Mapping Set 3)

---

## 🔧 How It Works Now

### Step 1: Update Database Schema

**Run the schema update script:**
```bash
python setup-mapping-schema-update.py
```

This will:
- Add `source_entity_name` column to `hris_field_mapping` table
- Update unique constraint to allow multiple source entities per target
- Fix `hris_mapping_config` to support multiple mappings

### Step 2: Create Your First Mapping

1. **Select Target Entity**: "Organizational Unit"
2. **Select SF Entity**: "FODepartment" (search in dropdown)
3. **Map Fields**:
   - `orgUnitName` → `name`
   - `orgUnitCode` → `code`
   - `orgUnitType` → `type` (with `map_org_unit_type` transform)
   - `parentOrgUnitId` → `parent_hris_id`
   - `status` → `status`
4. **Click "Save Mapping"**
5. ✅ **Saved**: `FODepartment` → `org_unit` mapping

### Step 3: Create Second Mapping (Same Target, Different Source)

1. **Keep Target Entity**: "Organizational Unit" (same)
2. **Select Different SF Entity**: "FOBusinessUnit" (search in dropdown)
3. **Map Fields**:
   - `businessUnitName` → `name`
   - `businessUnitCode` → `code`
   - `businessUnitType` → `type`
   - `parentBusinessUnitId` → `parent_hris_id`
4. **Click "Save Mapping"**
5. ✅ **Saved**: `FOBusinessUnit` → `org_unit` mapping

**Important**: This does NOT overwrite the first mapping! Both are saved.

### Step 4: Continue for All Entities

Repeat for:
- `FODivision` → `org_unit`
- `FOCostCenter` → `org_unit`
- `FOLegalEntity` → `org_unit`
- `FORegion` → `org_unit`
- `FOTeam` → `org_unit`

---

## 📊 How Data is Stored

### Database Structure

**`hris_field_mapping` table:**
```
connection_id | entity_type | source_entity_name | source_field    | target_field
--------------|-------------|-------------------|-----------------|-------------
conn-123      | org_unit    | FODepartment      | orgUnitName     | name
conn-123      | org_unit    | FODepartment      | orgUnitCode     | code
conn-123      | org_unit    | FOBusinessUnit    | businessUnitName| name
conn-123      | org_unit    | FOBusinessUnit    | businessUnitCode| code
conn-123      | employee    | PerPerson         | firstName       | first_name
conn-123      | employee    | PerPerson         | lastName        | last_name
```

**`hris_mapping_config` table:**
```
connection_id | target_entity_type | source_entity_name | last_synced_at
--------------|--------------------|--------------------|----------------
conn-123      | org_unit           | FODepartment       | 2024-01-19
conn-123      | org_unit           | FOBusinessUnit     | 2024-01-19
conn-123      | org_unit           | FODivision         | 2024-01-19
conn-123      | employee           | PerPerson          | 2024-01-19
```

---

## 🔄 How Mappings Persist

### When You Switch Tabs

1. **Mappings are saved** to database when you click "Save Mapping"
2. **When you return to Mapping tab**:
   - Component loads mappings from database
   - If you select a target entity and SF entity, it loads that specific mapping
   - Your previous mappings are preserved

### Loading Mappings

The frontend automatically:
1. Fetches mappings when you select a target entity
2. Filters by selected SF entity (if selected)
3. Displays existing mappings in the table
4. Allows you to edit and save

---

## 🎨 UI Flow

### Current Flow:
1. Select Target Entity (e.g., "Organizational Unit")
2. Search and Select SF Entity (e.g., "FODepartment")
3. Fields auto-load
4. Map fields
5. Save → Creates mapping for `FODepartment` → `org_unit`

### To Create Another Mapping:
1. **Keep** Target Entity: "Organizational Unit"
2. **Change** SF Entity: Search and select "FOBusinessUnit"
3. Fields auto-load (different fields)
4. Map fields
5. Save → Creates **separate** mapping for `FOBusinessUnit` → `org_unit`

---

## ✅ Verification

### Check All Your Mappings

**SQL Query:**
```sql
SELECT 
    target_entity_type,
    source_entity_name,
    COUNT(*) as field_count
FROM hris_mapping_config mc
JOIN hris_field_mapping fm 
    ON mc.connection_id = fm.connection_id
    AND mc.target_entity_type = fm.entity_type
    AND mc.source_entity_name = fm.source_entity_name
WHERE mc.connection_id = 'conn-xxxxx'
AND mc.is_active = TRUE
AND fm.is_active = TRUE
GROUP BY target_entity_type, source_entity_name
ORDER BY target_entity_type, source_entity_name;
```

**Expected Result:**
```
target_entity_type | source_entity_name | field_count
--------------------|--------------------|-------------
org_unit            | FODepartment       | 9
org_unit            | FOBusinessUnit     | 8
org_unit            | FODivision         | 7
org_unit            | FOCostCenter       | 6
org_unit            | FOLegalEntity      | 5
employee            | PerPerson          | 12
```

---

## 🚀 Step-by-Step Workflow

### Phase 1: Map All Org Unit Types (7 mappings)

1. **FODepartment** → `org_unit`
   - Select: Target = "Organizational Unit", SF = "FODepartment"
   - Map fields, Save

2. **FOBusinessUnit** → `org_unit`
   - Select: Target = "Organizational Unit", SF = "FOBusinessUnit"
   - Map fields, Save

3. **FODivision** → `org_unit`
   - Select: Target = "Organizational Unit", SF = "FODivision"
   - Map fields, Save

4. Continue for: `FOCostCenter`, `FOLegalEntity`, `FORegion`, `FOTeam`

### Phase 2: Map Employee Entities

1. **PerPerson** → `employee`
   - Select: Target = "Employee", SF = "PerPerson"
   - Map: `firstName` → `first_name`, `lastName` → `last_name`, etc.
   - Save

2. **PerAddress** → `employee` (for address fields)
   - Select: Target = "Employee", SF = "PerAddress"
   - Map address-related fields
   - Save

### Phase 3: Map Position Entities

1. **Position** → `position`
   - Select: Target = "Position", SF = "Position"
   - Map fields, Save

---

## 🔍 Troubleshooting

### Issue: Mappings disappear when switching tabs

**Fix**: Mappings are now automatically loaded when you:
- Return to Mapping tab
- Select a target entity
- Select an SF entity

The component fetches from database and restores your mappings.

### Issue: Can't create multiple mappings

**Fix**: 
1. Run `python setup-mapping-schema-update.py` to update schema
2. Make sure you're selecting **different SF entities** for the same target
3. Each mapping is saved separately

### Issue: Don't see existing mappings

**Check**:
1. Are you selecting the correct target entity?
2. Are you selecting the correct SF entity?
3. Check database: `SELECT * FROM hris_field_mapping WHERE connection_id = 'your-id'`

---

## 📝 Quick Reference

| Action | Result |
|--------|--------|
| Map `FODepartment` → `org_unit` | Creates mapping set 1 |
| Map `FOBusinessUnit` → `org_unit` | Creates mapping set 2 (doesn't overwrite set 1) |
| Switch tabs | Mappings persist in database |
| Return to Mapping tab | Mappings auto-load from database |
| Select different SF entity | Loads that entity's mapping (if exists) |

---

## 🎯 Summary

1. **Each SF Entity → Target Entity = Separate Mapping**
2. **All mappings are saved** in the database
3. **Mappings persist** when switching tabs
4. **You can create 6-7 mappings** for `org_unit` (one per SF entity type)
5. **Then create mappings** for `employee`, `position`, etc.

The system now supports multiple source entities mapping to the same target entity!
