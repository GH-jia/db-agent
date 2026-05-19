# 项目上下文模板

## 项目概述

- 项目名称：db-agent
- 项目目标：制作一个数据库 agent，通过聊天交互方式实现查询表数据、查询元数据功能。
- 主要数据库：PostgreSQL
- 后端技术栈：Python 3.11、FastAPI
- 前端位置：`web/`

## 当前项目结构

| 目录或文件 | 说明 |
| --- | --- |
| `api/` | FastAPI 路由层，只处理请求参数、响应结构和路由组织 |
| `service/` | 业务逻辑层，包含 LLM 调用、数据库 agent、知识库、向量库逻辑 |
| `dao/` | 数据库连接、ORM 模型和底层数据访问 |
| `knowledge/` | 业务术语、数据库说明、查询示例等 agent 可使用的知识资料 |
| `web/` | 前端页面 |
| `config.yaml` | 项目配置文件，可能包含数据库、模型等敏感配置 |
| `db-agent.sql` | PostgreSQL 业务库建表 SQL 和后续表结构变更 SQL |

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

如果存在 P0 待澄清问题，不允许进入下一阶段。

历史对话与最新需求文档冲突时，以最新需求文档为准。

## 技术栈 Profile

可用 profile：

- `backend-python-fastapi`
- `frontend-vue3`
- `backend-java-springboot-mybatis-plus`

选择原则：

- 涉及当前项目后端接口、业务逻辑、数据库访问时，使用 `backend-python-fastapi`。
- 涉及 `web/` 前端页面、组件、交互或构建时，使用 `frontend-vue3`。
- 涉及 Java Spring Boot 和 MyBatis-Plus 项目时，使用 `backend-java-springboot-mybatis-plus`。

## 敏感信息规则

- 不在日志、接口响应、注释、需求文档或说明中暴露密码、token、API Key、数据库连接串。
- 读取 `config.yaml` 时只提取结构性信息，不复制敏感值。
- 涉及配置结构变更时，需要在规格文档中说明同步更新 `service/config.py` 及相关调用代码。

## 数据库规则

- 业务数据库使用 PostgreSQL。
- 表结构、业务术语、典型查询方式发生变化时，应同步更新 `knowledge/` 下对应 Markdown 文件。
- 新增或调整业务表结构时，应同步更新 `db-agent.sql`。
- 维护 `db-agent.sql` 时采用追加式变更。
- 不新增外键约束；表之间的关联字段只做业务关联，必要时通过索引优化查询。

## 检查命令

后端代码修改后至少执行：

```powershell
.\.venv\Scripts\python -m compileall api service dao main.py logging_config.py
```

前端代码修改后至少执行：

```powershell
cd web
npm run build
```

需求孵化和需求规格化阶段不修改业务代码，因此通常不需要执行上述构建或语法检查。

## 待补充项目背景

以下内容可在项目推进中持续补充：

- 主要用户：
- 核心业务对象：
- 当前已支持能力：
- 已知限制：
- 近期优先级：
- 常见验收口径：
