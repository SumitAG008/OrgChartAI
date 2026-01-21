# SuccessFactors Data Model Alignment Fix

**Issue:** Application not fetching data from SuccessFactors due to data model misalignment

**Date:** 2026-01-21

---

## Problem

The original data models expected simple field names like `userId`, `firstName`, `orgUnitName`, but SuccessFactors actually returns:
- `name_defaultValue` instead of `name`
- `externalCode` as the primary key
- `name_en_US` for localized names
- Status codes like "A"/"I" instead of "Active"/"Inactive"
- Complex nested structures

## Solution

Created **3 new files** that properly align with SuccessFactors data model:

### 1. `models_successfactors.py` (New)
**Proper SuccessFactors models matching actual API response**

Key changes:
- `FOBusinessUnit`, `FODepartment`, `FODivision`, `FOCostCenter`, `FOLegalEntity`, `FOLocation`
- Proper field names: `externalCode`, `name_defaultValue`, `name_en_US`
- Status transformations: "A" → "Active", "I" → "Inactive"
- Complete field mapping configuration

### 2. `sf_data_transformer.py` (New)
**Enhanced transformer that handles real SF structure**

Features:
- Transforms SF field names to OrgChartAI schema
- Handles multiple name fields (name_defaultValue, name_en_US)
- Resolves hierarchical relationships (parent lookups)
- Status code transformations
- Date/datetime handling
- Reference resolution (HRIS IDs to internal IDs)

### 3. `test_sf_connection.py` (New)
**Test script to verify connection and see actual SF data**

Run this to:
- Test your SF connection
- Fetch sample data from all entities
- See actual field names and structure
- Test data transformation
- Generate field mapping report

---

## Quick Start

### Step 1: Update Your Credentials

Edit `test_sf_connection.py`:

```python
COMPANY_ID = "YOUR_COMPANY_ID"  # e.g., "SFPART123456"
USERNAME = "YOUR_USERNAME"       # e.g., "apiuser" (without @COMPANY_ID)
PASSWORD = "YOUR_PASSWORD"
API_URL = "https://api.successfactors.eu"  # or .com for US
```

### Step 2: Run Test Script

```bash
cd /home/user/OrgChartAI/backend/hris-service

# Activate venv if needed
source ../venv/bin/activate  # Linux/Mac
# OR
../venv/Scripts/activate  # Windows

# Run test
python test_sf_connection.py
```

### Step 3: Review Output

The script will:
1. ✅ Test connection
2. 📊 Fetch data from all entities (User, Position, FOBusinessUnit, FODepartment, etc.)
3. 🔄 Show transformation examples
4. 📋 Generate field mapping report

### Step 4: Verify Data Structure

Check the output to see:
- Which entities are available in your SF instance
- Actual field names in your data
- Transformed data ready for OrgChartAI

---

## What Changed

### Before (Not Working) ❌

```python
class SuccessFactorsOrgUnit(BaseModel):
    orgUnitId: str
    orgUnitName: Optional[str] = None  # WRONG - SF uses name_defaultValue
    parentOrgUnitId: Optional[str] = None
```

### After (Working) ✅

```python
class FOBusinessUnit(BaseModel):
    externalCode: str  # ✅ Correct primary key
    name_defaultValue: Optional[str] = None  # ✅ Correct field name
    name_en_US: Optional[str] = None  # ✅ Alternative name field
    parent: Optional[str] = None  # ✅ Correct parent reference
    status: Optional[str] = None  # ✅ "A" or "I"
```

### Transformation

```python
# SF Data
{
  "externalCode": "BU001",
  "name_defaultValue": "Engineering Division",
  "status": "A",
  "parent": "BU000"
}

# Transformed to OrgChartAI
{
  "code": "BU001",
  "name": "Engineering Division",
  "status": "Active",  # ✅ Transformed from "A"
  "parent_hris_id": "BU000",
  "hris_source": "successfactors",
  "type": "Business Unit"
}
```

---

## Field Mappings

### FOBusinessUnit → org_unit

| SuccessFactors Field | OrgChartAI Field | Notes |
|---------------------|------------------|-------|
| `externalCode` | `code` | Primary key |
| `name_defaultValue` | `name` | Default name |
| `name_en_US` | `name` | Fallback |
| `status` | `status` | "A" → "Active" |
| `parent` | `parent_org_unit_id` | Lookup |
| `startDate` | `effective_start_date` | Date |
| `endDate` | `effective_end_date` | Date |

### User → employee

| SuccessFactors Field | OrgChartAI Field | Notes |
|---------------------|------------------|-------|
| `userId` | `employee_number` | Primary key |
| `custom01` | `employee_number` | Often used for EmpID |
| `firstName` | `first_name` | - |
| `lastName` | `last_name` | - |
| `email` | `email` | - |
| `status` | `status` | "t" → "Active" |
| `department` | `org_unit_id` | Lookup |
| `manager` | `manager_id` | Lookup |
| `hireDate` | `hire_date` | Date |

### Position → position

| SuccessFactors Field | OrgChartAI Field | Notes |
|---------------------|------------------|-------|
| `code` | `position_code` | Primary key |
| `externalName_defaultValue` | `position_title` | Default title |
| `externalName_en_US` | `position_title` | Fallback |
| `department` | `org_unit_id` | Lookup |
| `parentPosition` | `reports_to_position_id` | Lookup |
| `incumbent` | `employee_id` | Lookup |
| `effectiveStartDate` | `effective_start_date` | Date |

---

## Next Steps

### 1. Update HRIS Service Router

Update `app/routers/successfactors.py` to use new transformer:

```python
from app.services.sf_data_transformer import SFDataTransformer

@router.get("/business-units")
async def get_business_units(...):
    client = SuccessFactorsClient(...)

    # Fetch from SF
    result = await client._make_request("FOBusinessUnit", params={"$top": limit})

    # Transform using new transformer
    transformer = SFDataTransformer()
    raw_data = transformer.extract_odata_results(result)
    transformed = transformer.transform_org_units(raw_data, entity_type="FOBusinessUnit")

    return {
        "count": len(transformed),
        "business_units": transformed
    }
```

### 2. Create Sync Service

Update sync service to use new transformer:

```python
from app.services.sf_data_transformer import SFDataTransformer

async def sync_org_units(connection_id: str, entity_type: str = "FOBusinessUnit"):
    # Fetch from SF
    client = get_sf_client(connection_id)
    result = await client._make_request(entity_type)

    # Transform
    transformer = SFDataTransformer()
    raw_data = transformer.extract_odata_results(result)
    transformed = transformer.transform_org_units(raw_data, entity_type=entity_type)

    # Insert into database
    for org_unit_data in transformed:
        # Insert logic here
        pass
```

### 3. Run Full Sync

Once verified:
1. Use the HRIS UI to configure connection
2. Map fields using the field mapping UI
3. Run sync to import all data
4. Verify data in org chart view

---

## Troubleshooting

### Issue: Still getting empty results

**Check:**
1. Entity name is correct (case-sensitive): `FOBusinessUnit` not `FoBusinessUnit`
2. User has permissions to read that entity
3. Data exists in that entity (check in SF UI)

### Issue: Fields are null after transformation

**Check:**
1. Field name matches exactly (case-sensitive)
2. SF uses localized fields (try `name_en_US` if `name_defaultValue` is null)
3. Review test script output to see actual field names

### Issue: Parent relationships not working

**Solution:**
1. Run sync in correct order: Org Units → Positions → Employees
2. Use `resolve_references()` after all entities are synced
3. Check parent HRIS IDs exist in lookup cache

---

## API Endpoints to Update

Add these new endpoints to `successfactors.py`:

```python
@router.get("/business-units")
async def get_business_units(...)

@router.get("/departments")
async def get_departments(...)

@router.get("/divisions")
async def get_divisions(...)

@router.get("/cost-centers")
async def get_cost_centers(...)

@router.get("/legal-entities")
async def get_legal_entities(...)
```

All using the new transformer.

---

## Files Changed/Added

### New Files ✨
- `app/models_successfactors.py` - Proper SF data models
- `app/services/sf_data_transformer.py` - Enhanced transformer
- `test_sf_connection.py` - Test script

### Files to Update 📝
- `app/routers/successfactors.py` - Use new transformer
- `app/services/sync_service.py` - Use new transformer
- `app/services/successfactors_client.py` - Already correct ✅

---

## Testing Checklist

- [ ] Run `test_sf_connection.py` successfully
- [ ] Verify connection test passes
- [ ] See data returned from FOBusinessUnit
- [ ] See data returned from User
- [ ] See data returned from Position
- [ ] Check transformation output looks correct
- [ ] Review field mapping report
- [ ] Update any custom field mappings
- [ ] Run sync in HRIS UI
- [ ] Verify data appears in database
- [ ] Check org chart displays correctly

---

## Support

If you encounter issues:

1. **Check SF Documentation:**
   - [OData API Guide](https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM)
   - Entity definitions for your SF version

2. **Run Test Script:**
   ```bash
   python test_sf_connection.py
   ```

3. **Check Logs:**
   ```bash
   tail -f logs/hris-service.log
   ```

4. **GitHub Issues:**
   https://github.com/SumitAG008/OrgChartAI/issues

---

**Status:** ✅ Ready to Test
**Last Updated:** 2026-01-21

