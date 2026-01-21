# How to Access Saved Mappings & Data Manipulation Guide

## 📍 Where Are Your Saved Mappings?

### Option 1: View All Saved Mappings (New Section)

At the top of the Mapping tab, you'll now see a **"Your Saved Mappings"** section that shows:
- All saved mappings grouped by target entity
- Source entities (e.g., FODepartment, FOBusinessUnit)
- Field counts for each mapping
- Last updated date
- **Click any mapping to edit it** - It will automatically select the target entity and SF entity

### Option 2: Select Target Entity + SF Entity

1. **Select Target Entity**: Click "Organizational Unit" (or Position, Employee)
   - You'll see a badge showing how many mappings exist (e.g., "7 mapped")
   - You'll see which SF entities are mapped (e.g., "FODepartment", "FOBusinessUnit")

2. **Select SF Entity**: Search and select the SF entity (e.g., "FOBusinessUnit")
   - Fields will auto-load
   - **You'll see**: "✓ Loaded: X saved mappings for FOBusinessUnit"
   - Your saved mappings will appear in the mapping table with dropdowns pre-selected

3. **Edit Mappings**: 
   - Change any field mapping
   - Add transformation functions
   - Click "Save Mapping" to update

---

## 🔧 Data Manipulation (Transformation Functions)

### How to Add Data Transformations

When you map a field, you'll see a **"Data Transformation (Optional)"** dropdown below the target field selector.

### Available Transformations

#### 1. **String Transformations**

**uppercase**
- Converts text to UPPERCASE
- Example: `"department"` → `"DEPARTMENT"`
- Use for: Standardizing text case

**lowercase**
- Converts text to lowercase
- Example: `"DEPARTMENT"` → `"department"`
- Use for: Standardizing text case

**title_case**
- Converts to Title Case
- Example: `"DEPARTMENT"` → `"Department"`
- Use for: Proper names, titles

**trim**
- Removes leading/trailing whitespace
- Example: `"  Department  "` → `"Department"`
- Use for: Cleaning up text fields

**map_org_unit_type**
- Maps SuccessFactors org unit types to internal types
- Example: `"FOBusinessUnit"` → `"BusinessUnit"`
- Use for: Type fields (org_unit.type)

#### 2. **Date Transformations**

**date_format('ISO','YYYY-MM-DD')**
- Changes date format
- Example: `"2024-01-19T10:30:00Z"` → `"2024-01-19"`
- Use for: Standardizing date formats

#### 3. **Status Transformations**

**status_active**
- Converts status codes to Active/Inactive
- Example: `"A"` → `"Active"`, `"I"` → `"Inactive"`
- Use for: Status fields

**boolean**
- Converts to true/false
- Example: `"1"` → `true`, `"0"` → `false`
- Use for: Boolean fields

#### 4. **Number Transformations**

**round(2)**
- Rounds number to 2 decimal places
- Example: `123.456` → `123.46`
- Use for: Financial data, percentages

---

## 📋 Step-by-Step: Adding a Transformation

### Example: Map `orgUnitType` → `type` with Transformation

1. **Select Target Entity**: "Organizational Unit"
2. **Select SF Entity**: "FODepartment"
3. **In Mapping Table**:
   - Find `orgUnitType` field
   - Select target field: `type`
   - **In "Data Transformation" dropdown**: Select `map_org_unit_type`
4. **Result**: 
   - `orgUnitType = "FODepartment"` → `type = "Department"`
   - The transformation automatically converts SF types to internal types

### Example: Map `orgUnitName` → `name` with Uppercase

1. **Find**: `orgUnitName` field
2. **Select target**: `name`
3. **Add transformation**: `uppercase`
4. **Result**: 
   - `orgUnitName = "sales department"` → `name = "SALES DEPARTMENT"`

---

## 🎯 Common Use Cases

### Use Case 1: Map Org Unit Type
```
Source Field: orgUnitType (FODepartment)
Target Field: type
Transformation: map_org_unit_type
Result: "FODepartment" → "Department"
```

### Use Case 2: Clean Up Text
```
Source Field: orgUnitName
Target Field: name
Transformation: trim
Result: "  Sales Department  " → "Sales Department"
```

### Use Case 3: Standardize Status
```
Source Field: status
Target Field: status
Transformation: status_active
Result: "A" → "Active", "I" → "Inactive"
```

### Use Case 4: Format Date
```
Source Field: createdDate
Target Field: created_at
Transformation: date_format('ISO','YYYY-MM-DD')
Result: "2024-01-19T10:30:00Z" → "2024-01-19"
```

---

## 🔍 Finding Your Saved Mappings

### Method 1: View All Mappings
- Look at the **"Your Saved Mappings"** section at the top
- Shows all mappings with source entities
- Click any to edit

### Method 2: Target Entity Cards
- Look at target entity cards (Organizational Unit, Position, Employee)
- See badge: "7 mapped"
- See source entities: "FODepartment", "FOBusinessUnit", etc.

### Method 3: Select Entities
- Select target entity → SF entity
- See "✓ Loaded: X saved mappings"
- Mappings appear in table with dropdowns pre-selected

---

## ✅ Verification

### Check if Mappings Are Loaded

1. **Select Target Entity**: "Organizational Unit"
2. **Select SF Entity**: "FOBusinessUnit"
3. **Look for**: Blue box showing "✓ Loaded: 7 saved mappings for FOBusinessUnit"
4. **Check Table**: Dropdowns should be pre-selected with your mappings
5. **Check Transformations**: If you added transformations, you'll see "✓ Will apply: [function name]"

### Check in Database

```sql
SELECT 
    source_entity_name,
    source_field,
    target_field,
    transform_function,
    mapping_type
FROM hris_field_mapping
WHERE connection_id = 'conn-xxxxx'
AND entity_type = 'org_unit'
AND source_entity_name = 'FOBusinessUnit'
AND is_active = TRUE;
```

---

## 💡 Tips

1. **Transformations are optional** - You can map fields without transformations (direct mapping)

2. **Transformations apply during sync** - They're stored with the mapping and applied when data is synced

3. **You can edit transformations** - Just change the dropdown and save

4. **Multiple mappings can use same transformation** - Each field mapping can have its own transformation

5. **Test transformations** - After saving, check the sync results to verify transformations work correctly

---

## 🚀 Quick Reference

| What You Want | How to Do It |
|---------------|--------------|
| **See all saved mappings** | Look at "Your Saved Mappings" section at top |
| **Edit a saved mapping** | Click it in "Your Saved Mappings" OR select target + SF entity |
| **Add transformation** | Select target field → Choose transformation from dropdown |
| **Change transformation** | Select different transformation → Save |
| **Remove transformation** | Select "-- No transformation (direct) --" → Save |
| **See which fields are mapped** | Look at mapping table - mapped fields show "Mapped" status |

Your mappings are saved and accessible! Use transformations to manipulate data between source and target.
