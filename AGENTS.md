## 项目角色

本项目是一个数据库 agent 应用，目标是通过聊天交互查询表数据、查询数据库元数据，并维护 agent 可使用的数据源连接。

## 当前技术栈 Profile

- `backend-python-fastapi`：后端使用 Python 3.11、FastAPI、SQLAlchemy、PostgreSQL、OpenAI SDK、Qdrant。
- `frontend-vue3`：前端位于 `web/`，使用 Vue 3 和 Vite。

如需求涉及 Java Spring Boot 与 MyBatis-Plus，只能在有对应项目文件证据时使用 `backend-java-springboot-mybatis-plus`。

## 必读上下文

开发前先阅读：

- `docs/ai/project-context.md`
- `requirements.txt`
- `web/package.json`（涉及前端时）
- `config.yaml` 的结构（只读取键名和结构，不复制敏感值）

## 基本约定

- 文件使用 UTF-8 编码，不要使用 UTF-8 with BOM。
- 当前环境不可使用 `rg`。搜索文件时使用 PowerShell 的 `Get-ChildItem` 和 `Select-String`。
- 不搜索 `.venv`、`.git`、`.idea`、`__pycache__`、`logs`、`web/node_modules`、`web/dist`。
- 不确定用户意图时，先询问澄清问题，不要猜测执行高风险操作。
- 讲解代码时使用通俗易懂的中文。

## 文件职责

- `main.py`：FastAPI 应用入口和路由挂载。
- `app/api/`：FastAPI 路由层，只处理请求参数、响应结构和路由组织。
- `app/service/`：业务逻辑层，包含 LLM 调用、数据库 agent、数据源、知识库、向量库逻辑。
- `app/dao/`：数据库连接、SQLAlchemy ORM 模型和底层数据库会话。
- `app/knowledge/`：业务术语、数据库说明、查询示例等 agent 可使用的知识资料。
- `web/`：Vue 3 + Vite 前端页面。
- `db-agent.sql`：PostgreSQL 业务库建表 SQL 和后续表结构变更 SQL。

## 运行和校验

安装后端依赖：

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

启动后端：

```powershell
.\.venv\Scripts\python main.py
```

修改后端代码后至少执行语法检查：

```powershell
.\.venv\Scripts\python -m compileall app main.py logging_config.py
```

安装前端依赖：

```powershell
cd web
npm install
```

启动前端开发服务：

```powershell
cd web
npm run dev
```

修改前端代码后至少执行构建检查：

```powershell
cd web
npm run build
```

当前仓库未发现已配置的自动化测试命令。不要编造测试命令。

## 配置和敏感信息

- `config.yaml` 可能包含数据库、模型、API Key、Qdrant 等敏感配置。
- 不在日志、接口响应、注释、需求文档或说明中暴露密码、token、API Key、数据库连接串。
- 修改配置结构时，需要同步更新 `app/service/config.py`、`app/dao/database.py` 及相关调用代码。

## 代码组织

- 新增接口放在 `app/api/`。
- 新增业务逻辑放在 `app/service/`。
- 新增数据库模型或连接相关逻辑放在 `app/dao/`。
- 不要把复杂业务逻辑直接写在路由函数中。
- 优先保持简单实现，确认可运行后再抽象。
- 新增第三方依赖前先确认 `requirements.txt` 或 `web/package.json` 中是否已有可用依赖；确需新增时同步更新依赖清单。

## 知识库和数据库脚本

- 数据库表结构、业务术语、典型查询方式发生变化时，同步更新 `app/knowledge/` 下对应 Markdown 文件。
- 新增或调整业务表结构时，同步更新 `db-agent.sql`。
- 维护 `db-agent.sql` 时采用追加式变更：已有表结构修改追加 `ALTER TABLE` 等变更 SQL；新建表 SQL 追加到文件末尾。

## 日志规则

- 使用 `logging`，不使用 `print` 作为长期日志方案。
- 日志中不要记录敏感信息。
- 异常日志应保留接口路径、操作类型等必要上下文，但不要泄露用户密钥或数据库密码。

