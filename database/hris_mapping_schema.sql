-- ============================================
-- HRIS FIELD MAPPING TABLES
-- ============================================
-- Stores field mappings between HRIS systems and OrgChartAI

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Field Mappings Table
CREATE TABLE IF NOT EXISTS hris_field_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- 'org_unit', 'position', 'employee'
    source_field TEXT NOT NULL, -- Field name from HRIS (e.g., 'orgUnitId')
    target_field TEXT NOT NULL, -- Field name in OrgChartAI (e.g., 'hris_id')
    mapping_type TEXT NOT NULL DEFAULT 'direct', -- 'direct', 'transform', 'custom'
    transform_function TEXT, -- Optional transformation function/script
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    UNIQUE(connection_id, entity_type, source_field)
);

CREATE INDEX IF NOT EXISTS idx_hris_mapping_connection ON hris_field_mapping(connection_id);
CREATE INDEX IF NOT EXISTS idx_hris_mapping_entity_type ON hris_field_mapping(connection_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_hris_mapping_active ON hris_field_mapping(connection_id, entity_type, is_active);

-- Mapping Configuration (stores metadata about mappings)
CREATE TABLE IF NOT EXISTS hris_mapping_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id TEXT NOT NULL UNIQUE,
    target_entity_type TEXT NOT NULL, -- 'org_unit', 'position', 'employee'
    source_entity_name TEXT NOT NULL, -- HRIS entity name (e.g., 'FOBusinessUnit', 'OrgUnit')
    hris_source TEXT NOT NULL, -- 'successfactors', 'workday', etc.
    is_active BOOLEAN DEFAULT TRUE,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_mapping_config_connection ON hris_mapping_config(connection_id);
CREATE INDEX IF NOT EXISTS idx_mapping_config_active ON hris_mapping_config(connection_id, is_active);
