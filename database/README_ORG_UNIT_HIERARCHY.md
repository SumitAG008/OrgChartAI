# Organizational Unit Hierarchy System

## Overview

This system addresses the critical need to properly handle organizational unit types, hierarchy levels, and parent-child relationships from HRIS systems.

## Problem Statement

HRIS systems (like SuccessFactors) have different org unit types:
- Legal Entity
- Business Unit (FOBusinessUnit)
- Division (FODivision)
- Department (FODepartment)
- Cost Center (FOCostCenter)
- Custom org unit types

The system needs to:
1. **Identify org unit types** from HRIS data
2. **Determine hierarchy levels** (which type is at which level)
3. **Validate parent-child relationships** (e.g., Department can be child of Division, but not of Team)
4. **Map HRIS types to internal types** (e.g., "FOBusinessUnit" → "BusinessUnit")

## Solution

### 1. Database Schema Updates

#### `org_unit` Table Enhancements:
- `hierarchy_level` (INTEGER): Level in hierarchy (1 = top, 2 = second, etc.)
- `parent_hris_id` (TEXT): HRIS ID of parent (for syncing)
- `hris_id` (TEXT): HRIS system ID
- `hris_source` (TEXT): HRIS system name (e.g., "successfactors")
- `hris_type` (TEXT): Original type from HRIS (e.g., "FOBusinessUnit")
- `custom_type` (TEXT): For custom org unit types
- `type` (TEXT): Made flexible (removed fixed enum constraint)

#### New Tables:

**`org_unit_type_hierarchy`**: Defines valid parent-child relationships
```sql
- parent_type: Type of parent org unit
- child_type: Type of child org unit
- hierarchy_level: Level of child in hierarchy
- is_allowed: Whether relationship is valid
```

**`hris_org_unit_type_mapping`**: Maps HRIS types to internal types
```sql
- hris_source: HRIS system name
- hris_type: Original type from HRIS
- internal_type: Our internal type
- hierarchy_level: Hierarchy level
```

### 2. Hierarchy Resolution Service

The `HierarchyResolver` service:
- Maps HRIS types to internal types
- Validates parent-child relationships
- Resolves parent org units by HRIS ID
- Determines hierarchy levels

### 3. Flexible Hierarchy Rules

**Important**: The hierarchy is NOT fixed! Different organizations have different structures.

The system allows flexible parent-child relationships:
- LegalEntity can be parent of: BusinessUnit, Division, Department, Region, CostCenter
- BusinessUnit can be parent of: Division, Department, CostCenter, Team, Region
- Division can be parent of: Department, CostCenter, Team, Region
- Department can be parent of: CostCenter, Team (and even sub-Departments)
- CostCenter can be parent of: Team

**Examples of valid hierarchies:**
```
Example 1: LegalEntity → BusinessUnit → Department
Example 2: LegalEntity → Division → Department → Team
Example 3: LegalEntity → Department (skipping levels)
Example 4: LegalEntity → Region → BusinessUnit → Department
Example 5: Department → Department (sub-departments)
```

**Level Calculation**: Hierarchy levels are calculated from actual parent-child relationships, not fixed. A Department can be at level 2, 3, 4, or any level depending on its position in the actual org structure.

### 4. SuccessFactors Type Mappings

Default mappings (levels are flexible, calculated from relationships):
- `LegalEntity` → `LegalEntity` (typically top level, but flexible)
- `FOBusinessUnit` → `BusinessUnit` (level determined by parent)
- `FODivision` → `Division` (level determined by parent)
- `FODepartment` → `Department` (level determined by parent)
- `FOCostCenter` → `CostCenter` (level determined by parent)

## Usage

### 1. Run Schema Updates

```bash
# Run the hierarchy schema
psql -d your_database -f database/org_unit_hierarchy_schema.sql
```

### 2. Customize Type Mappings

Add custom HRIS type mappings:
```sql
INSERT INTO hris_org_unit_type_mapping 
(hris_source, hris_type, internal_type, hierarchy_level, description)
VALUES 
('successfactors', 'CustomOrgUnit', 'Department', 4, 'Custom org unit type');
```

### 3. Customize Hierarchy Rules

Add custom parent-child relationships:
```sql
INSERT INTO org_unit_type_hierarchy 
(parent_type, child_type, hierarchy_level, description)
VALUES 
('BusinessUnit', 'CustomType', 3, 'Custom type under Business Unit');
```

### 4. Use in Data Transformation

```python
from app.services.data_transformer import DataTransformer
from app.services.hierarchy_resolver import HierarchyResolver

# Initialize with database session
transformer = DataTransformer(db=db_session)

# Transform org unit (automatically resolves type and hierarchy)
org_unit_data = await transformer.transform_successfactors_org_unit(
    sf_org_unit,
    entity_name="FOBusinessUnit"  # Entity name from $metadata
)
```

## How It Works

### Step 1: Type Detection
When syncing from SuccessFactors:
1. System identifies entity name (e.g., "FOBusinessUnit")
2. Looks up mapping in `hris_org_unit_type_mapping`
3. Gets internal type ("BusinessUnit") and hierarchy level (2)

### Step 2: Parent Resolution
1. System gets `parentOrgUnitId` from SuccessFactors
2. Looks up parent by `hris_id` in `org_unit` table
3. Validates relationship using `org_unit_type_hierarchy`
4. Links parent-child relationship

### Step 3: Hierarchy Building
1. All org units are processed with their types and levels
2. System builds hierarchy tree based on parent-child relationships
3. Validates that hierarchy follows rules (e.g., Department cannot be parent of Legal Entity)

## Benefits

1. **Flexible**: Supports any org unit type (not just fixed enum)
2. **Validated**: Ensures parent-child relationships make sense
3. **Configurable**: Can customize mappings and rules per customer
4. **Traceable**: Stores original HRIS type for reference
5. **Scalable**: Works with multiple HRIS systems

## Example: SuccessFactors Sync

```
SuccessFactors Data:
- FOBusinessUnit: "Sales BU" (parent: LegalEntity "ACME Corp")
- FODepartment: "Sales Team" (parent: FOBusinessUnit "Sales BU")

↓ Maps to ↓

OrgChartAI:
- BusinessUnit: "Sales BU" 
  - hierarchy_level: 2
  - type: "BusinessUnit"
  - hris_type: "FOBusinessUnit"
  - parent: LegalEntity "ACME Corp"
  
- Department: "Sales Team"
  - hierarchy_level: 4
  - type: "Department"
  - hris_type: "FODepartment"
  - parent: BusinessUnit "Sales BU"
```

## Migration Notes

1. Existing `org_unit` records will need `hierarchy_level` populated
2. Run migration script to backfill hierarchy levels
3. Update any code that relies on fixed enum for `type` field
4. Test parent-child relationship validation
