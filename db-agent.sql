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

CREATE TABLE IF NOT EXISTS agent_db_connections (
    id BIGSERIAL PRIMARY KEY,
    connection_id VARCHAR(64) NOT NULL UNIQUE,
    user_id VARCHAR(100),
    name VARCHAR(100) NOT NULL,
    db_type VARCHAR(30) NOT NULL DEFAULT 'postgresql',
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_ciphertext TEXT NOT NULL,
    ssl_mode VARCHAR(20) NOT NULL DEFAULT 'prefer',
    readonly BOOLEAN NOT NULL DEFAULT true,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    extra JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_tested_at TIMESTAMPTZ,
    last_test_success BOOLEAN,
    last_test_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_agent_db_connections_db_type
        CHECK (db_type IN ('postgresql')),
    CONSTRAINT chk_agent_db_connections_port
        CHECK (port > 0 AND port <= 65535),
    CONSTRAINT chk_agent_db_connections_ssl_mode
        CHECK (ssl_mode IN ('disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full')),
    CONSTRAINT chk_agent_db_connections_status
        CHECK (status IN ('active', 'disabled'))
);

COMMENT ON TABLE agent_db_connections IS '数据库 agent 用户数据库连接配置表';
COMMENT ON COLUMN agent_db_connections.id IS '自增主键';
COMMENT ON COLUMN agent_db_connections.connection_id IS '数据库连接配置业务 ID，由接口或服务生成并传递';
COMMENT ON COLUMN agent_db_connections.user_id IS '用户 ID，当前没有用户体系时可以为空';
COMMENT ON COLUMN agent_db_connections.name IS '连接配置名称，例如测试库或生产只读库';
COMMENT ON COLUMN agent_db_connections.db_type IS '数据库类型，当前仅支持 postgresql';
COMMENT ON COLUMN agent_db_connections.host IS '数据库主机地址';
COMMENT ON COLUMN agent_db_connections.port IS '数据库端口';
COMMENT ON COLUMN agent_db_connections.database_name IS '数据库名称';
COMMENT ON COLUMN agent_db_connections.username IS '数据库用户名';
COMMENT ON COLUMN agent_db_connections.password_ciphertext IS '加密后的数据库密码，不保存明文密码';
COMMENT ON COLUMN agent_db_connections.ssl_mode IS 'PostgreSQL SSL 模式';
COMMENT ON COLUMN agent_db_connections.readonly IS '是否只允许只读查询';
COMMENT ON COLUMN agent_db_connections.status IS '连接配置状态：active 或 disabled';
COMMENT ON COLUMN agent_db_connections.extra IS '扩展连接参数，不能保存明文密码、token 或 API Key';
COMMENT ON COLUMN agent_db_connections.last_tested_at IS '最近一次测试连接时间';
COMMENT ON COLUMN agent_db_connections.last_test_success IS '最近一次测试连接是否成功';
COMMENT ON COLUMN agent_db_connections.last_test_message IS '最近一次测试连接结果摘要，不能包含敏感信息';
COMMENT ON COLUMN agent_db_connections.created_at IS '创建时间';
COMMENT ON COLUMN agent_db_connections.updated_at IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_agent_db_connections_user_id
    ON agent_db_connections (user_id);

CREATE INDEX IF NOT EXISTS idx_agent_db_connections_status
    ON agent_db_connections (status);

ALTER TABLE agent_sessions
    ADD COLUMN IF NOT EXISTS db_connection_id VARCHAR(64);

COMMENT ON COLUMN agent_sessions.db_connection_id IS '会话绑定的数据库连接配置业务 ID';

CREATE INDEX IF NOT EXISTS idx_agent_sessions_db_connection_id
    ON agent_sessions (db_connection_id);

ALTER TABLE agent_db_connections
    DROP CONSTRAINT IF EXISTS chk_agent_db_connections_db_type;

COMMENT ON COLUMN agent_db_connections.db_type IS '数据库类型，支持 postgresql、mysql';
COMMENT ON COLUMN agent_db_connections.ssl_mode IS '数据库 SSL/TLS 模式';

ALTER TABLE agent_db_connections
            RENAME COLUMN password_ciphertext TO password;

COMMENT ON COLUMN agent_db_connections.password IS 'Database password stored as plaintext for target data source connections';
