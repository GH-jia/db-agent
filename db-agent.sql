-- db-agent project PostgreSQL schema script.
-- This file records business database table creation and schema changes.

CREATE TABLE IF NOT EXISTS agent_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL UNIQUE,
    user_id VARCHAR(100),
    title VARCHAR(200),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_agent_sessions_status
        CHECK (status IN ('active', 'archived'))
);

COMMENT ON TABLE agent_sessions IS '数据库 agent 用户会话表';
COMMENT ON COLUMN agent_sessions.id IS '自增主键';
COMMENT ON COLUMN agent_sessions.session_id IS '会话业务 ID，由接口或服务生成并传递';
COMMENT ON COLUMN agent_sessions.user_id IS '用户 ID，当前没有用户体系时可以为空';
COMMENT ON COLUMN agent_sessions.title IS '会话标题';
COMMENT ON COLUMN agent_sessions.status IS '会话状态：active 或 archived';
COMMENT ON COLUMN agent_sessions.created_at IS '创建时间';
COMMENT ON COLUMN agent_sessions.updated_at IS '更新时间';

CREATE TABLE IF NOT EXISTS agent_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    intent VARCHAR(50),
    sql_text TEXT,
    extra JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_agent_messages_session
        FOREIGN KEY (session_id)
        REFERENCES agent_sessions (session_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_agent_messages_role
        CHECK (role IN ('system', 'user', 'assistant', 'tool'))
);

COMMENT ON TABLE agent_messages IS '数据库 agent 会话消息表';
COMMENT ON COLUMN agent_messages.id IS '自增主键';
COMMENT ON COLUMN agent_messages.session_id IS '所属会话业务 ID';
COMMENT ON COLUMN agent_messages.role IS '消息角色：system、user、assistant 或 tool';
COMMENT ON COLUMN agent_messages.content IS '消息正文';
COMMENT ON COLUMN agent_messages.intent IS '消息意图，例如 data_query、metadata_query 或 chat';
COMMENT ON COLUMN agent_messages.sql_text IS '本轮消息生成或执行的 SQL，仅记录查询语句';
COMMENT ON COLUMN agent_messages.extra IS '扩展信息，例如 row_count、错误信息、工具调用摘要等';
COMMENT ON COLUMN agent_messages.created_at IS '创建时间';

CREATE INDEX IF NOT EXISTS idx_agent_messages_session_id
    ON agent_messages (session_id);

CREATE INDEX IF NOT EXISTS idx_agent_messages_session_created_at
    ON agent_messages (session_id, created_at);
