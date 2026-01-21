# Mapping Persistence & Multiple Mappings - Complete Solution

## ✅ What Was Fixed

### 1. Database Schema Updated
- ✅ Added `source_entity_name` column to `hris_field_mapping` table
- ✅ Updated unique constraint to allow multiple source entities per target
- ✅ Fixed `hris_mapping_config` to support multiple mappings

### 2. Backend Updated
- ✅ Saves `source_entity_name` with each mapping
- ✅ Returns mappings grouped by `source_entity_name`
- ✅ New endpoint: `/mapping/configs` to list all mapping configurations

### 3. Frontend Updated
- ✅ Mappings persist when switching tabs
- ✅ Mappings auto-load when selecting target + SF entity
- ✅ Includes `source_entity_name` when saving
- ✅ Searchable dropdown for SF entities

---

## 🎯 How to Use: Creating Multiple Mappings

### Example: Map 7 Different SF Entities to `org_unit`

#### Step 1: Map FODepartment → org_unit
1. Select **Target**: "Organizational Unit"
2. Search & Select **SF Entity**: "FODepartment"
3. Map fields (e.g., `orgUnitName` → `name`)
4. Click **"Save Mapping"**
5. ✅ Saved: `FODepartment` → `org_unit`

#### Step 2: Map FOBusinessUnit → org_unit
1. **Keep** Target: "Organizational Unit" (same)
2. **Change** SF Entity: Search & select "FOBusinessUnit"
3. Map fields (e.g., `businessUnitName` → `name`)
4. Click **"Save Mapping"**
5. ✅ Saved: `FOBusinessUnit` → `org_unit` (separate from FODepartment)

#### Step 3-7: Repeat for Other Entities
- `FODivision` → `org_unit`
- `FOCostCenter` → `org_unit`
- `FOLegalEntity` → `org_unit`
- `FORegion` → `org_unit`
- `FOTeam` → `org_unit`

**Result**: You now have **7 separate mappings** all for `org_unit`, each from a different SF entity.

---

## 🔄 How Mappings Persist

### When You Switch Tabs

1. **Mappings are saved** to database when you click "Save Mapping"
2. **When you return to Mapping tab**:
   - Component automatically fetches mappings from database
   - If you select a target entity and SF entity, it loads that specific mapping
   - Your previous mappings are preserved

### Loading Logic

```typescript
// When component mounts or target/SF entity changes:
1. Fetch mappings from: GET /api/v1/hris/connections/{id}/mapping?entity_type=org_unit
2. Response structure: {mappings: {org_unit: {FODepartment: [...], FOBusinessUnit: [...]}}}
3. Filter by selected SF entity
4. Display in mapping table
```

---

## 📊 Database Structure

### `hris_field_mapping` Table

Each row stores:
- `connection_id`: Your connection ID
- `entity_type`: Target entity (`org_unit`, `position`, `employee`)
- `source_entity_name`: SF entity (`FODepartment`, `FOBusinessUnit`, etc.)
- `source_field`: SF field name
- `target_field`: OrgChartAI field name
- `transform_function`: Optional transformation

**Unique Constraint**: `(connection_id, entity_type, source_entity_name, source_field)`

This means:
- ✅ You can have `FODepartment.orgUnitName` → `org_unit.name`
- ✅ You can have `FOBusinessUnit.businessUnitName` → `org_unit.name`
- ✅ Both are stored separately

### `hris_mapping_config` Table

Stores metadata:
- `connection_id`
- `target_entity_type`: `org_unit`
- `source_entity_name`: `FODepartment`, `FOBusinessUnit`, etc.
- `last_synced_at`: When last synced

**Unique Constraint**: `(connection_id, target_entity_type, source_entity_name)`

This allows multiple source entities per target.

---

## 🔍 Verifying Your Mappings

### SQL Query to See All Mappings

```sql
SELECT 
    entity_type as target,
    source_entity_name as source,
    COUNT(*) as field_count,
    MAX(updated_at) as last_updated
FROM hris_field_mapping
WHERE connection_id = 'conn-xxxxx'
AND is_active = TRUE
GROUP BY entity_type, source_entity_name
ORDER BY entity_type, source_entity_name;
```

### Expected Result After Creating 7 Mappings:

```
target    | source           | field_count | last_updated
----------|------------------|-------------|-------------
org_unit  | FODepartment    | 9           | 2024-01-19
org_unit  | FOBusinessUnit  | 8           | 2024-01-19
org_unit  | FODivision      | 7           | 2024-01-19
org_unit  | FOCostCenter    | 6           | 2024-01-19
org_unit  | FOLegalEntity    | 5           | 2024-01-19
org_unit  | FORegion         | 4           | 2024-01-19
org_unit  | FOTeam           | 3           | 2024-01-19
employee  | PerPerson        | 12          | 2024-01-19
```

---

## 🎨 UI Flow

### Creating a New Mapping

1. **Select Target Entity**: Click "Organizational Unit"
2. **Search SF Entity**: Type "FODepartment" in search box
3. **Select from Dropdown**: Click "F O Department (FODepartment)"
4. **Fields Auto-Load**: Fields appear in mapping table
5. **Map Fields**: Select target fields from dropdowns
6. **Save**: Click "Save Mapping"
7. ✅ **Saved to Database**

### Editing Existing Mapping

1. **Select Target Entity**: "Organizational Unit"
2. **Search & Select SF Entity**: "FODepartment"
3. **Mappings Auto-Load**: Previous mappings appear in table
4. **Edit**: Change field mappings
5. **Save**: Click "Save Mapping"
6. ✅ **Updated in Database**

### Creating Another Mapping (Same Target)

1. **Keep Target**: "Organizational Unit" (same)
2. **Change SF Entity**: Search & select "FOBusinessUnit" (different)
3. **New Fields Load**: Different fields appear
4. **Map Fields**: Create new mappings
5. **Save**: Click "Save Mapping"
6. ✅ **New Mapping Saved** (doesn't overwrite FODepartment mapping)

---

## 🚀 Complete Workflow

### Phase 1: Map All Org Unit Types (7 mappings)

```
1. FODepartment → org_unit
2. FOBusinessUnit → org_unit
3. FODivision → org_unit
4. FOCostCenter → org_unit
5. FOLegalEntity → org_unit
6. FORegion → org_unit
7. FOTeam → org_unit
```

### Phase 2: Map Employee Entities

```
1. PerPerson → employee
2. PerAddress → employee (for address fields)
3. PerEmail → employee (if separate)
```

### Phase 3: Map Position Entities

```
1. Position → position
2. JobProfile → position (for job details)
```

---

## ✅ Summary

1. **Mappings Persist**: Saved to database, loaded when you return
2. **Multiple Mappings Supported**: Each SF entity → target = separate mapping
3. **No Overwriting**: Saving `FOBusinessUnit` doesn't affect `FODepartment` mapping
4. **Auto-Load**: Mappings load when you select target + SF entity
5. **Searchable**: Easy to find SF entities in dropdown

You can now create all 6-7 mappings for `org_unit`, then move on to `employee`, `position`, etc.!
