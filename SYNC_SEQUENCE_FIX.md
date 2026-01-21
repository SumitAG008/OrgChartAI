# ✅ Sync Sequence & API Format Fix

## Issues Fixed

### 1. **JSONB Encoding Error** ✅
**Problem:** `invalid input for query argument $3: ('dict' object has no attribute 'encode')`

**Solution:** 
- Changed from `:credentials::jsonb` to `CAST(:credentials AS jsonb)` in SQL
- Properly convert dict to JSON string using `json.dumps()` before passing to SQL

**File:** `backend/hris-service/app/routers/auto_sync.py` (line 460)

### 2. **API Format** ✅
**Problem:** Need to use `/odata/v2/{EntityName}?format=json&$top=1000`

**Solution:**
- Updated `_make_request()` method to automatically add:
  - `format=json` parameter
  - `$top=1000` parameter (if not already specified)
  
**File:** `backend/hris-service/app/services/successfactors_client.py` (line 127)

### 3. **Sync Sequence** ✅
**Requirement:** Sync in specific order:
1. **Org Units** (first): FODepartment → FOCostCenter → FOLegalEntity → FODivision → FOBusinessUnit
2. **Positions** (second): Position
3. **Employees** (third): PerPerson → User

**Status:** Already implemented correctly in `auto_sync.py` (lines 266-278)

## Sync Flow

```
Phase 1: Org Units (establishes hierarchy)
├── FODepartment
├── FOCostCenter
├── FOLegalEntity
├── FODivision
└── FOBusinessUnit

Phase 2: Positions (depends on org units)
└── Position

Phase 3: Employees (depends on positions)
├── PerPerson
└── User
```

## API Endpoint Format

All SuccessFactors API calls now use:
```
/odata/v2/{EntityName}?format=json&$top=1000
```

Example:
- `/odata/v2/FODepartment?format=json&$top=1000`
- `/odata/v2/Position?format=json&$top=1000`
- `/odata/v2/PerPerson?format=json&$top=1000`

## Testing

1. **Restart HRIS Service:**
   ```bash
   cd backend/hris-service
   uvicorn main:app --reload --host 0.0.0.0 --port 8002
   ```

2. **Try Auto Sync:**
   - Go to UI → HRIS Connections
   - Click "Auto Sync"
   - Enter credentials
   - Click "Start Auto Sync"

3. **Expected Behavior:**
   - ✅ No more JSONB encoding errors
   - ✅ API calls use `format=json&$top=1000`
   - ✅ Sync happens in correct sequence:
     - Org Units first (FODepartment, FOCostCenter, etc.)
     - Positions second
     - Employees last (PerPerson, User)
   - ✅ Progress messages show current phase and entity

## Logs to Watch

The sync will log:
```
Starting sequential sync: 8 entities found
Phase 1 - Org Units: ['FODepartment', 'FOCostCenter', 'FOLegalEntity', 'FODivision', 'FOBusinessUnit']
Phase 2 - Positions: ['Position']
Phase 3 - Employees: ['PerPerson', 'User']
Syncing FODepartment -> org_unit...
✓ FODepartment: Fetched 50 records
✓ FODepartment: Sent 50 records to org-service
...
```

## All Fixed! 🎉

The sync will now:
1. ✅ Create connections without JSONB errors
2. ✅ Use correct API format (`format=json&$top=1000`)
3. ✅ Sync in the correct sequence (Org Units → Positions → Employees)
4. ✅ Process entities one at a time (not all at once)
