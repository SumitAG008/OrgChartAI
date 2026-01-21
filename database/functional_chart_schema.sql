-- Functional Chart Tables
-- Run this after main schema.sql

-- Function Categories (e.g., "People and Culture", "Governance")
CREATE TABLE IF NOT EXISTS function_category (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,  -- Emoji or icon identifier
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_function_category_display_order ON function_category(display_order);
CREATE INDEX IF NOT EXISTS idx_function_category_active ON function_category(is_active);

-- Functions (e.g., "Compensation", "Recruitment")
CREATE TABLE IF NOT EXISTS function (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES function_category(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,  -- Emoji or icon identifier
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    version INTEGER NOT NULL DEFAULT 1,
    UNIQUE(category_id, name)
);

CREATE INDEX IF NOT EXISTS idx_function_category_id ON function(category_id);
CREATE INDEX IF NOT EXISTS idx_function_display_order ON function(display_order);
CREATE INDEX IF NOT EXISTS idx_function_active ON function(is_active);

-- Accountabilities (specific responsibilities within a function)
CREATE TABLE IF NOT EXISTS accountability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    function_id UUID NOT NULL REFERENCES function(id) ON DELETE CASCADE,
    accountability_code TEXT,  -- Optional accountability ID
    objective TEXT NOT NULL,  -- The accountability description/objective
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_accountability_function_id ON accountability(function_id);
CREATE INDEX IF NOT EXISTS idx_accountability_display_order ON accountability(display_order);
CREATE INDEX IF NOT EXISTS idx_accountability_active ON accountability(is_active);

-- Accountability Assignments (links accountabilities to positions/employees)
CREATE TABLE IF NOT EXISTS accountability_assignment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    accountability_id UUID NOT NULL REFERENCES accountability(id) ON DELETE CASCADE,
    position_id UUID REFERENCES position(id) ON DELETE SET NULL,
    employee_id UUID REFERENCES employee(id) ON DELETE SET NULL,
    assignment_type TEXT NOT NULL CHECK (assignment_type IN ('Primary', 'Secondary', 'Shared')),
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Completed', 'Cancelled')),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    version INTEGER NOT NULL DEFAULT 1,
    CHECK (position_id IS NOT NULL OR employee_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_accountability_assignment_accountability ON accountability_assignment(accountability_id);
CREATE INDEX IF NOT EXISTS idx_accountability_assignment_position ON accountability_assignment(position_id);
CREATE INDEX IF NOT EXISTS idx_accountability_assignment_employee ON accountability_assignment(employee_id);
CREATE INDEX IF NOT EXISTS idx_accountability_assignment_status ON accountability_assignment(status);

-- Add triggers for updated_at
CREATE TRIGGER update_function_category_updated_at
    BEFORE UPDATE ON function_category
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_function_updated_at
    BEFORE UPDATE ON function
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accountability_updated_at
    BEFORE UPDATE ON accountability
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accountability_assignment_updated_at
    BEFORE UPDATE ON accountability_assignment
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO function_category (name, description, icon, display_order, created_by) VALUES
('People and Culture', 'Human resources and organizational culture functions', '👥', 1, '00000000-0000-0000-0000-000000000000'),
('Governance', 'Corporate governance and compliance', '⚖️', 2, '00000000-0000-0000-0000-000000000000'),
('Brand and Communications', 'Brand management and communications', '📣', 3, '00000000-0000-0000-0000-000000000000'),
('Account Management', 'Client account management and relationships', '🤝', 4, '00000000-0000-0000-0000-000000000000'),
('Commercial, Compliance and Legal', 'Legal, compliance, and commercial functions', '📋', 5, '00000000-0000-0000-0000-000000000000')
ON CONFLICT (name) DO NOTHING;

-- Insert sample functions for "People and Culture"
INSERT INTO function (category_id, name, icon, display_order, created_by)
SELECT 
    fc.id,
    func_data.name,
    func_data.icon,
    func_data.display_order,
    '00000000-0000-0000-0000-000000000000'
FROM function_category fc
CROSS JOIN (VALUES
    ('Compensation', '💰', 1),
    ('Corporate Social Responsibility', '🌍', 2),
    ('Culture Development', '🎨', 3),
    ('Employee Engagement', '😊', 4),
    ('Function Architecture', '🏗️', 5),
    ('Human Resource Compliance', '📋', 6),
    ('Human Resource Management', '👥', 7),
    ('Internal Communications', '📢', 8),
    ('Leadership Development', '🎯', 9),
    ('Occupational Health and Safety', '🏥', 10),
    ('Onboarding/Offboarding', '🚪', 11),
    ('People and Culture Strategy', '📊', 12),
    ('Performance Management', '📈', 13),
    ('Recruitment', '🔍', 14),
    ('Talent Development', '⭐', 15),
    ('Workforce Planning', '📅', 16)
) AS func_data(name, icon, display_order)
WHERE fc.name = 'People and Culture'
ON CONFLICT (category_id, name) DO NOTHING;

-- Insert sample accountabilities for Compensation function
INSERT INTO accountability (function_id, objective, created_by)
SELECT 
    f.id,
    'Operate remuneration, incentives and benefit programs to attract, compensate and retain quality employees',
    '00000000-0000-0000-0000-000000000000'
FROM function f
WHERE f.name = 'Compensation'
ON CONFLICT DO NOTHING;
