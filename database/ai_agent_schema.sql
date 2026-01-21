-- ============================================
-- AI AGENT SCHEMA
-- Tables for AI agent integration into org structure
-- ============================================

-- AI Agents (Core entity for AI agents in the organization)
CREATE TABLE IF NOT EXISTS ai_agent (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,                -- "Eve", "Tars", "Sonny" (personality names)
    agent_type TEXT NOT NULL,                 -- "Cross-Functional Integrator", "Strategy Advisor", "Market Analyst"
    description TEXT,
    avatar_url TEXT,

    -- AI Configuration
    model_provider TEXT NOT NULL CHECK (model_provider IN ('OpenAI', 'Anthropic', 'Local', 'MCP')),
    model_id TEXT NOT NULL,                  -- "gpt-4-turbo", "claude-3-opus", etc.
    model_config JSONB,                      -- Model-specific configuration

    -- Capabilities
    capabilities JSONB,                       -- Array of capability strings
    skills JSONB,                            -- Skills the AI agent has
    functions JSONB,                         -- Functions the AI can perform

    -- Metadata
    status TEXT NOT NULL CHECK (status IN ('Active', 'Inactive', 'Training', 'Deprecated')) DEFAULT 'Active',
    performance_score DECIMAL(3,2) CHECK (performance_score >= 0 AND performance_score <= 1),
    cost_per_hour DECIMAL(10,2),

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id),
    updated_by UUID REFERENCES app_user(id)
);

CREATE INDEX IF NOT EXISTS idx_ai_agent_status ON ai_agent(status);
CREATE INDEX IF NOT EXISTS idx_ai_agent_type ON ai_agent(agent_type);

COMMENT ON TABLE ai_agent IS 'AI agents that can be assigned to positions in the org chart';
COMMENT ON COLUMN ai_agent.agent_name IS 'Personality name like Eve, Tars, Sonny';
COMMENT ON COLUMN ai_agent.agent_type IS 'Functional role type like Cross-Functional Integrator';

-- AI Agent Position Assignments
CREATE TABLE IF NOT EXISTS ai_agent_position (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ai_agent_id UUID NOT NULL REFERENCES ai_agent(id) ON DELETE CASCADE,
    position_id UUID NOT NULL REFERENCES position(id) ON DELETE CASCADE,

    -- Assignment Details
    assignment_type TEXT NOT NULL CHECK (assignment_type IN ('Full', 'Assisted', 'Advisory', 'Augmented')),
    fte_allocation DECIMAL(3,2) NOT NULL CHECK (fte_allocation >= 0 AND fte_allocation <= 1) DEFAULT 1.0,

    -- Time Period
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,

    -- Performance
    tasks_completed INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2),

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES app_user(id),

    UNIQUE(ai_agent_id, position_id, start_date)
);

CREATE INDEX IF NOT EXISTS idx_ai_agent_position_agent ON ai_agent_position(ai_agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_agent_position_position ON ai_agent_position(position_id);
CREATE INDEX IF NOT EXISTS idx_ai_agent_position_type ON ai_agent_position(assignment_type);

COMMENT ON TABLE ai_agent_position IS 'Assignment of AI agents to positions';
COMMENT ON COLUMN ai_agent_position.assignment_type IS 'Full=100% AI, Assisted=AI helps human, Advisory=AI advises, Augmented=AI augments human';

-- AI Agent Interactions Log
CREATE TABLE IF NOT EXISTS ai_agent_interaction (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ai_agent_id UUID NOT NULL REFERENCES ai_agent(id) ON DELETE CASCADE,
    interaction_type TEXT NOT NULL CHECK (interaction_type IN ('Task', 'Query', 'Recommendation', 'Analysis', 'Decision')),
    input_data JSONB,
    output_data JSONB,

    -- Performance Metrics
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,4),
    confidence_score DECIMAL(3,2),

    -- User Feedback
    user_feedback TEXT CHECK (user_feedback IN ('Helpful', 'NotHelpful', 'Incorrect', 'Excellent')),
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),

    -- Context
    context_org_unit_id UUID REFERENCES org_unit(id),
    context_position_id UUID REFERENCES position(id),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES app_user(id)
);

CREATE INDEX IF NOT EXISTS idx_ai_interaction_agent ON ai_agent_interaction(ai_agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_interaction_type ON ai_agent_interaction(interaction_type);
CREATE INDEX IF NOT EXISTS idx_ai_interaction_created ON ai_agent_interaction(created_at);

COMMENT ON TABLE ai_agent_interaction IS 'Log of all AI agent interactions for performance tracking';

-- Alter position table to support AI integration
ALTER TABLE position
ADD COLUMN IF NOT EXISTS ai_usage_type TEXT
    CHECK (ai_usage_type IN ('None', 'Assisted', 'Augmented', 'FullAgent'))
    DEFAULT 'None';

ALTER TABLE position
ADD COLUMN IF NOT EXISTS assigned_ai_agent_id UUID REFERENCES ai_agent(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_position_ai_usage ON position(ai_usage_type);
CREATE INDEX IF NOT EXISTS idx_position_ai_agent ON position(assigned_ai_agent_id);

COMMENT ON COLUMN position.ai_usage_type IS 'How AI is used in this position: None, Assisted (AI helps human), Augmented (AI enhances human), FullAgent (100% AI)';

-- View: Active AI Agents with Assignments
CREATE OR REPLACE VIEW v_ai_agents_active AS
SELECT
    aa.id,
    aa.agent_name,
    aa.agent_type,
    aa.model_provider,
    aa.model_id,
    aa.status,
    aap.position_id,
    p.position_title,
    p.org_unit_id,
    o.name as org_unit_name,
    aap.assignment_type,
    aap.fte_allocation,
    aap.start_date,
    aap.end_date
FROM ai_agent aa
LEFT JOIN ai_agent_position aap ON aa.id = aap.ai_agent_id AND aap.end_date IS NULL
LEFT JOIN position p ON aap.position_id = p.id
LEFT JOIN org_unit o ON p.org_unit_id = o.id
WHERE aa.status = 'Active';

COMMENT ON VIEW v_ai_agents_active IS 'Active AI agents with their current position assignments';

-- View: AI Adoption Metrics
CREATE OR REPLACE VIEW v_ai_adoption_metrics AS
SELECT
    COUNT(DISTINCT CASE WHEN p.ai_usage_type = 'FullAgent' THEN p.id END) as full_agent_positions,
    COUNT(DISTINCT CASE WHEN p.ai_usage_type = 'Augmented' THEN p.id END) as augmented_positions,
    COUNT(DISTINCT CASE WHEN p.ai_usage_type = 'Assisted' THEN p.id END) as assisted_positions,
    COUNT(DISTINCT CASE WHEN p.ai_usage_type = 'None' THEN p.id END) as human_only_positions,
    COUNT(DISTINCT p.id) as total_positions,
    COUNT(DISTINCT aa.id) as active_ai_agents,
    SUM(CASE WHEN p.ai_usage_type IN ('FullAgent', 'Augmented', 'Assisted') THEN p.fte ELSE 0 END) as ai_fte_total,
    SUM(p.fte) as total_fte
FROM position p
LEFT JOIN ai_agent aa ON p.assigned_ai_agent_id = aa.id AND aa.status = 'Active'
WHERE p.status = 'Active';

COMMENT ON VIEW v_ai_adoption_metrics IS 'Overall AI adoption metrics across the organization';

-- Function: Calculate AI adoption rate
CREATE OR REPLACE FUNCTION calculate_ai_adoption_rate(p_org_unit_id UUID DEFAULT NULL)
RETURNS TABLE (
    org_unit_id UUID,
    org_unit_name TEXT,
    total_positions BIGINT,
    ai_positions BIGINT,
    adoption_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.id as org_unit_id,
        o.name as org_unit_name,
        COUNT(p.id)::BIGINT as total_positions,
        COUNT(CASE WHEN p.ai_usage_type != 'None' THEN 1 END)::BIGINT as ai_positions,
        ROUND(
            COUNT(CASE WHEN p.ai_usage_type != 'None' THEN 1 END)::NUMERIC /
            NULLIF(COUNT(p.id)::NUMERIC, 0) * 100,
            2
        ) as adoption_rate
    FROM org_unit o
    LEFT JOIN position p ON o.id = p.org_unit_id AND p.status = 'Active'
    WHERE (p_org_unit_id IS NULL OR o.id = p_org_unit_id)
      AND o.status = 'Active'
    GROUP BY o.id, o.name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_ai_adoption_rate IS 'Calculate AI adoption rate by org unit';

-- Sample Data: AI Agent Types
INSERT INTO ai_agent (agent_name, agent_type, description, model_provider, model_id, capabilities, created_by)
VALUES
    ('Eve', 'Cross-Functional Integrator', 'Continuously monitors and analyzes information flows across all departments (finance, marketing, sales, operations, customer support) to identify knowledge gaps, redundancies, and collaboration opportunities.', 'OpenAI', 'gpt-4-turbo', '["knowledge_bridging", "information_analysis", "collaboration_optimization"]'::jsonb, '00000000-0000-0000-0000-000000000000'),
    ('Tars', 'Chief Strategy Advisor', 'Provides high-level strategic recommendations based on market analysis, competitive intelligence, and organizational data.', 'Anthropic', 'claude-3-opus', '["strategic_planning", "market_analysis", "competitive_intelligence"]'::jsonb, '00000000-0000-0000-0000-000000000000'),
    ('Sonny', 'Market Analyst', 'Analyzes market trends, customer behavior, and competitive landscape to provide data-driven insights.', 'OpenAI', 'gpt-4-turbo', '["market_research", "trend_analysis", "customer_insights"]'::jsonb, '00000000-0000-0000-0000-000000000000')
ON CONFLICT DO NOTHING;

-- ============================================
-- END OF AI AGENT SCHEMA
-- ============================================
