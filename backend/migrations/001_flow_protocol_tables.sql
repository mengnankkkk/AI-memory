-- ============================================================
-- 数据库迁移脚本: 双阶段"心流"交互协议
-- 版本: V2.0
-- 创建日期: 2025-01-XX
-- 描述: 添加关系状态管理、事件系统、情感日志等核心表
-- ============================================================

-- ============================================================
-- 1. 关系状态管理表
-- ============================================================

-- 1.1 伙伴关系状态表 (核心表)
CREATE TABLE IF NOT EXISTS companion_relationship_states (
    id SERIAL PRIMARY KEY,

    -- 关系标识
    user_id VARCHAR(255) NOT NULL,
    companion_id VARCHAR(255) NOT NULL,

    -- 核心状态指标
    affinity_score INTEGER NOT NULL DEFAULT 50 CHECK (affinity_score >= 0 AND affinity_score <= 1000),
    trust_score INTEGER NOT NULL DEFAULT 10 CHECK (trust_score >= 0 AND trust_score <= 100),
    tension_score INTEGER NOT NULL DEFAULT 0 CHECK (tension_score >= 0 AND tension_score <= 100),

    -- 关系阶段
    romance_stage VARCHAR(50) NOT NULL DEFAULT 'stranger',

    -- 情感状态
    current_mood VARCHAR(50) NOT NULL DEFAULT 'neutral',

    -- 特殊标记
    special_flags JSONB NOT NULL DEFAULT '{}',

    -- 交互统计
    total_interactions INTEGER NOT NULL DEFAULT 0,
    positive_interactions INTEGER NOT NULL DEFAULT 0,
    negative_interactions INTEGER NOT NULL DEFAULT 0,

    -- 时间戳
    last_interaction_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- 唯一约束
    CONSTRAINT unique_user_companion UNIQUE(user_id, companion_id)
);

-- 索引
CREATE INDEX idx_relationship_user ON companion_relationship_states(user_id);
CREATE INDEX idx_relationship_companion ON companion_relationship_states(companion_id);
CREATE INDEX idx_relationship_stage ON companion_relationship_states(romance_stage);
CREATE INDEX idx_relationship_last_interaction ON companion_relationship_states(last_interaction_at DESC);

COMMENT ON TABLE companion_relationship_states IS '伙伴关系状态表 - 存储用户与AI伙伴的关系核心数据';
COMMENT ON COLUMN companion_relationship_states.affinity_score IS '好感度分数 (0-1000)';
COMMENT ON COLUMN companion_relationship_states.trust_score IS '信任度分数 (0-100)';
COMMENT ON COLUMN companion_relationship_states.tension_score IS '紧张度分数 (0-100)';
COMMENT ON COLUMN companion_relationship_states.romance_stage IS '关系阶段';


-- 1.2 关系变化历史表
CREATE TABLE IF NOT EXISTS relationship_history (
    id SERIAL PRIMARY KEY,

    -- 关系标识
    user_id VARCHAR(255) NOT NULL,
    companion_id VARCHAR(255) NOT NULL,

    -- 变化类型
    change_type VARCHAR(50) NOT NULL,

    -- 变化数据
    old_value VARCHAR(100),
    new_value VARCHAR(100),
    delta INTEGER,

    -- 触发原因
    trigger_reason VARCHAR(255),
    trigger_context JSONB,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_history_user_companion ON relationship_history(user_id, companion_id);
CREATE INDEX idx_history_type ON relationship_history(change_type);
CREATE INDEX idx_history_created ON relationship_history(created_at DESC);

COMMENT ON TABLE relationship_history IS '关系变化历史表 - 记录所有重要的关系状态变化';


-- 1.3 情感日志表
CREATE TABLE IF NOT EXISTS emotion_logs (
    id SERIAL PRIMARY KEY,

    -- 关系标识
    user_id VARCHAR(255) NOT NULL,
    companion_id VARCHAR(255) NOT NULL,

    -- 情感分析结果
    primary_emotion VARCHAR(50) NOT NULL,
    emotion_intensity INTEGER NOT NULL,
    detected_emotions JSONB,
    user_intent VARCHAR(100),

    -- 状态变化
    affinity_change INTEGER DEFAULT 0,
    trust_change INTEGER DEFAULT 0,
    tension_change INTEGER DEFAULT 0,

    -- 标记
    is_memorable BOOLEAN NOT NULL DEFAULT FALSE,
    is_appropriate BOOLEAN NOT NULL DEFAULT TRUE,

    -- 消息摘要
    user_message_summary VARCHAR(500),
    ai_response_summary VARCHAR(500),

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_emotion_user_companion ON emotion_logs(user_id, companion_id);
CREATE INDEX idx_emotion_primary ON emotion_logs(primary_emotion);
CREATE INDEX idx_emotion_memorable ON emotion_logs(is_memorable) WHERE is_memorable = TRUE;
CREATE INDEX idx_emotion_created ON emotion_logs(created_at DESC);

COMMENT ON TABLE emotion_logs IS '情感日志表 - 记录每次交互的情感分析数据';


-- ============================================================
-- 2. 事件系统表
-- ============================================================

-- 2.1 事件定义表
CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,

    -- 事件标识
    event_code VARCHAR(100) UNIQUE NOT NULL,
    event_name VARCHAR(255) NOT NULL,

    -- 事件类型
    event_type VARCHAR(50) NOT NULL,
    category VARCHAR(50),

    -- 触发条件
    trigger_conditions JSONB NOT NULL,

    -- 可重复性
    is_repeatable BOOLEAN NOT NULL DEFAULT FALSE,
    cooldown_hours INTEGER DEFAULT 0,

    -- 事件内容
    script_content JSONB NOT NULL,
    effects JSONB,

    -- 优先级
    priority INTEGER DEFAULT 0,

    -- 启用状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- 描述
    description TEXT,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_event_code ON events(event_code);
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_event_active ON events(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_event_priority ON events(priority DESC);

COMMENT ON TABLE events IS '事件定义表 - 存储所有可触发事件的配置';
COMMENT ON COLUMN events.event_type IS '事件类型: MAIN/RANDOM/DATE/SPECIAL';


-- 2.2 用户事件历史表
CREATE TABLE IF NOT EXISTS user_event_history (
    id SERIAL PRIMARY KEY,

    -- 用户标识
    user_id VARCHAR(255) NOT NULL,
    companion_id VARCHAR(255) NOT NULL,

    -- 事件信息
    event_id INTEGER NOT NULL REFERENCES events(event_id),
    event_code VARCHAR(100) NOT NULL,

    -- 用户选择
    choice_made VARCHAR(10),
    choice_content VARCHAR(500),

    -- 事件结果
    result_data JSONB,

    -- 状态影响
    affinity_delta INTEGER DEFAULT 0,
    trust_delta INTEGER DEFAULT 0,
    tension_delta INTEGER DEFAULT 0,

    -- 完成状态
    is_completed BOOLEAN NOT NULL DEFAULT TRUE,

    -- 时间戳
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_event_history_user ON user_event_history(user_id, companion_id);
CREATE INDEX idx_event_history_event ON user_event_history(event_id);
CREATE INDEX idx_event_history_triggered ON user_event_history(triggered_at DESC);

COMMENT ON TABLE user_event_history IS '用户事件历史表 - 记录用户触发的所有事件';


-- 2.3 离线生活日志表
CREATE TABLE IF NOT EXISTS offline_life_logs (
    id SERIAL PRIMARY KEY,

    -- 伙伴标识
    companion_id VARCHAR(255) NOT NULL,

    -- 日志内容
    log_content TEXT NOT NULL,
    log_type VARCHAR(50),

    -- 重要性
    importance_score INTEGER NOT NULL DEFAULT 50 CHECK (importance_score >= 0 AND importance_score <= 100),

    -- 关联情感
    associated_emotion VARCHAR(50),

    -- 分享状态
    is_shared_with_user BOOLEAN NOT NULL DEFAULT FALSE,
    shared_at TIMESTAMP WITH TIME ZONE,

    -- 用户反馈
    user_reaction VARCHAR(50),

    -- 时间戳
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_offline_companion ON offline_life_logs(companion_id);
CREATE INDEX idx_offline_shared ON offline_life_logs(is_shared_with_user);
CREATE INDEX idx_offline_generated ON offline_life_logs(generated_at DESC);
CREATE INDEX idx_offline_importance ON offline_life_logs(importance_score DESC);

COMMENT ON TABLE offline_life_logs IS '离线生活日志表 - AI伙伴的离线活动记录';


-- 2.4 事件模板表
CREATE TABLE IF NOT EXISTS event_templates (
    id SERIAL PRIMARY KEY,

    -- 模板信息
    template_name VARCHAR(100) UNIQUE NOT NULL,
    template_type VARCHAR(50) NOT NULL,

    -- 模板内容
    template_content JSONB NOT NULL,
    required_variables JSONB,

    -- 描述
    description TEXT,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_template_name ON event_templates(template_name);
CREATE INDEX idx_template_type ON event_templates(template_type);

COMMENT ON TABLE event_templates IS '事件模板表 - 存储可重用的事件脚本模板';


-- ============================================================
-- 3. 初始化数据
-- ============================================================

-- 3.1 插入示例事件定义
INSERT INTO events (event_code, event_name, event_type, category, trigger_conditions, is_repeatable, script_content, effects, priority, description) VALUES
(
    'FIRST_MEETING',
    '初次见面',
    'MAIN',
    'milestone',
    '{"affinity_score": {"min": 0, "max": 100}, "total_interactions": 1}',
    FALSE,
    '{
        "intro": "这是我们第一次见面...",
        "dialogue": [
            {"speaker": "companion", "text": "你好！很高兴认识你~"},
            {"speaker": "system", "text": "选择你的回应："}
        ],
        "choices": [
            {"id": "A", "text": "你好，我也很高兴认识你", "affinity": 5},
            {"id": "B", "text": "嗯，你好", "affinity": 2},
            {"id": "C", "text": "...", "affinity": 0}
        ]
    }',
    '{"affinity_min": 0, "affinity_max": 5, "trust_min": 0, "trust_max": 3}',
    100,
    '用户与AI伙伴的第一次见面事件'
),
(
    'LEVEL_UP_FRIEND',
    '成为朋友',
    'MAIN',
    'romance',
    '{"romance_stage": "acquaintance", "affinity_score": {"min": 250, "max": 1000}}',
    FALSE,
    '{
        "intro": "经过这段时间的相处，我觉得我们已经成为朋友了。",
        "dialogue": [
            {"speaker": "companion", "text": "你知道吗...我觉得你是个很特别的人。"},
            {"speaker": "companion", "text": "我很开心能认识你，希望我们能成为好朋友！"}
        ]
    }',
    '{"affinity": 10, "trust": 5}',
    90,
    '关系升级：从认识到朋友'
),
(
    'RAINY_DAY_CHAT',
    '雨天闲聊',
    'RANDOM',
    'daily_life',
    '{"weather": "rainy", "probability": 0.3}',
    TRUE,
    '{
        "intro": "窗外下起了雨...",
        "dialogue": [
            {"speaker": "companion", "text": "听着雨声，感觉特别安静呢。"},
            {"speaker": "companion", "text": "你喜欢雨天吗？"}
        ],
        "choices": [
            {"id": "A", "text": "喜欢，雨天很舒服", "affinity": 3},
            {"id": "B", "text": "不太喜欢，有点压抑", "affinity": 2},
            {"id": "C", "text": "还好吧", "affinity": 1}
        ]
    }',
    '{"affinity_min": 1, "affinity_max": 3}',
    50,
    '随机触发的雨天对话事件'
);


-- 3.2 插入事件模板示例
INSERT INTO event_templates (template_name, template_type, template_content, required_variables, description) VALUES
(
    'simple_dialogue',
    'dialogue',
    '{
        "structure": {
            "intro": "{{intro_text}}",
            "dialogue": [
                {"speaker": "companion", "text": "{{companion_text}}"}
            ]
        }
    }',
    '["intro_text", "companion_text"]',
    '简单对话模板'
),
(
    'choice_based_event',
    'interactive',
    '{
        "structure": {
            "intro": "{{intro_text}}",
            "dialogue": [
                {"speaker": "companion", "text": "{{question}}"}
            ],
            "choices": "{{choices_array}}"
        }
    }',
    '["intro_text", "question", "choices_array"]',
    '选择题型事件模板'
);


-- ============================================================
-- 4. 创建视图（可选）
-- ============================================================

-- 4.1 关系状态摘要视图
CREATE OR REPLACE VIEW relationship_summary AS
SELECT
    r.user_id,
    r.companion_id,
    r.affinity_score,
    r.trust_score,
    r.tension_score,
    r.romance_stage,
    r.current_mood,
    r.total_interactions,
    r.last_interaction_at,
    CASE
        WHEN r.affinity_score >= 900 THEN 'excellent'
        WHEN r.affinity_score >= 600 THEN 'good'
        WHEN r.affinity_score >= 300 THEN 'normal'
        ELSE 'poor'
    END AS relationship_quality,
    ROUND(
        (r.positive_interactions::float / NULLIF(r.total_interactions, 0) * 100)::numeric,
        2
    ) AS positive_rate
FROM companion_relationship_states r;

COMMENT ON VIEW relationship_summary IS '关系状态摘要视图 - 提供关系质量和统计信息';


-- ============================================================
-- 5. 创建函数和触发器
-- ============================================================

-- 5.1 自动更新updated_at字段的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5.2 为需要的表添加触发器
CREATE TRIGGER update_relationship_updated_at
    BEFORE UPDATE ON companion_relationship_states
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_event_templates_updated_at
    BEFORE UPDATE ON event_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- 6. 权限设置（根据实际需要调整）
-- ============================================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;


-- ============================================================
-- 迁移完成
-- ============================================================

-- 验证查询
SELECT 'Migration completed successfully!' AS status;

-- 显示创建的表
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'companion_relationship_states',
    'relationship_history',
    'emotion_logs',
    'events',
    'user_event_history',
    'offline_life_logs',
    'event_templates'
)
ORDER BY table_name;
