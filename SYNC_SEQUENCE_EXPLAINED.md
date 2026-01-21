# SuccessFactors Sync Sequence - Explained

## 🎯 Sync Order (Why It Matters)

Data must be synced in a specific sequence to maintain referential integrity:

### Phase 1: Org Units (Foundation)
**Order:**
1. `FODepartment` - Departments
2. `FOCostCenter` - Cost Centers  
3. `FOLegalEntity` - Legal Entities
4. `FODivision` - Divisions
5. `FOBusinessUnit` - Business Units

**Why First?**
- Positions reference org units (`org_unit_id`)
- Employees reference positions
- Must establish org structure hierarchy first

### Phase 2: Positions
**Order:**
1. `Position` - All positions

**Why Second?**
- Positions belong to org units
- Employees are assigned to positions
- Need org units to exist first

### Phase 3: Employees
**Order:**
1. `PerPerson` - Person records
2. `User` - User accounts

**Why Last?**
- Employees are assigned to positions
- Need positions to exist first
- Can link employees to their positions

## 📊 Complete Flow

```
┌─────────────────────────────────────────┐
│  PHASE 1: Org Units                     │
│  ─────────────────────────────────────  │
│  1. FODepartment                        │
│  2. FOCostCenter                        │
│  3. FOLegalEntity                       │
│  4. FODivision                          │
│  5. FOBusinessUnit                      │
│                                         │
│  ↓ Creates org_unit records             │
│  ↓ Establishes hierarchy                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  PHASE 2: Positions                     │
│  ─────────────────────────────────────  │
│  1. Position                            │
│                                         │
│  ↓ Creates position records             │
│  ↓ Links to org_unit_id                 │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  PHASE 3: Employees                     │
│  ─────────────────────────────────────  │
│  1. PerPerson                           │
│  2. User                                │
│                                         │
│  ↓ Creates employee records             │
│  ↓ Links to positions                   │
└─────────────────────────────────────────┘
```

## 🔄 What Happens During Sync

### For Each Entity:

1. **Fetch from SuccessFactors**
   ```
   GET /odata/v2/{EntityName}?$top=1000
   ```

2. **Transform Data**
   - Apply field mappings
   - Apply transformations
   - Add metadata (hris_id, hris_source, hris_type)

3. **Send to Org Service**
   ```
   POST /api/v1/{entity_type}/bulk
   Body: {"records": [transformed_data]}
   ```

4. **Org Service Upserts**
   - Checks if record exists by `hris_id`
   - Updates existing or creates new
   - Maintains relationships

## ✅ Benefits of Sequential Sync

1. **Referential Integrity**
   - Org units exist before positions reference them
   - Positions exist before employees reference them

2. **Hierarchy Building**
   - Parent-child relationships can be established
   - Org chart structure is built correctly

3. **Error Handling**
   - If Phase 1 fails, we know before trying Phase 2
   - Clear error messages per phase

4. **Progress Tracking**
   - Can see which phase is running
   - Know exactly which entity is being synced

## 📝 Implementation

The sync now follows this exact sequence:

```python
# Phase 1: Org Units (in order)
for entity in ["FODepartment", "FOCostCenter", "FOLegalEntity", 
               "FODivision", "FOBusinessUnit"]:
    sync_entity(entity)

# Phase 2: Positions
sync_entity("Position")

# Phase 3: Employees
for entity in ["PerPerson", "User"]:
    sync_entity(entity)
```

## 🎉 Result

After sync completes:
- ✅ All org units in database
- ✅ All positions linked to org units
- ✅ All employees linked to positions
- ✅ Complete org chart ready to visualize!
