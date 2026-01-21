# Complete Database Schema
## PostgreSQL DDL for Org Intelligence Platform

---

## 📊 Core Tables

### **1. Organization Structure**

```sql
-- Organization Units
CREATE TABLE org_unit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    parent_org_unit_id UUID REFERENCES org_unit(id),
    type TEXT NOT NULL CHECK (type IN ('Division', 'Department', 'Team', 'Region', 'LegalEntity', 'CostCenterOwner', 'BusinessUnit')),
    cost_center_id UUID REFERENCES cost_center(id),
    location_id UUID REFERENCES location(id),
    legal_entity_id UUID REFERENCES legal_entity(id),
    scope TEXT CHECK (scope IN ('Global', 'Regional', 'Country', 'Local')),
    tree_id TEXT, -- For M&A scenarios: 'Current', 'Future', 'Scenario A', etc.
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    status TEXT NOT NULL CHECK (status IN ('Active', 'Planned', 'Inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_org_unit_parent ON org_unit(parent_org_unit_id);
CREATE INDEX idx_org_unit_tree ON org_unit(tree_id);
CREATE INDEX idx_org_unit_status ON org_unit(status);

-- Positions
CREATE TABLE position (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
    status TEXT NOT NULL CHECK (status IN ('Active', 'Planned', 'Frozen', 'Closed', 'Vacant')),
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_position_org_unit ON position(org_unit_id);
CREATE INDEX idx_position_reports_to ON position(reports_to_position_id);
CREATE INDEX idx_position_status ON position(status);
CREATE INDEX idx_position_job ON position(job_id);

-- Jobs (Job Profiles)
CREATE TABLE job (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

CREATE INDEX idx_job_family ON job(job_family);
```

### **2. Employee Tables**

```sql
-- Employees
CREATE TABLE employee (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_number TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    preferred_name TEXT,
    email TEXT NOT NULL UNIQUE,
    employment_type TEXT NOT NULL CHECK (employment_type IN ('Permanent', 'FixedTerm', 'Contractor', 'Temporary')),
    legal_entity_id UUID REFERENCES legal_entity(id),
    primary_position_id UUID REFERENCES position(id),
    hire_date DATE NOT NULL,
    termination_date DATE,
    status TEXT NOT NULL CHECK (status IN ('Active', 'OnLeave', 'Terminated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_employee_status ON employee(status);
CREATE INDEX idx_employee_primary_position ON employee(primary_position_id);
CREATE INDEX idx_employee_legal_entity ON employee(legal_entity_id);

-- Assignments
CREATE TABLE assignment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employee(id),
    position_id UUID NOT NULL REFERENCES position(id),
    assignment_type TEXT NOT NULL CHECK (assignment_type IN ('Primary', 'Secondary', 'Temporary', 'Project')),
    reports_to_position_id UUID REFERENCES position(id), -- For dotted-line reporting
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT NOT NULL CHECK (status IN ('Active', 'Completed', 'Planned')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_assignment_employee ON assignment(employee_id);
CREATE INDEX idx_assignment_position ON assignment(position_id);
CREATE INDEX idx_assignment_status ON assignment(status);
CREATE INDEX idx_assignment_type ON assignment(assignment_type);
```

### **3. Supporting Tables**

```sql
-- Locations
CREATE TABLE location (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    city TEXT,
    timezone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_location_country ON location(country);

-- Cost Centers
CREATE TABLE cost_center (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    region TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legal Entities
CREATE TABLE legal_entity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_legal_entity_country ON legal_entity(country);
```

### **4. Flexible Attribute System**

```sql
-- Attribute Definitions
CREATE TABLE org_attribute_definition (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_type TEXT NOT NULL CHECK (object_type IN ('OrganizationUnit', 'Position', 'Employee')),
    code TEXT NOT NULL,
    label TEXT NOT NULL,
    data_type TEXT NOT NULL CHECK (data_type IN ('String', 'Number', 'Boolean', 'Date', 'Enum')),
    allowed_values JSONB, -- For enum types
    is_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(object_type, code)
);

CREATE INDEX idx_attr_def_object_type ON org_attribute_definition(object_type);

-- Attribute Values
CREATE TABLE org_attribute_value (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_type TEXT NOT NULL CHECK (object_type IN ('OrganizationUnit', 'Position', 'Employee')),
    object_id UUID NOT NULL,
    attribute_definition_id UUID NOT NULL REFERENCES org_attribute_definition(id),
    value TEXT NOT NULL, -- Stringified, interpreted by data_type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(object_type, object_id, attribute_definition_id)
);

CREATE INDEX idx_attr_value_object ON org_attribute_value(object_type, object_id);
CREATE INDEX idx_attr_value_def ON org_attribute_value(attribute_definition_id);
```

### **5. M&A and Scenario Tables**

```sql
-- Org Unit Mappings (for M&A scenarios)
CREATE TABLE org_unit_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_org_unit_id UUID NOT NULL REFERENCES org_unit(id),
    target_org_unit_id UUID NOT NULL REFERENCES org_unit(id),
    mapping_type TEXT NOT NULL CHECK (mapping_type IN ('Merge', 'Split', 'Move')),
    scenario_id TEXT NOT NULL,
    effective_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID
);

CREATE INDEX idx_mapping_source ON org_unit_mapping(source_org_unit_id);
CREATE INDEX idx_mapping_target ON org_unit_mapping(target_org_unit_id);
CREATE INDEX idx_mapping_scenario ON org_unit_mapping(scenario_id);

-- Scenarios
CREATE TABLE scenario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    tree_id TEXT NOT NULL UNIQUE,
    base_scenario_id UUID REFERENCES scenario(id), -- If this is a variant
    status TEXT NOT NULL CHECK (status IN ('Draft', 'Active', 'Archived')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID
);

CREATE INDEX idx_scenario_status ON scenario(status);
```

---

## 🎯 Skills and Capability Tables

### **6. Skills Schema**

```sql
-- Skills Master
CREATE TABLE skill (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL, -- e.g., 'Technical', 'Soft', 'Domain', 'AI/ML'
    sub_category TEXT,
    description TEXT,
    is_core_skill BOOLEAN DEFAULT FALSE, -- Core vs specialized
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skill_category ON skill(category);
CREATE INDEX idx_skill_code ON skill(code);

-- Employee Skills (with proficiency levels)
CREATE TABLE employee_skill (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
    proficiency_level INTEGER NOT NULL CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    -- 1 = Beginner, 2 = Intermediate, 3 = Advanced, 4 = Expert, 5 = Master
    years_of_experience DECIMAL(4,1),
    last_validated_at DATE,
    validated_by UUID, -- Who validated this skill
    validation_method TEXT, -- 'Self-Assessment', 'Manager Review', 'Certification', 'Project Evidence', 'AI Inference'
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1), -- For AI-inferred skills
    is_primary_skill BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, skill_id)
);

CREATE INDEX idx_employee_skill_employee ON employee_skill(employee_id);
CREATE INDEX idx_employee_skill_skill ON employee_skill(skill_id);
CREATE INDEX idx_employee_skill_level ON employee_skill(proficiency_level);
CREATE INDEX idx_employee_skill_validation ON employee_skill(validation_method);

-- Job Skill Requirements
CREATE TABLE job_skill (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES job(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
    required_level INTEGER NOT NULL CHECK (required_level >= 1 AND required_level <= 5),
    is_mandatory BOOLEAN DEFAULT TRUE,
    weight DECIMAL(3,2) CHECK (weight >= 0 AND weight <= 1), -- For matching algorithms
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, skill_id)
);

CREATE INDEX idx_job_skill_job ON job_skill(job_id);
CREATE INDEX idx_job_skill_skill ON job_skill(skill_id);
CREATE INDEX idx_job_skill_required ON job_skill(required_level);

-- Position Skill Requirements (can override job defaults)
CREATE TABLE position_skill (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID NOT NULL REFERENCES position(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
    required_level INTEGER NOT NULL CHECK (required_level >= 1 AND required_level <= 5),
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(position_id, skill_id)
);

CREATE INDEX idx_position_skill_position ON position_skill(position_id);
CREATE INDEX idx_position_skill_skill ON position_skill(skill_id);

-- Skill Clusters (for AI-based team formation)
CREATE TABLE skill_cluster (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    skill_ids UUID[] NOT NULL, -- Array of skill IDs that form this cluster
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skill_cluster_skills ON skill_cluster USING GIN(skill_ids);
```

---

## 🤖 AI and Recommendation Tables

### **7. AI Recommendations**

```sql
-- AI Recommendations
CREATE TABLE ai_recommendation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_type TEXT NOT NULL CHECK (recommendation_type IN (
        'TeamFormation', 
        'OrgDesign', 
        'SkillGap', 
        'InternalMobility', 
        'Restructure', 
        'SpanOptimization',
        'WorkforcePlanning'
    )),
    target_object_type TEXT NOT NULL CHECK (target_object_type IN ('OrgUnit', 'Position', 'Employee', 'Project', 'Scenario')),
    target_object_id UUID NOT NULL,
    recommendation_text TEXT NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    reasoning JSONB, -- Structured reasoning data
    suggested_actions JSONB, -- Array of suggested actions
    model_version TEXT, -- Which AI model generated this
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('Active', 'Accepted', 'Rejected', 'Expired')) DEFAULT 'Active'
);

CREATE INDEX idx_ai_recommendation_type ON ai_recommendation(recommendation_type);
CREATE INDEX idx_ai_recommendation_target ON ai_recommendation(target_object_type, target_object_id);
CREATE INDEX idx_ai_recommendation_status ON ai_recommendation(status);

-- Team Formation Suggestions
CREATE TABLE team_formation_suggestion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID, -- If for a specific project
    project_name TEXT,
    required_skills JSONB NOT NULL, -- Array of {skill_id, required_level}
    suggested_employees UUID[] NOT NULL, -- Array of employee IDs
    skill_coverage_score DECIMAL(3,2), -- How well the team covers required skills
    availability_score DECIMAL(3,2), -- Team availability
    cost_estimate DECIMAL(12,2),
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK (status IN ('Draft', 'Proposed', 'Accepted', 'Rejected'))
);

CREATE INDEX idx_team_formation_project ON team_formation_suggestion(project_id);
CREATE INDEX idx_team_formation_status ON team_formation_suggestion(status);

-- Org Design Suggestions
CREATE TABLE org_design_suggestion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES scenario(id),
    org_unit_id UUID REFERENCES org_unit(id),
    suggestion_type TEXT NOT NULL CHECK (suggestion_type IN (
        'FlattenStructure',
        'MergeUnits',
        'SplitUnit',
        'AddLayer',
        'RemoveLayer',
        'ReorganizeReporting'
    )),
    current_state JSONB NOT NULL, -- Snapshot of current org structure
    proposed_state JSONB NOT NULL, -- Proposed org structure
    expected_benefits JSONB, -- Expected improvements
    risks JSONB, -- Identified risks
    impact_analysis JSONB, -- Headcount, cost, span of control impacts
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK (status IN ('Draft', 'Proposed', 'Accepted', 'Rejected'))
);

CREATE INDEX idx_org_design_scenario ON org_design_suggestion(scenario_id);
CREATE INDEX idx_org_design_org_unit ON org_design_suggestion(org_unit_id);
```

---

## 📈 Analytics and Metrics Tables

### **8. Calculated Metrics**

```sql
-- Org Metrics (pre-calculated for performance)
CREATE TABLE org_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_unit_id UUID NOT NULL REFERENCES org_unit(id),
    metric_date DATE NOT NULL,
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
    total_compensation DECIMAL(12,2), -- If available from HRIS
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_unit_id, metric_date)
);

CREATE INDEX idx_org_metrics_org_unit ON org_metrics(org_unit_id);
CREATE INDEX idx_org_metrics_date ON org_metrics(metric_date);

-- Skill Gap Analysis
CREATE TABLE skill_gap_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_unit_id UUID REFERENCES org_unit(id),
    position_id UUID REFERENCES position(id),
    skill_id UUID NOT NULL REFERENCES skill(id),
    required_level INTEGER NOT NULL,
    current_level INTEGER, -- Average current level across employees
    gap_size INTEGER NOT NULL, -- required_level - current_level
    employees_affected INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_unit_id, position_id, skill_id)
);

CREATE INDEX idx_skill_gap_org_unit ON skill_gap_analysis(org_unit_id);
CREATE INDEX idx_skill_gap_position ON skill_gap_analysis(position_id);
CREATE INDEX idx_skill_gap_skill ON skill_gap_analysis(skill_id);
```

---

## 🔄 Change Management Tables

### **9. Change Packages**

```sql
-- Change Packages (for sending approved changes back to HRIS)
CREATE TABLE change_package (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES scenario(id),
    change_type TEXT NOT NULL CHECK (change_type IN (
        'PositionMove',
        'PositionCreate',
        'PositionFreeze',
        'OrgUnitMove',
        'OrgUnitMerge',
        'OrgUnitSplit',
        'ReportingLineChange',
        'BulkPositionCreate'
    )),
    change_data JSONB NOT NULL, -- Structured change data
    status TEXT NOT NULL CHECK (status IN ('Draft', 'PendingApproval', 'Approved', 'SentToHRIS', 'Applied', 'Rejected')) DEFAULT 'Draft',
    requested_by UUID NOT NULL,
    approved_by UUID,
    approved_at TIMESTAMP,
    sent_to_hris_at TIMESTAMP,
    hris_response JSONB, -- Response from HRIS
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_change_package_scenario ON change_package(scenario_id);
CREATE INDEX idx_change_package_status ON change_package(status);
CREATE INDEX idx_change_package_type ON change_package(change_type);
```

---

## 🔍 Views for Common Queries

```sql
-- View: Active Employees with Positions
CREATE VIEW v_active_employees AS
SELECT 
    e.id,
    e.employee_number,
    e.first_name,
    e.last_name,
    e.preferred_name,
    e.email,
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
CREATE VIEW v_vacant_positions AS
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
CREATE VIEW v_employee_skills_summary AS
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
  AND es.proficiency_level >= 3; -- Only show intermediate and above
```

---

## 📝 Notes

1. **UUIDs**: All primary keys use UUIDs for distributed system compatibility
2. **Effective Dating**: Core tables support time-travel queries via `effective_start_date` and `effective_end_date`
3. **Soft Deletes**: Use `status` fields rather than hard deletes for audit trails
4. **Indexes**: Strategic indexes on foreign keys and frequently queried fields
5. **Constraints**: CHECK constraints ensure data integrity
6. **JSONB**: Used for flexible, queryable structured data (PostgreSQL-specific)

---

## 🔄 Migration Strategy

1. Create core tables (org_unit, position, job, employee, assignment)
2. Create supporting tables (location, cost_center, legal_entity)
3. Create skills tables
4. Create AI/recommendation tables
5. Create analytics tables
6. Create views
7. Populate with initial data from HRIS
