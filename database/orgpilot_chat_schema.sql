-- ============================================
-- ORGPILOT AI CHAT SCHEMA
-- Tables for conversational AI interface
-- ============================================

-- OrgPilot Chat Sessions
CREATE TABLE IF NOT EXISTS orgpilot_chat_session (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,

    -- Context
    tree_id TEXT,                             -- Org structure being discussed
    org_unit_id UUID REFERENCES org_unit(id), -- Focused org unit
    scenario_id UUID REFERENCES scenario(id), -- Focused scenario

    -- Session Details
    session_name TEXT,
    session_mode TEXT CHECK (session_mode IN ('Agent', 'Advisor', 'Hybrid')) DEFAULT 'Advisor',

    -- Timestamps
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
    ended_at TIMESTAMP,

    -- Status
    status TEXT NOT NULL CHECK (status IN ('Active', 'Paused', 'Archived', 'Deleted')) DEFAULT 'Active',

    -- Metadata
    total_messages INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,4) DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orgpilot_session_user ON orgpilot_chat_session(user_id);
CREATE INDEX IF NOT EXISTS idx_orgpilot_session_tree ON orgpilot_chat_session(tree_id);
CREATE INDEX IF NOT EXISTS idx_orgpilot_session_status ON orgpilot_chat_session(status);
CREATE INDEX IF NOT EXISTS idx_orgpilot_session_started ON orgpilot_chat_session(started_at);

COMMENT ON TABLE orgpilot_chat_session IS 'OrgPilot AI chat sessions for conversational org design assistance';
COMMENT ON COLUMN orgpilot_chat_session.session_mode IS 'Agent=proactive AI, Advisor=reactive AI, Hybrid=both';

-- OrgPilot Messages
CREATE TABLE IF NOT EXISTS orgpilot_message (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES orgpilot_chat_session(id) ON DELETE CASCADE,

    -- Message Details
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,

    -- Context (what org data was referenced)
    context_type TEXT CHECK (context_type IN ('OrgChart', 'Metrics', 'Forecast', 'Recommendation', 'Analysis')),
    context_data JSONB,                       -- Referenced org units, positions, employees

    -- AI Model Details
    model_used TEXT,                          -- "gpt-4-turbo", "claude-3-opus"
    model_provider TEXT,                      -- "OpenAI", "Anthropic"
    system_prompt TEXT,                       -- System prompt used
    temperature DECIMAL(3,2),
    max_tokens INTEGER,

    -- Performance
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    cost_usd DECIMAL(10,4),

    -- User Feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,
    is_helpful BOOLEAN,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orgpilot_message_session ON orgpilot_message(session_id);
CREATE INDEX IF NOT EXISTS idx_orgpilot_message_role ON orgpilot_message(role);
CREATE INDEX IF NOT EXISTS idx_orgpilot_message_created ON orgpilot_message(created_at);

COMMENT ON TABLE orgpilot_message IS 'Individual messages in OrgPilot chat conversations';

-- OrgPilot Recommendations
CREATE TABLE IF NOT EXISTS orgpilot_recommendation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES orgpilot_chat_session(id) ON DELETE CASCADE,
    message_id UUID REFERENCES orgpilot_message(id) ON DELETE SET NULL,

    -- Recommendation Details
    recommendation_type TEXT NOT NULL CHECK (recommendation_type IN (
        'OrgStructure', 'TeamFormation', 'RoleAssignment', 'SkillGap',
        'SpanOfControl', 'CostOptimization', 'ProcessImprovement'
    )),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    reasoning TEXT,

    -- Impact
    expected_impact JSONB,                    -- {"headcount_change": -5, "cost_savings": 100000}
    confidence_score DECIMAL(3,2),

    -- Targets
    target_org_unit_id UUID REFERENCES org_unit(id),
    target_position_id UUID REFERENCES position(id),
    affected_entities JSONB,                  -- Array of affected entities

    -- Actions
    suggested_actions JSONB,                  -- Array of actionable steps
    implementation_complexity TEXT CHECK (implementation_complexity IN ('Low', 'Medium', 'High')),

    -- Status
    status TEXT NOT NULL CHECK (status IN ('Pending', 'Accepted', 'Rejected', 'Implemented', 'Expired')) DEFAULT 'Pending',
    accepted_at TIMESTAMP,
    accepted_by UUID REFERENCES app_user(id),
    rejection_reason TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orgpilot_rec_session ON orgpilot_recommendation(session_id);
CREATE INDEX IF NOT EXISTS idx_orgpilot_rec_type ON orgpilot_recommendation(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_orgpilot_rec_status ON orgpilot_recommendation(status);

COMMENT ON TABLE orgpilot_recommendation IS 'AI recommendations generated during OrgPilot chat sessions';

-- OrgPilot Analysis Results
CREATE TABLE IF NOT EXISTS orgpilot_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES orgpilot_chat_session(id) ON DELETE CASCADE,
    message_id UUID REFERENCES orgpilot_message(id) ON DELETE SET NULL,

    -- Analysis Details
    analysis_type TEXT NOT NULL CHECK (analysis_type IN (
        'OrgHealth', 'SpanOfControl', 'HierarchyDepth', 'SkillGaps',
        'VacancyAnalysis', 'CostAnalysis', 'EfficiencyAnalysis'
    )),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,

    -- Results
    metrics JSONB NOT NULL,                   -- Key metrics from analysis
    insights JSONB,                           -- Key insights discovered
    visualizations JSONB,                     -- Data for charts/graphs

    -- Scope
    org_unit_id UUID REFERENCES org_unit(id),
    tree_id TEXT,
    filters JSONB,                            -- Filters used in analysis

    -- Model
    model_used TEXT,
    confidence_score DECIMAL(3,2),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES app_user(id)
);

CREATE INDEX IF NOT EXISTS idx_orgpilot_analysis_session ON orgpilot_analysis(session_id);
CREATE INDEX IF NOT EXISTS idx_orgpilot_analysis_type ON orgpilot_analysis(analysis_type);
CREATE INDEX IF NOT EXISTS idx_orgpilot_analysis_created ON orgpilot_analysis(created_at);

COMMENT ON TABLE orgpilot_analysis IS 'AI-generated analysis results from OrgPilot';

-- View: Active Chat Sessions with Stats
CREATE OR REPLACE VIEW v_orgpilot_sessions_active AS
SELECT
    s.id,
    s.user_id,
    u.name as user_name,
    s.session_name,
    s.session_mode,
    s.started_at,
    s.last_message_at,
    s.total_messages,
    s.total_tokens_used,
    s.total_cost_usd,
    s.tree_id,
    s.org_unit_id,
    o.name as org_unit_name
FROM orgpilot_chat_session s
JOIN app_user u ON s.user_id = u.id
LEFT JOIN org_unit o ON s.org_unit_id = o.id
WHERE s.status = 'Active'
ORDER BY s.last_message_at DESC NULLS LAST;

COMMENT ON VIEW v_orgpilot_sessions_active IS 'Active OrgPilot chat sessions with summary stats';

-- View: Recent Recommendations
CREATE OR REPLACE VIEW v_orgpilot_recommendations_recent AS
SELECT
    r.id,
    r.session_id,
    s.user_id,
    r.recommendation_type,
    r.title,
    r.description,
    r.confidence_score,
    r.status,
    r.target_org_unit_id,
    o.name as target_org_unit_name,
    r.implementation_complexity,
    r.created_at,
    r.expires_at
FROM orgpilot_recommendation r
JOIN orgpilot_chat_session s ON r.session_id = s.id
LEFT JOIN org_unit o ON r.target_org_unit_id = o.id
WHERE r.status = 'Pending'
  AND (r.expires_at IS NULL OR r.expires_at > CURRENT_TIMESTAMP)
ORDER BY r.created_at DESC;

COMMENT ON VIEW v_orgpilot_recommendations_recent IS 'Recent pending OrgPilot recommendations';

-- Function: Get chat session context
CREATE OR REPLACE FUNCTION get_chat_session_context(p_session_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_context JSONB;
BEGIN
    SELECT jsonb_build_object(
        'session_id', s.id,
        'user_id', s.user_id,
        'tree_id', s.tree_id,
        'org_unit', CASE WHEN s.org_unit_id IS NOT NULL
            THEN jsonb_build_object(
                'id', o.id,
                'name', o.name,
                'code', o.code,
                'type', o.type
            )
            ELSE NULL
        END,
        'message_count', s.total_messages,
        'recent_messages', (
            SELECT jsonb_agg(jsonb_build_object(
                'role', m.role,
                'content', LEFT(m.content, 200),
                'created_at', m.created_at
            ) ORDER BY m.created_at DESC)
            FROM orgpilot_message m
            WHERE m.session_id = s.id
            LIMIT 5
        )
    ) INTO v_context
    FROM orgpilot_chat_session s
    LEFT JOIN org_unit o ON s.org_unit_id = o.id
    WHERE s.id = p_session_id;

    RETURN v_context;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_chat_session_context IS 'Get full context for a chat session including recent messages';

-- Function: Update session stats after message
CREATE OR REPLACE FUNCTION update_session_stats_after_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE orgpilot_chat_session
    SET
        total_messages = total_messages + 1,
        total_tokens_used = total_tokens_used + COALESCE(NEW.tokens_used, 0),
        total_cost_usd = total_cost_usd + COALESCE(NEW.cost_usd, 0),
        last_message_at = NEW.created_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_stats
AFTER INSERT ON orgpilot_message
FOR EACH ROW
EXECUTE FUNCTION update_session_stats_after_message();

COMMENT ON TRIGGER trigger_update_session_stats ON orgpilot_message IS 'Auto-update session stats when message is added';

-- ============================================
-- END OF ORGPILOT CHAT SCHEMA
-- ============================================
