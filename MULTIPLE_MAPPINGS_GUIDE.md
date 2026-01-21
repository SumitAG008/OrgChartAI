# Multiple Mappings Guide - Understanding the Setup

## 🎯 The Problem You're Facing

You need to map **multiple SuccessFactors entities** to the **same target entity**:

### Example: Multiple SF Entities → Same Target

**Organizational Unit (Target)** can receive data from:
- `FODepartment` → `org_unit`
- `FOBusinessUnit` → `org_unit`
- `FOLegalEntity` → `org_unit`
- `FODivision` → `org_unit`
- `FOCostCenter` → `org_unit`
- `FORegion` → `org_unit`
- `FOTeam` → `org_unit`

**Employee (Target)** can receive data from:
- `PerPerson` → `employee`
- `PerPersonal` → `employee`
- `PerEmail` → `employee` (for email field)
- `PerAddress` → `employee` (for address fields)

**Position (Target)** can receive data from:
- `Position` → `position`
- `JobProfile` → `position` (for job details)

---

## 🔄 How It Works

### Current Architecture

1. **Each Mapping is Unique**:
   - Connection ID: `conn-xxxxx`
   - Target Entity: `org_unit`, `position`, `employee`
   - Source Entity: `FODepartment`, `FOBusinessUnit`, etc.
   - Source Field: `orgUnitName`, `orgUnitCode`, etc.
   - Target Field: `name`, `code`, etc.

2. **Database Structure**:
   ```sql
   hris_field_mapping:
   - connection_id
   - entity_type (target: org_unit, position, employee)
   - source_field (SF field name)
   - target_field (OrgChartAI field name)
   - transform_function (optional)
   
   hris_mapping_config:
   - connection_id
   - target_entity_type (org_unit, position, employee)
   - source_entity_name (FODepartment, FOBusinessUnit, etc.)
   ```

3. **How Mappings Are Saved**:
   - When you select: `FODepartment` → `org_unit`
   - And map fields: `orgUnitName` → `name`, `orgUnitCode` → `code`
   - These are saved with `entity_type = 'org_unit'` and `source_entity_name = 'FODepartment'`

4. **Multiple Mappings for Same Target**:
   - You can create **separate mappings** for each SF entity
   - `FODepartment` → `org_unit` (Mapping Set 1)
   - `FOBusinessUnit` → `org_unit` (Mapping Set 2)
   - `FOLegalEntity` → `org_unit` (Mapping Set 3)
   - All saved in the same database, but grouped by `source_entity_name`

---

## 📋 Step-by-Step: Creating Multiple Mappings

### Step 1: Map FODepartment → Organizational Unit

1. Select **Target Entity**: "Organizational Unit"
2. Search and select **SF Entity**: "FODepartment"
3. Map fields:
   - `orgUnitName` → `name`
   - `orgUnitCode` → `code`
   - `orgUnitType` → `type` (with `map_org_unit_type` transform)
   - `parentOrgUnitId` → `parent_hris_id`
   - `status` → `status`
4. Click **"Save Mapping"**
5. ✅ Saved: `FODepartment` → `org_unit` mapping

### Step 2: Map FOBusinessUnit → Organizational Unit

1. **Keep** Target Entity: "Organizational Unit" (same)
2. Search and select **SF Entity**: "FOBusinessUnit" (different)
3. Map fields:
   - `businessUnitName` → `name`
   - `businessUnitCode` → `code`
   - `businessUnitType` → `type`
   - `parentBusinessUnitId` → `parent_hris_id`
4. Click **"Save Mapping"**
5. ✅ Saved: `FOBusinessUnit` → `org_unit` mapping

### Step 3: Map FOLegalEntity → Organizational Unit

1. **Keep** Target Entity: "Organizational Unit" (same)
2. Search and select **SF Entity**: "FOLegalEntity"
3. Map fields...
4. Click **"Save Mapping"**
5. ✅ Saved: `FOLegalEntity` → `org_unit` mapping

### Step 4: Map PerPerson → Employee

1. Select **Target Entity**: "Employee"
2. Search and select **SF Entity**: "PerPerson"
3. Map fields:
   - `firstName` → `first_name`
   - `lastName` → `last_name`
   - `email` → `email`
   - `userId` → `employee_number`
4. Click **"Save Mapping"**
5. ✅ Saved: `PerPerson` → `employee` mapping

---

## 🗄️ How Mappings Are Stored

### Database Tables

**`hris_field_mapping`** table stores:
```
connection_id | entity_type | source_field      | target_field | source_entity_name
--------------|-------------|-------------------|--------------|------------------
conn-123      | org_unit    | orgUnitName       | name         | FODepartment
conn-123      | org_unit    | orgUnitCode       | code         | FODepartment
conn-123      | org_unit    | businessUnitName  | name         | FOBusinessUnit
conn-123      | org_unit    | businessUnitCode  | code         | FOBusinessUnit
conn-123      | employee    | firstName         | first_name   | PerPerson
conn-123      | employee    | lastName          | last_name    | PerPerson
```

**`hris_mapping_config`** table stores:
```
connection_id | target_entity_type | source_entity_name | last_synced_at
--------------|---------------------|--------------------|----------------
conn-123      | org_unit            | FODepartment       | 2024-01-19
conn-123      | org_unit            | FOBusinessUnit     | 2024-01-19
conn-123      | org_unit            | FOLegalEntity      | 2024-01-19
conn-123      | employee            | PerPerson          | 2024-01-19
```

---

## 🔧 Backend API Endpoints

### Get All Mappings for a Target Entity
```
GET /api/v1/hris/connections/{connection_id}/mapping?entity_type=org_unit
```

**Response**:
```json
{
  "mappings": {
    "org_unit": [
      {
        "entity_type": "org_unit",
        "source_field": "orgUnitName",
        "target_field": "name",
        "mapping_type": "direct",
        "source_entity_name": "FODepartment"
      },
      {
        "entity_type": "org_unit",
        "source_field": "businessUnitName",
        "target_field": "name",
        "mapping_type": "direct",
        "source_entity_name": "FOBusinessUnit"
      }
    ]
  }
}
```

### Save Mappings
```
POST /api/v1/hris/connections/{connection_id}/mapping
```

**Request Body**:
```json
{
  "mappings": {
    "org_unit": [
      {
        "entity_type": "org_unit",
        "source_field": "orgUnitName",
        "target_field": "name",
        "mapping_type": "direct",
        "source_entity_name": "FODepartment"
      }
    ]
  }
}
```

---

## 🎨 UI Improvements Needed

### Current Problem
- Mappings disappear when switching tabs
- Can't see all mappings for a target entity
- Can't manage multiple source entities

### Solution: Mapping Manager View

**New UI Structure**:

1. **Mapping Overview** (Top Section):
   - Shows all target entities
   - For each target, shows count of source entities mapped
   - Example: "Organizational Unit: 7 mappings (FODepartment, FOBusinessUnit, ...)"

2. **Source Entity List** (Left Side):
   - Lists all SF entities that have mappings for selected target
   - Click to edit a specific mapping
   - Add new mapping button

3. **Field Mapping Editor** (Right Side):
   - Shows fields for selected source entity
   - Allows mapping to target entity fields
   - Save button saves this specific mapping

---

## 📝 Recommended Workflow

### Phase 1: Map All Org Unit Types
1. Map `FODepartment` → `org_unit`
2. Map `FOBusinessUnit` → `org_unit`
3. Map `FODivision` → `org_unit`
4. Map `FOCostCenter` → `org_unit`
5. Map `FOLegalEntity` → `org_unit`
6. Map `FORegion` → `org_unit`
7. Map `FOTeam` → `org_unit`

### Phase 2: Map Employee Entities
1. Map `PerPerson` → `employee`
2. Map `PerAddress` → `employee` (for address fields)
3. Map `PerEmail` → `employee` (if separate)

### Phase 3: Map Position Entities
1. Map `Position` → `position`
2. Map `JobProfile` → `position` (for job details)

### Phase 4: Map Skills/Other
1. Map `Skill` → `skill` (if you have a skill entity)
2. Map other entities as needed

---

## ✅ Verification

### Check All Mappings
```sql
SELECT 
    target_entity_type,
    source_entity_name,
    COUNT(*) as field_count
FROM hris_mapping_config
WHERE connection_id = 'conn-xxxxx'
AND is_active = TRUE
GROUP BY target_entity_type, source_entity_name
ORDER BY target_entity_type, source_entity_name;
```

### Expected Result:
```
target_entity_type | source_entity_name | field_count
-------------------|--------------------|-------------
org_unit           | FODepartment       | 9
org_unit           | FOBusinessUnit     | 8
org_unit           | FODivision         | 7
org_unit           | FOCostCenter       | 6
org_unit           | FOLegalEntity      | 5
employee           | PerPerson          | 12
position           | Position           | 14
```

---

## 🚀 Next Steps

1. **Fix Tab Switching**: Load mappings when component mounts
2. **Add Source Entity to Mappings**: Store which SF entity each mapping is for
3. **Create Mapping Manager UI**: Show all mappings, allow editing
4. **Add Mapping List View**: See all mappings for a target entity
