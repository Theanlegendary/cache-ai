-- AI Cache Database Schema

-- Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    repository VARCHAR(255),
    branch VARCHAR(255) DEFAULT 'main',
    agent_name VARCHAR(255),
    total_interactions INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    duration_seconds INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Interactions Table
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(50),
    user_input TEXT,
    ai_response TEXT,
    cache_hit BOOLEAN DEFAULT FALSE,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    model VARCHAR(255),
    success BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_type (type)
);

-- Cache Entries Table
CREATE TABLE IF NOT EXISTS cache_entries (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_hash VARCHAR(64) NOT NULL UNIQUE,
    pattern TEXT NOT NULL,
    cached_response TEXT NOT NULL,
    hit_count INTEGER DEFAULT 0,
    miss_count INTEGER DEFAULT 0,
    last_hit TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ttl INTEGER DEFAULT 2592000,
    expires_at TIMESTAMP,
    enabled BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    INDEX idx_pattern_hash (pattern_hash),
    INDEX idx_expires_at (expires_at),
    INDEX idx_created_at (created_at)
);

-- Cache Statistics Table
CREATE TABLE IF NOT EXISTS cache_statistics (
    stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_id UUID,
    hit_count INTEGER DEFAULT 0,
    miss_count INTEGER DEFAULT 0,
    total_requests INTEGER DEFAULT 0,
    hit_rate DECIMAL(5,4),
    average_response_time_ms DECIMAL(10,2),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cache_id) REFERENCES cache_entries(cache_id) ON DELETE CASCADE,
    INDEX idx_cache_id (cache_id),
    INDEX idx_recorded_at (recorded_at)
);

-- AI Performance Metrics Table
CREATE TABLE IF NOT EXISTS performance_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID,
    accuracy DECIMAL(5,4),
    token_efficiency DECIMAL(10,2),
    response_quality INTEGER,
    user_satisfaction INTEGER,
    notes TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_recorded_at (recorded_at)
);

-- Usage Patterns Table
CREATE TABLE IF NOT EXISTS usage_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    pattern_type VARCHAR(100),
    pattern_description TEXT,
    frequency INTEGER DEFAULT 1,
    average_tokens INTEGER,
    average_response_time INTEGER,
    first_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_pattern_type (pattern_type)
);

-- Error Logs Table
CREATE TABLE IF NOT EXISTS error_logs (
    error_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID,
    interaction_id UUID,
    error_type VARCHAR(100),
    error_message TEXT,
    stack_trace TEXT,
    severity VARCHAR(50),
    resolution TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (interaction_id) REFERENCES interactions(interaction_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_severity (severity),
    INDEX idx_logged_at (logged_at)
);

-- Views for Analytics

-- Session Summary View
CREATE OR REPLACE VIEW v_session_summary AS
SELECT 
    s.session_id,
    s.user_id,
    s.start_time,
    s.end_time,
    s.duration_seconds,
    COUNT(i.interaction_id) as total_interactions,
    COALESCE(SUM(i.tokens_used), 0) as total_tokens,
    COALESCE(SUM(CASE WHEN i.cache_hit THEN 1 ELSE 0 END), 0) as cache_hits,
    COALESCE(AVG(i.response_time_ms), 0) as avg_response_time
FROM sessions s
LEFT JOIN interactions i ON s.session_id = i.session_id
GROUP BY s.session_id, s.user_id, s.start_time, s.end_time, s.duration_seconds;

-- Cache Performance View
CREATE OR REPLACE VIEW v_cache_performance AS
SELECT 
    cache_id,
    pattern_hash,
    hit_count,
    miss_count,
    hit_count + miss_count as total_requests,
    CASE 
        WHEN (hit_count + miss_count) > 0 
        THEN ROUND(CAST(hit_count AS FLOAT) / (hit_count + miss_count), 4)
        ELSE 0 
    END as hit_rate,
    created_at,
    last_hit
FROM cache_entries;

-- User Activity View
CREATE OR REPLACE VIEW v_user_activity AS
SELECT 
    s.user_id,
    COUNT(DISTINCT s.session_id) as total_sessions,
    COALESCE(SUM(COUNT(i.interaction_id)) OVER (PARTITION BY s.user_id), 0) as total_interactions,
    MIN(s.start_time) as first_session,
    MAX(s.end_time) as last_session
FROM sessions s
LEFT JOIN interactions i ON s.session_id = i.session_id
GROUP BY s.user_id;
