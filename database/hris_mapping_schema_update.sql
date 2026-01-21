-- ============================================
-- UPDATE HRIS MAPPING SCHEMA
-- Add source_entity_name to hris_field_mapping
-- Fix hris_mapping_config to allow multiple source entities per target
-- ============================================

-- Add source_entity_name column to hris_field_mapping if it doesn't exist
ALTER TABLE hris_field_mapping 
ADD COLUMN IF NOT EXISTS source_entity_name TEXT;

-- Update unique constraint to include source_entity_name
-- First, drop the old constraint if it exists
ALTER TABLE hris_field_mapping 
DROP CONSTRAINT IF EXISTS hris_field_mapping_connection_id_entity_type_source_field_key;

-- Add new unique constraint that includes source_entity_name
ALTER TABLE hris_field_mapping 
ADD CONSTRAINT hris_field_mapping_unique 
UNIQUE(connection_id, entity_type, source_entity_name, source_field);

-- Create index for faster queries by source entity
CREATE INDEX IF NOT EXISTS idx_hris_mapping_source_entity 
ON hris_field_mapping(connection_id, entity_type, source_entity_name);

-- Fix hris_mapping_config: Remove UNIQUE constraint on connection_id
-- This allows multiple source entities per target entity
ALTER TABLE hris_mapping_config 
DROP CONSTRAINT IF EXISTS hris_mapping_config_connection_id_key;

-- Add new unique constraint that includes target_entity_type and source_entity_name
ALTER TABLE hris_mapping_config 
ADD CONSTRAINT hris_mapping_config_unique 
UNIQUE(connection_id, target_entity_type, source_entity_name);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_mapping_config_source_entity 
ON hris_mapping_config(connection_id, target_entity_type, source_entity_name);
