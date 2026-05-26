# 项目上下文

更新时间：2026-05-21

## 项目概述

| 项目 | 内容 |
| --- | --- |
| 项目名称 | db-agent |
| 项目类型 | 前后端分离的单体应用 |
| 项目目标 | 制作数据库 agent，通过聊天交互查询表数据、查询元数据，并维护 agent 可使用的数据源连接 |
| 后端入口 | `main.py` |
| 后端源码 | `app/` |
| 前端源码 | `web/` |
| 主要业务库 | PostgreSQL |
| 配置文件 | `config.yaml`，包含模型、数据库、Qdrant 等配置结构，可能包含敏感值 |

## 当前技术栈 Profile

| Profile | 置信度 | 证据 |
| --- | ---: | --- |
| `backend-python-fastapi` | 高 | `requirements.txt` 包含 `fastapi`、`uvicorn`、`sqlalchemy`、`psycopg2-binary`、`openai`、`qdrant-client`；`main.py` 创建 `FastAPI()` 并挂载 `app.api.*` 路由 |
| `frontend-vue3` | 高 | `web/package.json` 依赖 `vue` 3.x、`vite`、`@vitejs/plugin-vue`；`web/src/main.js` 使用 `createApp`；页面为 `.vue` 文件 |
| `backend-java-springboot-mybatis-plus` | 无当前证据 | 仓库未发现 `pom.xml`、`build.gradle`、`src/main/java`、Spring Boot 或 MyBatis-Plus 文件 |

## 仓库结构

| 目录或文件 | 当前职责 | 证据状态 |
| --- | --- | --- |
| `main.py` | FastAPI 应用入口，配置生命周期、请求日志中间件、路由挂载，使用 uvicorn 在 `127.0.0.1:8000` 启动 | 已确认 |
| `logging_config.py` | 后端日志配置 | 已确认 |
| `requirements.txt` | 后端 Python 依赖清单 | 已确认 |
| `config.yaml` | 后端运行配置，包含 `API_KEY`、`CHAT_MODEL`、`EMBEDDING_MODEL`、`EMBEDDING_DIM`、`QDRANT.*`、`DATABASE.*` 等键 | 已确认结构，敏感值未记录 |
| `app/api/` | FastAPI 路由层 | 已确认 |
| `app/service/` | 业务逻辑层，包含 LLM、agent、数据源、知识库、向量库、配置读取 | 已确认 |
| `app/service/data_source/` | 目标数据源抽象、连接配置 schema、PostgreSQL/MySQL provider | 已确认 |
| `app/dao/` | SQLAlchemy engine、SessionLocal、ORM 模型 | 已确认 |
| `app/knowledge/` | 本地知识库 Markdown：数据库说明、业务术语、查询示例 | 已确认 |
| `web/` | Vue 3 + Vite 前端 | 已确认 |
| `docs/ai/requirements/` | 需求孵化和需求规格化文档目录 | 已确认 |
| `.agents/skills/` | 项目内需求孵化、需求规格化技能 | 已确认 |
| `db-agent.sql` | PostgreSQL 业务库建表 SQL 和后续变更 SQL | 已确认 |
| `logs/` | 运行日志，不作为源码搜索重点 | 已确认 |

## 后端上下文

| 模块 | 说明 |
| --- | --- |
| `app/api/agent.py` | `/agent` 路由，包含 `/query` 和 `/chat`，负责数据库 agent 查询和对话 |
| `app/api/chat.py` | `/chat` 路由，包含 `/stream` 和 `/clear`，用于基础 LLM 对话流和清空会话 |
| `app/api/db_connections.py` | `/db-connections` 路由，提供数据源连接的列表、创建、查询、更新、删除 |
| `app/api/items.py` | `/items` 示例 CRUD 路由 |
| `app/api/knowledge.py` | `/knowledge` 路由，提供知识库重建和检索 |
| `app/service/chat_llm.py` | OpenAI SDK 调用、基础对话和流式输出 |
| `app/service/db_agent.py` | 意图分类、SQL 生成、SQL 只读校验、元数据回答、查询结果总结 |
| `app/service/agent_chat.py` | 数据库 agent 多轮会话编排和消息持久化 |
| `app/service/db_connection.py` | 数据源连接管理业务逻辑 |
| `app/service/data_source/` | 支持 PostgreSQL 与 MySQL 的目标数据源元数据读取和查询执行 |
| `app/service/knowledge_base.py` | 从 `app/knowledge/` 加载 Markdown、切分知识片段并进行检索 |
| `app/service/embedding.py` | OpenAI embedding 调用 |
| `app/service/qdrant_store.py` | Qdrant collection 管理、向量写入和搜索 |
| `app/dao/database.py` | 从 `config.yaml` 读取 `DATABASE.*`，创建 SQLAlchemy engine 和 SessionLocal |
| `app/dao/models.py` | ORM 模型：`items`、`agent_db_connections`、`agent_sessions`、`agent_messages` |

### 后端约定

- 路由层使用 `APIRouter`，请求体多为 Pydantic `BaseModel`。
- 数据库会话通过 `SessionLocal()` 和 FastAPI `Depends(get_db)` 注入，当前为同步 SQLAlchemy 风格。
- `main.py` 在应用启动路径中执行 `Base.metadata.create_all(bind=engine)`。
- 异常处理以 `HTTPException` 为主，未发现统一响应包装或全局异常处理模块。
- 数据库 agent 当前只允许生成和执行单条 `SELECT`，禁止 `INSERT`、`UPDATE`、`DELETE`、`DROP`、`ALTER`、`TRUNCATE`、`CREATE`、`GRANT`、`REVOKE` 等关键字。
- 数据源连接业务支持 `postgresql` 和 `mysql`；项目自身业务库仍使用 PostgreSQL。

## 前端上下文

| 模块 | 说明 |
| --- | --- |
| `web/package.json` | npm scripts：`dev`、`build`、`preview`；依赖 Vue 3 和 Vite |
| `web/vite.config.js` | Vite 配置，启用 Vue 插件，并把 `/agent`、`/db-connections` 代理到 `http://127.0.0.1:8000` |
| `web/src/main.js` | Vue 应用入口，挂载 `App.vue` |
| `web/src/App.vue` | 应用壳，使用本地状态在“智能问答”和“数据源管理”两个页面间切换 |
| `web/src/pages/ChatPage.vue` | agent 聊天页面 |
| `web/src/pages/DbConnectionPage.vue` | 数据源连接管理页面 |
| `web/src/api/http.js` | 基于浏览器 `fetch` 的 JSON 请求封装 |
| `web/src/api/agent.js` | `/agent/chat` 与连接列表相关请求 |
| `web/src/api/dbConnections.js` | `/db-connections` CRUD 请求 |
| `web/src/styles.css` | 前端样式 |

### 前端约定

- 当前未使用 `vue-router`、Pinia、Axios 或 UI 组件库。
- 页面切换由 `App.vue` 内部状态控制。
- API 请求使用 `fetch` 封装，错误信息优先取响应体的 `detail` 或 `message`。
- 开发服务通过 Vite 代理访问后端，后端默认端口为 `8000`。

## API 约定

| 路由 | 方法 | 用途 |
| --- | --- | --- |
| `/agent/query` | POST | 根据数据源连接和自然语言问题生成 SQL、执行查询并返回数据 |
| `/agent/chat` | POST | 数据库 agent 多轮对话 |
| `/chat/stream` | POST | 基础 LLM 流式对话 |
| `/chat/clear` | POST | 清空基础 LLM 会话历史 |
| `/db-connections` | GET | 分页列出数据源连接，支持 `user_id`、`db_type`、`status`、`keyword` 过滤 |
| `/db-connections` | POST | 创建数据源连接 |
| `/db-connections/{connection_id}` | GET | 查询单个数据源连接 |
| `/db-connections/{connection_id}` | PUT | 更新数据源连接 |
| `/db-connections/{connection_id}` | DELETE | 删除数据源连接 |
| `/knowledge/rebuild` | POST | 重建本地知识库向量索引 |
| `/knowledge/search` | POST | 搜索本地知识库 |
| `/items`、`/items/{item_id}` | GET/POST/PUT/DELETE | 示例 items CRUD |

## 数据库约定

- 项目自身业务库通过 `config.yaml` 的 `DATABASE.HOST`、`DATABASE.PORT`、`DATABASE.NAME`、`DATABASE.USER`、`DATABASE.PASSWORD` 配置。
- ORM 使用 SQLAlchemy，模型集中在 `app/dao/models.py`。
- `db-agent.sql` 记录 PostgreSQL 建表和后续变更 SQL。
- 当前 ORM 模型包含 `agent_db_connections`、`agent_sessions`、`agent_messages`、`items`。
- `db-agent.sql` 目前包含 `agent_messages` 到 `agent_sessions` 的外键约束；这与“新增约束应谨慎并通过需求规格确认”的原则有关，后续变更需以实际需求和最新文档为准。
- 目标数据源 provider 当前支持 PostgreSQL 和 MySQL，元数据通过 `information_schema` 查询。

## 权限和安全约定

- 当前未发现认证、授权、权限注解或登录态机制。
- 数据源连接接口存在 `user_id` 字段和过滤参数，但未发现鉴权约束。
- 不得在日志、接口响应、文档或注释中暴露 `config.yaml` 内的敏感值、数据库密码、API Key、token 或完整连接串。
- 数据库 agent 只读查询校验在 `app/service/db_agent.py` 中实现。
- `app/service/db_connection.py` 的 `to_response` 不返回密码明文，只返回 `has_password`。

## 错误处理和日志约定

- 后端使用 Python `logging`，`main.py` 中间件记录请求方法、路径、状态码、耗时。
- 路由层常见异常映射为 `HTTPException`，常见状态码包括 400、404、500。
- `requestJson` 在前端把非 2xx 响应转换为 `Error`，错误文案来自 `detail`、`message` 或默认“请求失败”。
- 日志应保留操作上下文，但不能记录敏感信息。

## 构建、运行和校验命令

| 场景 | 命令 | 证据 |
| --- | --- | --- |
| 安装后端依赖 | `.\.venv\Scripts\python -m pip install -r requirements.txt` | 项目约定与 `requirements.txt` |
| 启动后端 | `.\.venv\Scripts\python main.py` | `main.py` 包含 uvicorn 启动入口 |
| 后端语法检查 | `.\.venv\Scripts\python -m compileall app main.py logging_config.py` | 当前后端源码位于 `app/` |
| 安装前端依赖 | `cd web` 后执行 `npm install` | `web/package.json` 与 `web/package-lock.json` |
| 启动前端开发服务 | `cd web` 后执行 `npm run dev` | `web/package.json` 的 `dev` script |
| 构建前端 | `cd web` 后执行 `npm run build` | `web/package.json` 的 `build` script |
| 预览前端构建 | `cd web` 后执行 `npm run preview` | `web/package.json` 的 `preview` script |

当前未发现 `pytest`、lint、type-check、Docker、Maven、Gradle 或 CI 工作流命令配置。

## 测试约定

- 当前仓库未发现 `tests/` 目录、`pytest.ini`、`pyproject.toml` 测试配置或 npm test script。
- 修改后端代码后的最低校验是 `compileall`。
- 修改前端代码后的最低校验是 `npm run build`。
- 不要在没有项目文件证据的情况下编造测试命令。

## 需求工作流约定

每个需求使用独立目录：

```text
docs/ai/requirements/<requirement-slug>/
```

需求孵化阶段输出：

```text
docs/ai/requirements/<requirement-slug>/requirement-state.md
```

需求规格化阶段输出：

```text
docs/ai/requirements/<requirement-slug>/requirement-spec.md
```

规则：

- 需求开发前优先使用需求前置工作流。
- 如果存在 P0 待澄清问题，不允许进入下一阶段。
- 历史对话与最新需求文档冲突时，以最新需求文档为准。
- 需求文档输出语言为中文 Markdown。
- 需求孵化和需求规格化阶段不修改业务代码。

## 已知风险与约束

- `config.yaml` 当前是未跟踪文件，但后端运行依赖它；处理时只读取结构，不复制敏感值。
- 旧上下文曾把后端目录写为根级 `api/`、`service/`、`dao/`、`knowledge/`，当前实际目录是 `app/api/`、`app/service/`、`app/dao/`、`app/knowledge/`。
- `db-agent.sql` 中 `agent_db_connections` 的历史建表 SQL 与当前 ORM 在支持 MySQL、密码字段命名等方面存在变更记录，后续数据库变更应同时核对 ORM 与追加 SQL。
- 当前未发现自动化测试体系，功能变更时需要根据风险补充或至少执行现有最低校验。
- 当前未发现认证授权机制，涉及多用户、连接隔离或权限控制的需求必须先规格化。

## 低置信度或缺失信息

- 未发现 README。
- 未发现 Dockerfile、docker-compose、CI 工作流。
- 未发现后端 lint、format、pytest 配置。
- 未发现前端 lint、test、type-check script。
- 未发现统一响应 schema 或全局异常处理模块。
- 未发现数据库迁移工具，如 Alembic。

## 更新历史

| 日期 | 更新内容 |
| --- | --- |
| 2026-05-21 | 重新扫描仓库，更新实际目录为 `app/...`，补充 Vue 3 + Vite 前端、数据源 provider、API 路由、命令、缺失测试/CI 信息，并生成上下文报告 |
