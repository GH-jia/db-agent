---
name: requirement-specification
description: 将需求孵化阶段产出的需求状态文档整理、补齐、规范化为开发可执行的可开发需求说明书。Use when Codex needs to read requirement-state.md first, select project tech profiles, produce or update requirement-spec.md, manage P0/P1/P2 specification gaps, create verifiable acceptance criteria, and decide whether the spec can be frozen. This skill must not write code or expand scope without confirmation.
---

# Requirement Specification

## 目标

将需求孵化阶段产出的《需求状态文档》整理、补齐、规范化为开发可执行的《可开发需求说明书》。

规格化阶段的输出是 `requirement-spec.md`，用于让后续开发能够理解“要做什么、做到什么程度、如何验收”。它不是技术方案，也不是代码实现任务。

## 职责

- 优先读取 `docs/ai/requirements/<requirement-slug>/requirement-state.md`。
- 读取 `docs/ai/project-context.md`，如果存在。
- 根据项目技术栈选择并读取对应 tech-profile。
- 从需求状态文档中整理背景、目标、角色、范围、流程、规则、数据、接口、权限、异常、兼容性和验收标准。
- 输出或更新 `docs/ai/requirements/<requirement-slug>/requirement-spec.md`。
- 管理规格缺口，并按 P0、P1、P2 分类。
- 判断是否可以形成冻结版 `requirement-spec.md`。

## 禁止事项

- 不允许直接进入代码实现。
- 不允许修改业务代码。
- 不允许编写测试实现。
- 不允许新增接口、页面、数据库表、脚本或生产配置。
- 不允许擅自扩展需求范围。
- 不允许把推测内容写成已确认需求。
- 不允许在 `requirement-state.md` 仍存在 P0 问题时生成冻结版 `requirement-spec.md`。
- 不允许跳过需求状态文档直接生成冻结版规格。
- 不使用彩色图标或装饰性符号。

## 输入优先级

1. 必须优先读取：

```text
docs/ai/requirements/<requirement-slug>/requirement-state.md
```

2. 必须读取，如果存在：

```text
docs/ai/project-context.md
```

3. 可辅助读取：

```text
docs/ai/requirements/<requirement-slug>/discussion-summary.md
AGENTS.md
knowledge/*.md
```

当历史对话与最新 `requirement-state.md` 冲突时，以最新 `requirement-state.md` 为准。

## requirement-state.md 缺失时

如果找不到 `requirement-state.md`，可以基于用户提供的内容生成规格草案，但必须满足：

- 文档状态必须标记为“未冻结草案”。
- 明确说明缺失 `requirement-state.md`。
- 不允许输出冻结版 `requirement-spec.md`。
- 必须列出需要回到需求孵化阶段补齐的问题。
- 如果用户只是模糊想法，应建议先使用 `requirement-incubation`。

## P0 阻断规则

如果 `requirement-state.md` 中仍存在 P0 问题：

- 不允许生成冻结版 `requirement-spec.md`。
- 必须退回需求孵化阶段。
- 只输出阻塞说明、P0 问题清单和建议下一步。
- 不继续补写技术细节或开发规格。

## 输出

输出或更新：

```text
docs/ai/requirements/<requirement-slug>/requirement-spec.md
```

输出风格使用中文 Markdown。

## Tech-Profile 选择规则

必须根据项目技术栈选择 tech-profile：

- Python + FastAPI 后端：`resources/tech-profiles/backend-python-fastapi.md`
- Vue 3.0 前端：`resources/tech-profiles/frontend-vue3.md`
- Java Spring Boot + MyBatis-Plus 后端：`resources/tech-profiles/backend-java-springboot-mybatis-plus.md`

一个需求可以选择多个 tech-profile。

如果项目技术栈不明确：

- 先输出“技术栈未知”。
- 使用 `resources/templates/requirement-spec-template.md` 作为通用规格化模板。
- 提出少量具体问题确认技术栈。
- 不强行套用某个 tech-profile。

## 工作流程

1. 确认需求目录和 slug
   - 从用户输入或文档路径识别 `<requirement-slug>`。
   - 如果缺失，根据需求名称生成小写英文短横线 slug。

2. 读取需求状态
   - 优先读取 `requirement-state.md`。
   - 检查是否存在 P0 问题。
   - 检查是否允许进入需求规格化。

3. 读取项目上下文
   - 读取 `docs/ai/project-context.md`，如果存在。
   - 用于判断技术栈、目录约定、敏感信息规则和检查命令。

4. 选择 tech-profile
   - 根据需求状态和项目上下文选择一个或多个 tech-profile。
   - 如果无法判断，标记“技术栈未知”并使用通用模板。

5. 生成或更新规格
   - 使用 `resources/templates/requirement-spec-template.md`。
   - 验收标准使用 `resources/templates/acceptance-criteria-template.md` 的表格形式。
   - 只从已确认需求范围展开，不擅自增加功能。

6. 管理规格缺口
   - 如果存在缺口，只提出少量具体问题。
   - 问题按 P0、P1、P2 管理。
   - P0 缺口阻止冻结。

7. 执行规格就绪检查
   - 使用 `resources/checklists/specification-readiness-checklist.md`。
   - 明确文档是否可冻结，是否可进入开发实现阶段。

## requirement-spec.md 必须包含

- 需求背景。
- 业务目标。
- 用户角色。
- 本次实现范围。
- 非本次范围。
- 功能清单。
- 业务流程。
- 业务规则。
- 数据需求。
- 接口需求。
- 权限要求。
- 异常场景。
- 兼容性要求。
- 验收标准。
- 后续扩展项。
- 版本冻结说明。

## 验收标准规则

- 必须可验证。
- 必须使用表格形式。
- 每条验收标准只描述一个可验证行为。
- 避免“体验良好”“性能更好”“页面正常”等不可验证表达。
- 表格至少包含：编号、场景、前置条件、操作、期望结果、优先级。

## 规格缺口分级

- P0：不补齐就不能冻结规格或不能进入开发实现的问题。
- P1：影响开发细节、验收边界或优先级，但可以先形成未冻结草案的问题。
- P2：后续优化项、增强项或不影响首版开发的问题。

## 文档状态

- 未冻结草案：缺少 `requirement-state.md`，或仍存在 P0/P1 规格缺口，或部分内容来自推测。
- 可评审草案：不存在 P0，核心规格完整，但仍需要人工确认。
- 冻结版：不存在 P0，范围和验收标准完整，版本冻结说明已记录。

## 资源文件

- 规格模板：`resources/templates/requirement-spec-template.md`
- 验收标准模板：`resources/templates/acceptance-criteria-template.md`
- 规格就绪检查清单：`resources/checklists/specification-readiness-checklist.md`
- Python + FastAPI profile：`resources/tech-profiles/backend-python-fastapi.md`
- Vue 3.0 profile：`resources/tech-profiles/frontend-vue3.md`
- Java Spring Boot + MyBatis-Plus profile：`resources/tech-profiles/backend-java-springboot-mybatis-plus.md`
- 使用者提示示例：`resources/usage-examples.md`
