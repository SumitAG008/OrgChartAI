# Constant Value Input Field - Complete Guide

## ✅ What Was Fixed

### 1. **Constant Value Input Field Added**
- When you select "constant" from transformation dropdown, an **input field appears**
- You can type any constant value you want
- No need to select from predefined options

### 2. **Save Function Fixed**
- Removed `hasChanges` requirement - you can save anytime
- Better validation - checks if mappings exist before saving
- Clear error messages if something is missing

### 3. **Green Highlighting for Required Fields**
- Changed all red/orange colors to **green**
- Required fields now show in **green** (not red/orange)
- Hierarchy fields also in **green**
- Mapped fields have green border and background

---

## 🎯 How to Use Constant Value

### Step 1: Map a Field
1. Select **Target Entity**: "Organizational Unit"
2. Select **SF Entity**: "FODepartment"
3. In mapping table, find a source field (e.g., `status`)
4. Select target field from dropdown (e.g., `status`)

### Step 2: Add Constant Transformation
1. Below target field dropdown, you'll see **"Data Transformation (Optional)"**
2. Select **"constant - Set constant value (enter below)"**
3. **Input field appears** below the dropdown

### Step 3: Enter Constant Value
1. Type your constant value in the input field
   - Example: `Active`
   - Example: `Department`
   - Example: `My Custom Value`
2. The value is saved as: `constant('YourValue')`

### Step 4: Save
1. Click **"Save Mapping"**
2. Constant value is saved with the mapping

---

## 💡 Examples

### Example 1: Set Status to 'Active'
```
Source Field: orgUnitId (any field)
Target Field: status
Transformation: constant
Constant Value Input: Active
Result: status = 'Active' (always)
```

### Example 2: Set Type to 'Department'
```
Source Field: orgUnitType
Target Field: type
Transformation: constant
Constant Value Input: Department
Result: type = 'Department' (always)
```

### Example 3: Custom Value
```
Source Field: description
Target Field: description
Transformation: constant
Constant Value Input: Imported from SuccessFactors on 2024-01-19
Result: description = 'Imported from SuccessFactors on 2024-01-19' (always)
```

---

## 🎨 UI Changes

### Green Highlighting
- ✅ **Required fields**: Green text and background
- ✅ **Mapped fields**: Green border and background
- ✅ **Hierarchy fields**: Green indicators
- ✅ **Legend**: Green background instead of gray
- ✅ **Status badges**: Green instead of orange/red

### Constant Input Field
- ✅ **Appears when**: You select "constant" from dropdown
- ✅ **Placeholder**: "Enter constant value (e.g., Active, Department, etc.)"
- ✅ **Styling**: Green border and background (green-50)
- ✅ **Feedback**: Shows "✓ This field will always be set to this value"

---

## 🔧 How It Works

### When You Select "constant"
1. Dropdown shows: `constant - Set constant value (enter below)`
2. Input field appears below
3. You type your value
4. Value is formatted as: `constant('YourValue')`
5. Saved to database with mapping

### During Data Sync
1. Source field value is read (but ignored)
2. Constant transformation is applied
3. Target field gets the constant value
4. Result: `target_field = 'YourConstantValue'`

---

## ✅ Verification

### Check Constant Value
1. **In UI**: 
   - Select target + SF entity
   - Find field with constant transformation
   - See input field with your value
   - See green message: "✓ This field will always be set to this value"

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

---

## 🚀 Quick Reference

| Action | Result |
|--------|--------|
| Select "constant" from dropdown | Input field appears |
| Type value in input | Value saved as `constant('YourValue')` |
| Save mapping | Constant transformation saved |
| During sync | Target field always = your constant value |

---

## 💡 Tips

1. **You can type any value** - Not limited to predefined options
2. **Spaces are allowed** - "My Custom Value" works fine
3. **Case sensitive** - "Active" ≠ "active"
4. **Edit anytime** - Change the input value and save again
5. **Multiple constants** - Each field can have its own constant value

The constant input field is now available! Type any value you want.
