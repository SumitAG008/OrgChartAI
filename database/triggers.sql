-- Database Triggers for Automatic Timestamp Updates and Audit Trail
-- PostgreSQL Triggers for SaaS Application

-- ============================================
-- FUNCTION: Update updated_at timestamp
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================
-- FUNCTION: Create change history entry
-- ============================================

CREATE OR REPLACE FUNCTION create_change_history()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
    changed_fields TEXT[];
    field_name TEXT;
BEGIN
    -- Get old and new values as JSONB
    IF TG_OP = 'DELETE' THEN
        old_data = to_jsonb(OLD);
        new_data = NULL;
    ELSIF TG_OP = 'UPDATE' THEN
        old_data = to_jsonb(OLD);
        new_data = to_jsonb(NEW);
        
        -- Find changed fields
        FOR field_name IN SELECT jsonb_object_keys(new_data) LOOP
            IF old_data->>field_name IS DISTINCT FROM new_data->>field_name THEN
                changed_fields := array_append(changed_fields, field_name);
            END IF;
        END LOOP;
    ELSIF TG_OP = 'INSERT' THEN
        old_data = NULL;
        new_data = to_jsonb(NEW);
        changed_fields := ARRAY(SELECT jsonb_object_keys(new_data));
    END IF;
    
    -- Insert into change_history
    INSERT INTO change_history (
        table_name,
        record_id,
        action,
        old_values,
        new_values,
        changed_fields,
        changed_by,
        changed_at
    ) VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        old_data,
        new_data,
        changed_fields,
        COALESCE(NEW.updated_by, NEW.created_by, OLD.updated_by),
        CURRENT_TIMESTAMP
    );
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ language 'plpgsql';

-- ============================================
-- FUNCTION: Create version history entry
-- ============================================

CREATE OR REPLACE FUNCTION create_version_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO version_history (
            table_name,
            record_id,
            version,
            data,
            created_at,
            created_by
        ) VALUES (
            TG_TABLE_NAME,
            NEW.id,
            NEW.version,
            to_jsonb(NEW),
            CURRENT_TIMESTAMP,
            COALESCE(NEW.updated_by, NEW.created_by)
        );
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================
-- TRIGGERS: Update timestamps
-- ============================================

-- Org Unit triggers
CREATE TRIGGER update_org_unit_timestamp
    BEFORE UPDATE ON org_unit
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Position triggers
CREATE TRIGGER update_position_timestamp
    BEFORE UPDATE ON position
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Employee triggers
CREATE TRIGGER update_employee_timestamp
    BEFORE UPDATE ON employee
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Assignment triggers
CREATE TRIGGER update_assignment_timestamp
    BEFORE UPDATE ON assignment
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Job triggers
CREATE TRIGGER update_job_timestamp
    BEFORE UPDATE ON job
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- TRIGGERS: Create change history
-- ============================================

-- Org Unit audit
CREATE TRIGGER audit_org_unit_changes
    AFTER INSERT OR UPDATE OR DELETE ON org_unit
    FOR EACH ROW
    EXECUTE FUNCTION create_change_history();

-- Position audit
CREATE TRIGGER audit_position_changes
    AFTER INSERT OR UPDATE OR DELETE ON position
    FOR EACH ROW
    EXECUTE FUNCTION create_change_history();

-- Employee audit
CREATE TRIGGER audit_employee_changes
    AFTER INSERT OR UPDATE OR DELETE ON employee
    FOR EACH ROW
    EXECUTE FUNCTION create_change_history();

-- Assignment audit
CREATE TRIGGER audit_assignment_changes
    AFTER INSERT OR UPDATE OR DELETE ON assignment
    FOR EACH ROW
    EXECUTE FUNCTION create_change_history();

-- ============================================
-- TRIGGERS: Create version history
-- ============================================

-- Org Unit versioning
CREATE TRIGGER version_org_unit_changes
    AFTER UPDATE ON org_unit
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION create_version_history();

-- Position versioning
CREATE TRIGGER version_position_changes
    AFTER UPDATE ON position
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION create_version_history();

-- Employee versioning
CREATE TRIGGER version_employee_changes
    AFTER UPDATE ON employee
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION create_version_history();

-- ============================================
-- FUNCTION: Get change history for a record
-- ============================================

CREATE OR REPLACE FUNCTION get_change_history(
    p_table_name TEXT,
    p_record_id UUID,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    id UUID,
    action TEXT,
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    changed_by UUID,
    changed_at TIMESTAMP,
    change_reason TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ch.id,
        ch.action,
        ch.old_values,
        ch.new_values,
        ch.changed_fields,
        ch.changed_by,
        ch.changed_at,
        ch.change_reason
    FROM change_history ch
    WHERE ch.table_name = p_table_name
      AND ch.record_id = p_record_id
    ORDER BY ch.changed_at DESC
    LIMIT p_limit;
END;
$$ language 'plpgsql';

-- ============================================
-- FUNCTION: Get version at specific timestamp
-- ============================================

CREATE OR REPLACE FUNCTION get_version_at_timestamp(
    p_table_name TEXT,
    p_record_id UUID,
    p_timestamp TIMESTAMP
)
RETURNS JSONB AS $$
DECLARE
    v_version JSONB;
BEGIN
    SELECT data INTO v_version
    FROM version_history
    WHERE table_name = p_table_name
      AND record_id = p_record_id
      AND created_at <= p_timestamp
    ORDER BY version DESC
    LIMIT 1;
    
    RETURN v_version;
END;
$$ language 'plpgsql';
