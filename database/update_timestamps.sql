-- Update all existing tables to use TIMESTAMP instead of DATE
-- Run this after schema.sql to update date fields to timestamps

-- Update org_unit
ALTER TABLE org_unit 
    ALTER COLUMN effective_start_date TYPE TIMESTAMP USING effective_start_date::TIMESTAMP,
    ALTER COLUMN effective_end_date TYPE TIMESTAMP USING effective_end_date::TIMESTAMP,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET NOT NULL,
    ALTER COLUMN created_by SET NOT NULL,
    ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

-- Update position
ALTER TABLE position 
    ALTER COLUMN effective_start_date TYPE TIMESTAMP USING effective_start_date::TIMESTAMP,
    ALTER COLUMN effective_end_date TYPE TIMESTAMP USING effective_end_date::TIMESTAMP,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET NOT NULL,
    ALTER COLUMN created_by SET NOT NULL,
    ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

-- Update employee
ALTER TABLE employee 
    ALTER COLUMN hire_date TYPE TIMESTAMP USING hire_date::TIMESTAMP,
    ALTER COLUMN termination_date TYPE TIMESTAMP USING termination_date::TIMESTAMP,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET NOT NULL,
    ALTER COLUMN created_by SET NOT NULL,
    ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

-- Update assignment
ALTER TABLE assignment 
    ALTER COLUMN start_date TYPE TIMESTAMP USING start_date::TIMESTAMP,
    ALTER COLUMN end_date TYPE TIMESTAMP USING end_date::TIMESTAMP,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET NOT NULL,
    ALTER COLUMN created_by SET NOT NULL,
    ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

-- Update all other tables with created_at/updated_at
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
    LOOP
        -- Add created_at if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = r.table_name AND column_name = 'created_at'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP', r.table_name);
        END IF;
        
        -- Add updated_at if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = r.table_name AND column_name = 'updated_at'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP', r.table_name);
        END IF;
        
        -- Add created_by if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = r.table_name AND column_name = 'created_by'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN created_by UUID', r.table_name);
        END IF;
        
        -- Add updated_by if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = r.table_name AND column_name = 'updated_by'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN updated_by UUID', r.table_name);
        END IF;
        
        -- Add version if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = r.table_name AND column_name = 'version'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN version INTEGER NOT NULL DEFAULT 1', r.table_name);
        END IF;
    END LOOP;
END $$;
