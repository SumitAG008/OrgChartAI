-- OrgChartAI Database Schema
-- PostgreSQL (Neon) Schema
-- Run this to create all tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. SUPPORTING TABLES
-- ============================================

-- Locations
CREATE TABLE IF NOT EXISTS location (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    city TEXT,
    timezone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_location_country ON location(country);

-- Cost Centers
CREATE TABLE IF NOT EXISTS cost_center (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    region TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legal Entities
CREATE TABLE IF NOT EXISTS legal_entity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_entity_country ON legal_entity(country);

-- ============================================
-- 2. ORGANIZATION STRUCTURE
-- ============================================

-- Organization Units
CREATE TABLE IF NOT EXISTS org_unit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    parent_org_unit_id UUID REFERENCES org_unit(id),
    type TEXT NOT NULL, -- Org unit type (flexible, validated by hierarchy rules)
    cost_center_id UUID REFERENCES cost_center(id),
    location_id UUID REFERENCES location(id),
    legal_entity_id UUID REFERENCES legal_entity(id),
    scope TEXT CHECK (scope IN ('Global', 'Regional', 'Country', 'Local')),
    tree_id TEXT,
    effective_start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_end_date TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('Active', 'Planned', 'Inactive')) DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_org_unit_parent ON org_unit(parent_org_unit_id);
CREATE INDEX IF NOT EXISTS idx_org_unit_tree ON org_unit(tree_id);
CREATE INDEX IF NOT EXISTS idx_org_unit_status ON org_unit(status);

-- Jobs (Job Profiles)
CREATE TABLE IF NOT EXISTS job (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_code TEXT NOT NULL UNIQUE,
    job_title TEXT NOT NULL,
    job_family TEXT,
    job_sub_family TEXT,
    default_grade TEXT,
    default_position_type TEXT CHECK (default_position_type IN ('Permanent', 'FixedTerm', 'Contract', 'Temporary', 'Intern')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_family ON job(job_family);

-- Positions
CREATE TABLE IF NOT EXISTS position (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_unit_id UUID NOT NULL REFERENCES org_unit(id),
    job_id UUID REFERENCES job(id),
    position_code TEXT NOT NULL UNIQUE,
    position_title TEXT NOT NULL,
    position_type TEXT NOT NULL CHECK (position_type IN ('Permanent', 'FixedTerm', 'Contract', 'Temporary', 'Intern')),
    reports_to_position_id UUID REFERENCES position(id),
    fte DECIMAL(3,2) CHECK (fte >= 0 AND fte <= 1) DEFAULT 1.0,
    grade TEXT,
    level INTEGER,
    is_managerial BOOLEAN DEFAULT FALSE,
    is_mass_position_template BOOLEAN DEFAULT FALSE,
    status TEXT NOT NULL CHECK (status IN ('Active', 'Planned', 'Frozen', 'Closed', 'Vacant')) DEFAULT 'Active',
    effective_start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_end_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_position_org_unit ON position(org_unit_id);
CREATE INDEX IF NOT EXISTS idx_position_reports_to ON position(reports_to_position_id);
CREATE INDEX IF NOT EXISTS idx_position_status ON position(status);
CREATE INDEX IF NOT EXISTS idx_position_job ON position(job_id);

-- ============================================
-- 3. EMPLOYEE TABLES
-- ============================================

-- Employees
CREATE TABLE IF NOT EXISTS employee (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_number TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    preferred_name TEXT,
    email TEXT NOT NULL UNIQUE,
    photo_url TEXT,
    employment_type TEXT NOT NULL CHECK (employment_type IN ('Permanent', 'FixedTerm', 'Contractor', 'Temporary')),
    legal_entity_id UUID REFERENCES legal_entity(id),
    primary_position_id UUID REFERENCES position(id),
    hire_date TIMESTAMP NOT NULL,
    termination_date TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('Active', 'OnLeave', 'Terminated')) DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_employee_status ON employee(status);
CREATE INDEX IF NOT EXISTS idx_employee_primary_position ON employee(primary_position_id);
CREATE INDEX IF NOT EXISTS idx_employee_legal_entity ON employee(legal_entity_id);

-- Assignments
CREATE TABLE IF NOT EXISTS assignment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employee(id),
    position_id UUID NOT NULL REFERENCES position(id),
    assignment_type TEXT NOT NULL CHECK (assignment_type IN ('Primary', 'Secondary', 'Temporary', 'Project')),
    reports_to_position_id UUID REFERENCES position(id),
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('Active', 'Completed', 'Planned')) DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_assignment_employee ON assignment(employee_id);
CREATE INDEX IF NOT EXISTS idx_assignment_position ON assignment(position_id);
CREATE INDEX IF NOT EXISTS idx_assignment_status ON assignment(status);
CREATE INDEX IF NOT EXISTS idx_assignment_type ON assignment(assignment_type);

-- ============================================
-- 4. SKILLS TABLES
-- ============================================

-- Skills Master
CREATE TABLE IF NOT EXISTS skill (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    description TEXT,
    is_core_skill BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skill_category ON skill(category);
CREATE INDEX IF NOT EXISTS idx_skill_code ON skill(code);

-- Employee Skills
CREATE TABLE IF NOT EXISTS employee_skill (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
    proficiency_level INTEGER NOT NULL CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    years_of_experience DECIMAL(4,1),
    last_validated_at TIMESTAMP,
    validated_by UUID,
    validation_method TEXT,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    is_primary_skill BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_employee_skill_employee ON employee_skill(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_skill_skill ON employee_skill(skill_id);
CREATE INDEX IF NOT EXISTS idx_employee_skill_level ON employee_skill(proficiency_level);

-- Job Skill Requirements
CREATE TABLE IF NOT EXISTS job_skill (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES job(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
    required_level INTEGER NOT NULL CHECK (required_level >= 1 AND required_level <= 5),
    is_mandatory BOOLEAN DEFAULT TRUE,
    weight DECIMAL(3,2) CHECK (weight >= 0 AND weight <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_job_skill_job ON job_skill(job_id);
CREATE INDEX IF NOT EXISTS idx_job_skill_skill ON job_skill(skill_id);

-- Position Skill Requirements
CREATE TABLE IF NOT EXISTS position_skill (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id UUID NOT NULL REFERENCES position(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
    required_level INTEGER NOT NULL CHECK (required_level >= 1 AND required_level <= 5),
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(position_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_position_skill_position ON position_skill(position_id);
CREATE INDEX IF NOT EXISTS idx_position_skill_skill ON position_skill(skill_id);

-- ============================================
-- 5. SCENARIO & M&A TABLES
-- ============================================

-- Scenarios
CREATE TABLE IF NOT EXISTS scenario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    tree_id TEXT NOT NULL UNIQUE,
    base_scenario_id UUID REFERENCES scenario(id),
    status TEXT NOT NULL CHECK (status IN ('Draft', 'Active', 'Archived')) DEFAULT 'Draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID
);

CREATE INDEX IF NOT EXISTS idx_scenario_status ON scenario(status);

-- Org Unit Mappings (for M&A)
CREATE TABLE IF NOT EXISTS org_unit_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_org_unit_id UUID NOT NULL REFERENCES org_unit(id),
    target_org_unit_id UUID NOT NULL REFERENCES org_unit(id),
    mapping_type TEXT NOT NULL CHECK (mapping_type IN ('Merge', 'Split', 'Move')),
    scenario_id TEXT NOT NULL,
    effective_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID
);

CREATE INDEX IF NOT EXISTS idx_mapping_source ON org_unit_mapping(source_org_unit_id);
CREATE INDEX IF NOT EXISTS idx_mapping_target ON org_unit_mapping(target_org_unit_id);
CREATE INDEX IF NOT EXISTS idx_mapping_scenario ON org_unit_mapping(scenario_id);

-- ============================================
-- 6. ANALYTICS TABLES
-- ============================================

-- Org Metrics (pre-calculated)
CREATE TABLE IF NOT EXISTS org_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_unit_id UUID NOT NULL REFERENCES org_unit(id),
    metric_date TIMESTAMP NOT NULL,
    headcount INTEGER NOT NULL DEFAULT 0,
    headcount_fte DECIMAL(10,2) NOT NULL DEFAULT 0,
    vacant_positions INTEGER NOT NULL DEFAULT 0,
    span_of_control_avg DECIMAL(5,2),
    span_of_control_max INTEGER,
    span_of_control_min INTEGER,
    permanent_count INTEGER DEFAULT 0,
    contract_count INTEGER DEFAULT 0,
    temporary_count INTEGER DEFAULT 0,
    layers_above INTEGER,
    layers_below INTEGER,
    total_compensation DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_unit_id, metric_date)
);

CREATE INDEX IF NOT EXISTS idx_org_metrics_org_unit ON org_metrics(org_unit_id);
CREATE INDEX IF NOT EXISTS idx_org_metrics_date ON org_metrics(metric_date);

-- Skill Gap Analysis
CREATE TABLE IF NOT EXISTS skill_gap_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_unit_id UUID REFERENCES org_unit(id),
    position_id UUID REFERENCES position(id),
    skill_id UUID NOT NULL REFERENCES skill(id),
    required_level INTEGER NOT NULL,
    current_level INTEGER,
    gap_size INTEGER NOT NULL,
    employees_affected INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_unit_id, position_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_skill_gap_org_unit ON skill_gap_analysis(org_unit_id);
CREATE INDEX IF NOT EXISTS idx_skill_gap_position ON skill_gap_analysis(position_id);
CREATE INDEX IF NOT EXISTS idx_skill_gap_skill ON skill_gap_analysis(skill_id);

-- ============================================
-- 7. CHANGE MANAGEMENT
-- ============================================

-- Change Packages
CREATE TABLE IF NOT EXISTS change_package (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario_id UUID REFERENCES scenario(id),
    change_type TEXT NOT NULL CHECK (change_type IN (
        'PositionMove', 'PositionCreate', 'PositionFreeze',
        'OrgUnitMove', 'OrgUnitMerge', 'OrgUnitSplit',
        'ReportingLineChange', 'BulkPositionCreate'
    )),
    change_data JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Draft', 'PendingApproval', 'Approved', 'SentToHRIS', 'Applied', 'Rejected')) DEFAULT 'Draft',
    requested_by UUID NOT NULL,
    approved_by UUID,
    approved_at TIMESTAMP,
    sent_to_hris_at TIMESTAMP,
    hris_response JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_change_package_scenario ON change_package(scenario_id);
CREATE INDEX IF NOT EXISTS idx_change_package_status ON change_package(status);
CREATE INDEX IF NOT EXISTS idx_change_package_type ON change_package(change_type);

-- ============================================
-- 8. FLEXIBLE ATTRIBUTES
-- ============================================

-- Attribute Definitions
CREATE TABLE IF NOT EXISTS org_attribute_definition (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    object_type TEXT NOT NULL CHECK (object_type IN ('OrganizationUnit', 'Position', 'Employee')),
    code TEXT NOT NULL,
    label TEXT NOT NULL,
    data_type TEXT NOT NULL CHECK (data_type IN ('String', 'Number', 'Boolean', 'Date', 'Enum')),
    allowed_values JSONB,
    is_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(object_type, code)
);

CREATE INDEX IF NOT EXISTS idx_attr_def_object_type ON org_attribute_definition(object_type);

-- Attribute Values
CREATE TABLE IF NOT EXISTS org_attribute_value (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    object_type TEXT NOT NULL CHECK (object_type IN ('OrganizationUnit', 'Position', 'Employee')),
    object_id UUID NOT NULL,
    attribute_definition_id UUID NOT NULL REFERENCES org_attribute_definition(id),
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(object_type, object_id, attribute_definition_id)
);

CREATE INDEX IF NOT EXISTS idx_attr_value_object ON org_attribute_value(object_type, object_id);
CREATE INDEX IF NOT EXISTS idx_attr_value_def ON org_attribute_value(attribute_definition_id);

-- ============================================
-- 9. AI RECOMMENDATIONS
-- ============================================

-- AI Recommendations
CREATE TABLE IF NOT EXISTS ai_recommendation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recommendation_type TEXT NOT NULL CHECK (recommendation_type IN (
        'TeamFormation', 'OrgDesign', 'SkillGap', 'InternalMobility',
        'Restructure', 'SpanOptimization', 'WorkforcePlanning'
    )),
    target_object_type TEXT NOT NULL CHECK (target_object_type IN ('OrgUnit', 'Position', 'Employee', 'Project', 'Scenario')),
    target_object_id UUID NOT NULL,
    recommendation_text TEXT NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    reasoning JSONB,
    suggested_actions JSONB,
    model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('Active', 'Accepted', 'Rejected', 'Expired')) DEFAULT 'Active'
);

CREATE INDEX IF NOT EXISTS idx_ai_recommendation_type ON ai_recommendation(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_ai_recommendation_target ON ai_recommendation(target_object_type, target_object_id);
CREATE INDEX IF NOT EXISTS idx_ai_recommendation_status ON ai_recommendation(status);

-- ============================================
-- 10. AUDIT & VERSIONING TABLES
-- ============================================

-- Users table for audit tracking
CREATE TABLE IF NOT EXISTS app_user (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('Admin', 'Manager', 'Viewer', 'Editor')),
    status TEXT NOT NULL CHECK (status IN ('Active', 'Inactive')) DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_email ON app_user(email);

-- Change History (tracks all changes for audit trail)
CREATE TABLE IF NOT EXISTS change_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    changed_by UUID NOT NULL REFERENCES app_user(id),
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    change_reason TEXT,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_change_history_table_record ON change_history(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_change_history_changed_at ON change_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_change_history_changed_by ON change_history(changed_by);

-- Version History (tracks versioned changes)
CREATE TABLE IF NOT EXISTS version_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    version INTEGER NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id),
    change_summary TEXT
);

CREATE INDEX IF NOT EXISTS idx_version_history_table_record ON version_history(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_version_history_version ON version_history(table_name, record_id, version);

-- ============================================
-- 11. AI/ML TABLES
-- ============================================

-- AI Model Configurations
CREATE TABLE IF NOT EXISTS ai_model_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name TEXT NOT NULL UNIQUE,
    model_type TEXT NOT NULL CHECK (model_type IN ('OrgChartGenerator', 'TeamFormation', 'OrgDesign', 'SkillInference')),
    provider TEXT NOT NULL CHECK (provider IN ('OpenAI', 'Anthropic', 'Local', 'MCP')),
    model_id TEXT NOT NULL,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id)
);

-- AI Generation History
CREATE TABLE IF NOT EXISTS ai_generation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    generation_type TEXT NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    model_config_id UUID REFERENCES ai_model_config(id),
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,4),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id)
);

CREATE INDEX IF NOT EXISTS idx_ai_generation_type ON ai_generation_history(generation_type);
CREATE INDEX IF NOT EXISTS idx_ai_generation_created_at ON ai_generation_history(created_at);

-- Auto-Generated Org Charts
CREATE TABLE IF NOT EXISTS auto_generated_chart (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    source_data JSONB NOT NULL,
    generated_chart JSONB NOT NULL,
    model_config_id UUID REFERENCES ai_model_config(id),
    generation_id UUID REFERENCES ai_generation_history(id),
    status TEXT NOT NULL CHECK (status IN ('Draft', 'Review', 'Approved', 'Rejected')) DEFAULT 'Draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id),
    approved_by UUID REFERENCES app_user(id),
    approved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_auto_chart_status ON auto_generated_chart(status);
CREATE INDEX IF NOT EXISTS idx_auto_chart_created_at ON auto_generated_chart(created_at);

-- ============================================
-- 12. VIEWS
-- ============================================

-- View: Active Employees with Positions
CREATE OR REPLACE VIEW v_active_employees AS
SELECT 
    e.id,
    e.employee_number,
    e.first_name,
    e.last_name,
    e.preferred_name,
    e.email,
    e.photo_url,
    e.employment_type,
    p.id as position_id,
    p.position_title,
    p.position_code,
    o.id as org_unit_id,
    o.name as org_unit_name,
    o.code as org_unit_code
FROM employee e
JOIN position p ON e.primary_position_id = p.id
JOIN org_unit o ON p.org_unit_id = o.id
WHERE e.status = 'Active'
  AND p.status = 'Active';

-- View: Vacant Positions
CREATE OR REPLACE VIEW v_vacant_positions AS
SELECT 
    p.*,
    o.name as org_unit_name,
    j.job_title
FROM position p
JOIN org_unit o ON p.org_unit_id = o.id
LEFT JOIN job j ON p.job_id = j.id
LEFT JOIN assignment a ON p.id = a.position_id 
    AND a.assignment_type = 'Primary' 
    AND a.status = 'Active'
WHERE p.status = 'Active'
  AND a.id IS NULL;

-- View: Employee Skills Summary
CREATE OR REPLACE VIEW v_employee_skills_summary AS
SELECT 
    e.id as employee_id,
    e.employee_number,
    e.preferred_name || ' ' || e.last_name as employee_name,
    s.id as skill_id,
    s.name as skill_name,
    s.category as skill_category,
    es.proficiency_level,
    es.years_of_experience,
    es.validation_method
FROM employee e
JOIN employee_skill es ON e.id = es.employee_id
JOIN skill s ON es.skill_id = s.id
WHERE e.status = 'Active'
  AND es.proficiency_level >= 3;

-- ============================================
-- END OF SCHEMA
-- ============================================
