-- ============================================
-- ORGANIZATIONAL UNIT HIERARCHY ENHANCEMENTS
-- ============================================
-- This schema addresses:
-- 1. Flexible org unit types (not just fixed enum)
-- 2. Hierarchy levels for determining parent-child relationships
-- 3. HRIS type mapping for different HRIS systems
-- 4. Hierarchy validation rules

-- ============================================
-- 1. UPDATE ORG_UNIT TABLE
-- ============================================

-- Add hierarchy level and parent HRIS ID to org_unit
ALTER TABLE org_unit 
ADD COLUMN IF NOT EXISTS hierarchy_level INTEGER,
ADD COLUMN IF NOT EXISTS parent_hris_id TEXT,
ADD COLUMN IF NOT EXISTS hris_id TEXT,
ADD COLUMN IF NOT EXISTS hris_source TEXT,
ADD COLUMN IF NOT EXISTS hris_type TEXT, -- Original type from HRIS (e.g., "FOBusinessUnit", "FODepartment")
ADD COLUMN IF NOT EXISTS custom_type TEXT; -- For custom org unit types

-- Create indexes for hierarchy queries
CREATE INDEX IF NOT EXISTS idx_org_unit_hierarchy_level ON org_unit(hierarchy_level);
CREATE INDEX IF NOT EXISTS idx_org_unit_hris_id ON org_unit(hris_id, hris_source);
CREATE INDEX IF NOT EXISTS idx_org_unit_parent_hris_id ON org_unit(parent_hris_id, hris_source);
CREATE INDEX IF NOT EXISTS idx_org_unit_type ON org_unit(type);

-- ============================================
-- 2. ORG UNIT TYPE HIERARCHY CONFIGURATION
-- ============================================
-- Defines which org unit types can be parents of which other types
-- and their hierarchy levels

CREATE TABLE IF NOT EXISTS org_unit_type_hierarchy (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_type TEXT NOT NULL,
    child_type TEXT NOT NULL,
    hierarchy_level INTEGER NOT NULL, -- Level of child (1 = top level, 2 = second level, etc.)
    is_allowed BOOLEAN DEFAULT TRUE, -- Whether this parent-child relationship is allowed
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_type, child_type)
);

CREATE INDEX IF NOT EXISTS idx_org_unit_type_hierarchy_parent ON org_unit_type_hierarchy(parent_type);
CREATE INDEX IF NOT EXISTS idx_org_unit_type_hierarchy_child ON org_unit_type_hierarchy(child_type);
CREATE INDEX IF NOT EXISTS idx_org_unit_type_hierarchy_level ON org_unit_type_hierarchy(hierarchy_level);

-- ============================================
-- 3. HRIS TYPE MAPPING
-- ============================================
-- Maps HRIS system org unit types to our internal types
-- Example: SuccessFactors "FOBusinessUnit" -> "BusinessUnit"

CREATE TABLE IF NOT EXISTS hris_org_unit_type_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hris_source TEXT NOT NULL, -- 'successfactors', 'workday', etc.
    hris_type TEXT NOT NULL, -- Original type from HRIS (e.g., "FOBusinessUnit", "FODepartment")
    internal_type TEXT NOT NULL, -- Our internal type (e.g., "BusinessUnit", "Department")
    hierarchy_level INTEGER NOT NULL, -- Hierarchy level (1 = top, 2 = second, etc.)
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hris_source, hris_type)
);

CREATE INDEX IF NOT EXISTS idx_hris_type_mapping_source ON hris_org_unit_type_mapping(hris_source);
CREATE INDEX IF NOT EXISTS idx_hris_type_mapping_internal ON hris_org_unit_type_mapping(internal_type);
CREATE INDEX IF NOT EXISTS idx_hris_type_mapping_level ON hris_org_unit_type_mapping(hierarchy_level);

-- ============================================
-- 4. DEFAULT HIERARCHY RULES
-- ============================================
-- Flexible hierarchy rules - allows any valid parent-child relationship
-- Hierarchy levels are determined by actual data, not enforced
-- Only validates that relationships make logical sense

INSERT INTO org_unit_type_hierarchy (parent_type, child_type, hierarchy_level, description) VALUES
-- Legal Entity can be parent of many types (top level)
('ROOT', 'LegalEntity', 1, 'Legal Entity is the top level org unit'),
('LegalEntity', 'BusinessUnit', NULL, 'Business Unit can report to Legal Entity'),
('LegalEntity', 'Division', NULL, 'Division can report directly to Legal Entity'),
('LegalEntity', 'Department', NULL, 'Department can report directly to Legal Entity'),
('LegalEntity', 'Region', NULL, 'Region can report to Legal Entity'),
('LegalEntity', 'CostCenter', NULL, 'Cost Center can report to Legal Entity'),

-- Business Unit can be parent of multiple types
('BusinessUnit', 'Division', NULL, 'Division can report to Business Unit'),
('BusinessUnit', 'Department', NULL, 'Department can report to Business Unit'),
('BusinessUnit', 'CostCenter', NULL, 'Cost Center can report to Business Unit'),
('BusinessUnit', 'Team', NULL, 'Team can report to Business Unit'),
('BusinessUnit', 'Region', NULL, 'Region can report to Business Unit'),

-- Division can be parent of multiple types
('Division', 'Department', NULL, 'Department can report to Division'),
('Division', 'CostCenter', NULL, 'Cost Center can report to Division'),
('Division', 'Team', NULL, 'Team can report to Division'),
('Division', 'Region', NULL, 'Region can report to Division'),

-- Department can be parent of multiple types
('Department', 'CostCenter', NULL, 'Cost Center can report to Department'),
('Department', 'Team', NULL, 'Team can report to Department'),

-- Cost Center can be parent of Team
('CostCenter', 'Team', NULL, 'Team can report to Cost Center'),

-- Region can be parent of multiple types (geographic hierarchy)
('Region', 'BusinessUnit', NULL, 'Business Unit can report to Region'),
('Region', 'Division', NULL, 'Division can report to Region'),
('Region', 'Department', NULL, 'Department can report to Region'),

-- Allow same-type hierarchies (e.g., Department → Department for sub-departments)
('Department', 'Department', NULL, 'Department can have sub-departments'),
('Division', 'Division', NULL, 'Division can have sub-divisions'),
('BusinessUnit', 'BusinessUnit', NULL, 'Business Unit can have sub-business units')
ON CONFLICT (parent_type, child_type) DO NOTHING;

-- ============================================
-- 5. DEFAULT SUCCESSFACTORS TYPE MAPPINGS
-- ============================================
-- Maps SuccessFactors org unit types to our internal types
-- hierarchy_level is NULL to allow flexible hierarchy
-- Actual level is calculated from parent-child relationships

INSERT INTO hris_org_unit_type_mapping (hris_source, hris_type, internal_type, hierarchy_level, description) VALUES
('successfactors', 'LegalEntity', 'LegalEntity', NULL, 'SuccessFactors Legal Entity (typically top level)'),
('successfactors', 'FOBusinessUnit', 'BusinessUnit', NULL, 'SuccessFactors Business Unit (flexible level)'),
('successfactors', 'FODivision', 'Division', NULL, 'SuccessFactors Division (flexible level)'),
('successfactors', 'FODepartment', 'Department', NULL, 'SuccessFactors Department (flexible level)'),
('successfactors', 'FOCostCenter', 'CostCenter', NULL, 'SuccessFactors Cost Center (flexible level)'),
('successfactors', 'OrgUnit', 'Department', NULL, 'Generic SuccessFactors Org Unit (defaults to Department)'),
('successfactors', 'CustomOrgUnit', 'Department', NULL, 'Custom SuccessFactors Org Unit (defaults to Department)')
ON CONFLICT (hris_source, hris_type) DO NOTHING;

-- ============================================
-- 6. HELPER FUNCTIONS
-- ============================================

-- Function to get hierarchy level for an org unit type (if specified)
-- Returns NULL if level is flexible
CREATE OR REPLACE FUNCTION get_org_unit_hierarchy_level(org_unit_type TEXT)
RETURNS INTEGER AS $$
DECLARE
    level_val INTEGER;
BEGIN
    SELECT MIN(hierarchy_level) INTO level_val
    FROM org_unit_type_hierarchy
    WHERE child_type = org_unit_type
    AND hierarchy_level IS NOT NULL;
    
    RETURN level_val; -- Returns NULL if no fixed level
END;
$$ LANGUAGE plpgsql;

-- Function to calculate hierarchy level from actual parent-child relationships
CREATE OR REPLACE FUNCTION calculate_org_unit_level(org_unit_id UUID)
RETURNS INTEGER AS $$
DECLARE
    level_val INTEGER := 1;
    current_parent_id UUID;
    current_type TEXT;
BEGIN
    -- Start from the org unit
    SELECT parent_org_unit_id, type INTO current_parent_id, current_type
    FROM org_unit
    WHERE id = org_unit_id;
    
    -- If it's a LegalEntity or has no parent, it's level 1
    IF current_type = 'LegalEntity' OR current_parent_id IS NULL THEN
        RETURN 1;
    END IF;
    
    -- Traverse up the hierarchy to count levels
    WHILE current_parent_id IS NOT NULL LOOP
        level_val := level_val + 1;
        
        SELECT parent_org_unit_id INTO current_parent_id
        FROM org_unit
        WHERE id = current_parent_id;
        
        -- Safety check to prevent infinite loops
        IF level_val > 20 THEN
            RETURN level_val;
        END IF;
    END LOOP;
    
    RETURN level_val;
END;
$$ LANGUAGE plpgsql;

-- Function to validate parent-child relationship
CREATE OR REPLACE FUNCTION is_valid_parent_child(
    parent_type TEXT,
    child_type TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM org_unit_type_hierarchy
        WHERE parent_type = is_valid_parent_child.parent_type
        AND child_type = is_valid_parent_child.child_type
        AND is_allowed = TRUE
    );
END;
$$ LANGUAGE plpgsql;

-- Function to map HRIS type to internal type
CREATE OR REPLACE FUNCTION map_hris_type_to_internal(
    hris_source_name TEXT,
    hris_type_name TEXT
)
RETURNS TEXT AS $$
DECLARE
    mapped_type TEXT;
BEGIN
    SELECT internal_type INTO mapped_type
    FROM hris_org_unit_type_mapping
    WHERE hris_source = hris_source_name
    AND hris_type = hris_type_name
    AND is_active = TRUE;
    
    RETURN COALESCE(mapped_type, 'Department'); -- Default to Department if not found
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 7. VIEWS FOR HIERARCHY QUERIES
-- ============================================

-- View to show org unit hierarchy with levels
CREATE OR REPLACE VIEW org_unit_hierarchy_view AS
SELECT 
    ou.id,
    ou.code,
    ou.name,
    ou.type,
    ou.hierarchy_level,
    ou.hris_id,
    ou.hris_source,
    ou.hris_type,
    ou.parent_org_unit_id,
    ou.parent_hris_id,
    parent_ou.name AS parent_name,
    parent_ou.type AS parent_type,
    parent_ou.hierarchy_level AS parent_level
FROM org_unit ou
LEFT JOIN org_unit parent_ou ON ou.parent_org_unit_id = parent_ou.id;

-- View to show org units with their HRIS mappings
CREATE OR REPLACE VIEW org_unit_hris_mapping_view AS
SELECT 
    ou.id,
    ou.code,
    ou.name,
    ou.type AS internal_type,
    ou.hris_type,
    ou.hris_source,
    ou.hierarchy_level,
    mapping.internal_type AS mapped_type,
    mapping.hierarchy_level AS mapped_level
FROM org_unit ou
LEFT JOIN hris_org_unit_type_mapping mapping 
    ON ou.hris_source = mapping.hris_source 
    AND ou.hris_type = mapping.hris_type;
