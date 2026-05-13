## 基本约定

文件使用UTF8编码，不要使用UTF8 with BOM编码。
业务数据库使用 postgresql 。
这个项目已有依赖列表参考`requirements.txt`文件内容。
项目配置文件是`config.yaml`，其中有数据库、模型相关配置信息。
当前开发环境默认使用Python 3.11.0创建的`.venv`虚拟环境。
项目启动文件是`main.py`。
项目目标是制作一个数据库 agent ，可以通过聊天交互方式实现查询表数据、查询元数据功能。
在开发时，应该从最简单的版本开始，逐步完善功能。
你在讲解代码时要通俗易懂。

## 项目结构

`api/`：FastAPI路由层，只处理请求参数、响应结构和路由组织。
`service/`：业务逻辑层，包含LLM调用、数据库agent、知识库、向量库逻辑。
`dao/`：数据库连接、ORM模型和底层数据访问。
`knowledge/`：业务术语、数据库说明、查询示例等可被agent使用的知识资料。
`logs/`：运行日志，不作为源码搜索重点。

## 运行和依赖

项目依赖使用`requirements.txt`管理，安装命令是：

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

启动项目命令是：

```powershell
.\.venv\Scripts\python main.py
```

修改代码后至少执行语法检查：

```powershell
.\.venv\Scripts\python -m compileall api service dao main.py logging_config.py
```

## 搜索规则

当前环境不可使用`rg`。
搜索文件时使用PowerShell的`Get-ChildItem`和`Select-String`。
只搜索项目源码目录和根目录下文件，不要搜索`.venv`、`.git`、`.idea`、`__pycache__`、`logs`文件夹。


## 配置和敏感信息

`config.yaml`可能包含数据库、模型、API Key等敏感配置。
不要在日志、接口响应、注释或说明中暴露密码、token、API Key、数据库连接串。
修改配置结构时，需要同步更新`service/config.py`及相关调用代码。

## Agent行为边界

不确定用户意图时，应先询问澄清问题，不要猜测执行高风险操作。

## 代码组织

新增接口放在`api/`。
新增业务逻辑放在`service/`。
新增数据库模型或连接相关逻辑放在`dao/`。
不要把复杂业务逻辑直接写在路由函数中。
优先保持简单实现，确认可运行后再抽象。

## 依赖管理

新增第三方依赖前先确认`requirements.txt`中是否已有可用依赖。
如确需新增依赖，必须同步更新`requirements.txt`。
不要引入重量级框架来解决小问题。

## 知识库维护

数据库表结构、业务术语、典型查询方式发生变化时，应同步更新`knowledge/`下对应Markdown文件。
`knowledge/database.md`记录表、字段、关系和注意事项。
`knowledge/business_terms.md`记录业务术语解释。
`knowledge/query_examples.md`记录常见自然语言问题和SQL示例。

## 日志规则

使用`logging`，不使用`print`作为长期日志方案。
日志中不要记录敏感信息。
异常日志应保留足够上下文，例如接口路径、操作类型，但不要泄露用户密钥或数据库密码。

## 数据库脚本

根目录下的`db-agent.sql`用于记录 PostgreSQL 业务库的建表 SQL 和后续表结构变更 SQL。
新增或调整业务表结构时，应同步更新`db-agent.sql`。
维护`db-agent.sql`时采用追加式变更：
- 对于已有表的表结构修改，不要回改已有的`CREATE TABLE`语句，只能在文件末尾追加`ALTER TABLE`等变更 SQL。
- 新建表 SQL 也要追加到`db-agent.sql`文件末尾，不要插入到已有 SQL 中间。
- 不要新增外键约束；表之间的关联字段只做业务关联，必要时通过索引优化查询。
