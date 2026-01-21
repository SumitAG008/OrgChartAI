-- ============================================
-- FORECAST SCHEMA
-- Tables for workforce planning and forecasting
-- ============================================

-- Forecast Data (Time Series)
CREATE TABLE IF NOT EXISTS forecast_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Scope
    org_unit_id UUID REFERENCES org_unit(id) ON DELETE CASCADE,
    scenario_id UUID REFERENCES scenario(id) ON DELETE CASCADE,
    tree_id TEXT,

    -- Forecast Details
    forecast_type TEXT NOT NULL CHECK (forecast_type IN (
        'Headcount', 'PositionCount', 'FTE', 'Compensation',
        'HoursWorked', 'Vacancies', 'Attrition', 'Hiring'
    )),
    forecast_date DATE NOT NULL,              -- Start of month/quarter
    forecast_period TEXT NOT NULL CHECK (forecast_period IN ('Monthly', 'Quarterly', 'Yearly')),

    -- Value
    forecast_value DECIMAL(12,2) NOT NULL,
    baseline_value DECIMAL(12,2),            -- Actual current value for comparison
    variance DECIMAL(12,2),                  -- forecast_value - baseline_value

    -- Grouping/Segmentation
    group_by_field TEXT,                      -- "vacancy_status", "department", "employment_type", etc.
    group_by_value TEXT,                      -- "Vacant", "Engineering", "Permanent", etc.

    -- Confidence
    confidence_level DECIMAL(3,2) CHECK (confidence_level >= 0 AND confidence_level <= 1),
    forecast_method TEXT CHECK (forecast_method IN ('Manual', 'AI', 'Statistical', 'Hybrid')),

    -- Notes & Assumptions
    notes TEXT,
    assumptions JSONB,                        -- Array of assumption strings

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id),
    updated_by UUID REFERENCES app_user(id),

    UNIQUE(org_unit_id, scenario_id, forecast_type, forecast_date, group_by_field, group_by_value)
);

CREATE INDEX IF NOT EXISTS idx_forecast_org_unit ON forecast_data(org_unit_id);
CREATE INDEX IF NOT EXISTS idx_forecast_scenario ON forecast_data(scenario_id);
CREATE INDEX IF NOT EXISTS idx_forecast_date ON forecast_data(forecast_date);
CREATE INDEX IF NOT EXISTS idx_forecast_type ON forecast_data(forecast_type);
CREATE INDEX IF NOT EXISTS idx_forecast_period ON forecast_data(forecast_period);

COMMENT ON TABLE forecast_data IS 'Time series forecast data for workforce planning';
COMMENT ON COLUMN forecast_data.forecast_type IS 'Type of metric being forecasted';
COMMENT ON COLUMN forecast_data.group_by_field IS 'Optional field to segment the forecast (e.g., by department, status, type)';

-- Forecast Scenarios (Different forecast assumptions)
CREATE TABLE IF NOT EXISTS forecast_scenario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario_name TEXT NOT NULL,
    description TEXT,

    -- Scenario Type
    scenario_type TEXT CHECK (scenario_type IN ('Conservative', 'Baseline', 'Optimistic', 'Custom')),

    -- Assumptions
    growth_rate DECIMAL(5,2),                 -- Annual growth rate %
    attrition_rate DECIMAL(5,2),             -- Annual attrition rate %
    hiring_rate DECIMAL(5,2),                -- Monthly hiring rate %
    budget_constraint DECIMAL(12,2),          -- Budget cap
    assumptions JSONB,                        -- Detailed assumptions

    -- Time Period
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    -- Status
    status TEXT CHECK (status IN ('Draft', 'Active', 'Archived')) DEFAULT 'Draft',

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id)
);

CREATE INDEX IF NOT EXISTS idx_forecast_scenario_status ON forecast_scenario(status);

COMMENT ON TABLE forecast_scenario IS 'Different forecast scenarios with varying assumptions';

-- Forecast Templates (Reusable forecast configurations)
CREATE TABLE IF NOT EXISTS forecast_template (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name TEXT NOT NULL UNIQUE,
    description TEXT,

    -- Template Configuration
    forecast_types TEXT[],                    -- Array of forecast types to include
    time_period TEXT NOT NULL CHECK (time_period IN ('Monthly', 'Quarterly', 'Yearly')),
    duration_months INTEGER NOT NULL,         -- How many months to forecast

    -- Default Assumptions
    default_assumptions JSONB,

    -- Grouping
    group_by_fields TEXT[],                   -- Fields to segment by

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id)
);

COMMENT ON TABLE forecast_template IS 'Reusable forecast configurations for quick setup';

-- Forecast Accuracy Tracking
CREATE TABLE IF NOT EXISTS forecast_accuracy (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Forecast Reference
    forecast_data_id UUID NOT NULL REFERENCES forecast_data(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    forecast_value DECIMAL(12,2) NOT NULL,

    -- Actual Data
    actual_date DATE NOT NULL,
    actual_value DECIMAL(12,2) NOT NULL,

    -- Accuracy Metrics
    absolute_error DECIMAL(12,2),             -- |actual - forecast|
    percentage_error DECIMAL(5,2),            -- ((actual - forecast) / actual) * 100
    mape DECIMAL(5,2),                        -- Mean Absolute Percentage Error

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_forecast_accuracy_forecast ON forecast_accuracy(forecast_data_id);
CREATE INDEX IF NOT EXISTS idx_forecast_accuracy_date ON forecast_accuracy(actual_date);

COMMENT ON TABLE forecast_accuracy IS 'Tracks forecast accuracy by comparing predictions to actuals';

-- Allocation Status (Track if people are allocated to roles)
CREATE TABLE IF NOT EXISTS allocation_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,

    -- Allocation Details
    is_allocated BOOLEAN DEFAULT FALSE,
    primary_role_assigned BOOLEAN DEFAULT FALSE,
    role_count INTEGER DEFAULT 0,
    total_fte_allocation DECIMAL(3,2) DEFAULT 0,

    -- Role Distribution
    has_single_role BOOLEAN DEFAULT FALSE,
    has_multiple_roles BOOLEAN DEFAULT FALSE,

    -- Last Calculation
    last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(employee_id)
);

CREATE INDEX IF NOT EXISTS idx_allocation_status_employee ON allocation_status(employee_id);
CREATE INDEX IF NOT EXISTS idx_allocation_status_allocated ON allocation_status(is_allocated);

COMMENT ON TABLE allocation_status IS 'Tracks employee allocation status for people allocation metrics';

-- View: Monthly Forecast Summary
CREATE OR REPLACE VIEW v_forecast_monthly_summary AS
SELECT
    fd.org_unit_id,
    o.name as org_unit_name,
    fd.forecast_type,
    DATE_TRUNC('month', fd.forecast_date) as month,
    SUM(fd.forecast_value) as total_forecast,
    AVG(fd.confidence_level) as avg_confidence,
    COUNT(*) as forecast_count
FROM forecast_data fd
JOIN org_unit o ON fd.org_unit_id = o.id
WHERE fd.forecast_period = 'Monthly'
GROUP BY fd.org_unit_id, o.name, fd.forecast_type, DATE_TRUNC('month', fd.forecast_date)
ORDER BY month, forecast_type;

COMMENT ON VIEW v_forecast_monthly_summary IS 'Monthly summary of forecasts by org unit and type';

-- View: Forecast vs Actual Variance
CREATE OR REPLACE VIEW v_forecast_variance AS
SELECT
    fa.forecast_data_id,
    fd.org_unit_id,
    o.name as org_unit_name,
    fd.forecast_type,
    fa.forecast_date,
    fa.forecast_value,
    fa.actual_date,
    fa.actual_value,
    fa.absolute_error,
    fa.percentage_error,
    CASE
        WHEN fa.percentage_error <= 5 THEN 'Excellent'
        WHEN fa.percentage_error <= 10 THEN 'Good'
        WHEN fa.percentage_error <= 20 THEN 'Fair'
        ELSE 'Poor'
    END as accuracy_rating
FROM forecast_accuracy fa
JOIN forecast_data fd ON fa.forecast_data_id = fd.id
JOIN org_unit o ON fd.org_unit_id = o.id;

COMMENT ON VIEW v_forecast_variance IS 'Forecast vs actual comparison with accuracy rating';

-- Function: Generate Monthly Forecasts
CREATE OR REPLACE FUNCTION generate_monthly_forecasts(
    p_org_unit_id UUID,
    p_start_date DATE,
    p_months INTEGER,
    p_forecast_type TEXT,
    p_baseline_value DECIMAL,
    p_growth_rate DECIMAL DEFAULT 0,
    p_created_by UUID DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_current_date DATE;
    v_current_value DECIMAL;
    v_month INTEGER;
    v_inserted_count INTEGER := 0;
BEGIN
    v_current_value := p_baseline_value;

    FOR v_month IN 0..(p_months - 1) LOOP
        v_current_date := p_start_date + (v_month || ' months')::INTERVAL;

        -- Apply growth rate
        IF v_month > 0 THEN
            v_current_value := v_current_value * (1 + (p_growth_rate / 100 / 12));
        END IF;

        -- Insert forecast
        INSERT INTO forecast_data (
            org_unit_id,
            forecast_type,
            forecast_date,
            forecast_period,
            forecast_value,
            baseline_value,
            variance,
            forecast_method,
            created_by
        ) VALUES (
            p_org_unit_id,
            p_forecast_type,
            v_current_date,
            'Monthly',
            ROUND(v_current_value, 2),
            p_baseline_value,
            ROUND(v_current_value - p_baseline_value, 2),
            'Statistical',
            COALESCE(p_created_by, '00000000-0000-0000-0000-000000000000'::UUID)
        )
        ON CONFLICT (org_unit_id, scenario_id, forecast_type, forecast_date, group_by_field, group_by_value)
        DO UPDATE SET
            forecast_value = EXCLUDED.forecast_value,
            variance = EXCLUDED.variance,
            updated_at = CURRENT_TIMESTAMP;

        v_inserted_count := v_inserted_count + 1;
    END LOOP;

    RETURN v_inserted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_monthly_forecasts IS 'Generate monthly forecast data points with growth rate';

-- Function: Calculate Allocation Status
CREATE OR REPLACE FUNCTION calculate_allocation_status()
RETURNS INTEGER AS $$
DECLARE
    v_updated_count INTEGER := 0;
BEGIN
    -- Clear existing data
    TRUNCATE allocation_status;

    -- Calculate allocation for all active employees
    INSERT INTO allocation_status (
        employee_id,
        is_allocated,
        primary_role_assigned,
        role_count,
        total_fte_allocation,
        has_single_role,
        has_multiple_roles,
        last_calculated
    )
    SELECT
        e.id as employee_id,
        COUNT(a.id) > 0 as is_allocated,
        e.primary_position_id IS NOT NULL as primary_role_assigned,
        COUNT(a.id) as role_count,
        COALESCE(SUM(p.fte), 0) as total_fte_allocation,
        COUNT(a.id) = 1 as has_single_role,
        COUNT(a.id) > 1 as has_multiple_roles,
        CURRENT_TIMESTAMP
    FROM employee e
    LEFT JOIN assignment a ON e.id = a.employee_id AND a.status = 'Active'
    LEFT JOIN position p ON a.position_id = p.id
    WHERE e.status = 'Active'
    GROUP BY e.id;

    GET DIAGNOSTICS v_updated_count = ROW_COUNT;
    RETURN v_updated_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_allocation_status IS 'Calculate and update allocation status for all employees';

-- ============================================
-- END OF FORECAST SCHEMA
-- ============================================
