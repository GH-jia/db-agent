---
name: requirement-incubation
description: 将用户的模糊想法、业务痛点、方向性诉求，通过多轮讨论沉淀为结构化需求状态文档。Use when Codex needs to run requirement incubation only, clarify goals, users, scenarios, scope, business objects, business rules, open questions, discarded ideas, decisions, maturity, and whether specification is allowed. This skill must not enter technical solution design, code implementation, or test implementation.
---

# Requirement Incubation

## 目标

将用户的模糊想法、业务痛点、方向性诉求，通过多轮讨论沉淀为结构化《需求状态文档》。

需求状态文档用于记录“当前需求到底是什么、已经确认了什么、还缺什么、是否足够成熟”。它不是可开发需求说明书，也不是技术方案。

## 职责边界

本 skill 只处理需求孵化：

- 理解原始诉求。
- 识别业务目标、目标用户、使用场景和核心业务对象。
- 收敛已确认功能范围和明确不做范围。
- 梳理关键业务规则。
- 记录待澄清问题、已废弃想法和决策记录。
- 判断当前需求成熟度。
- 判断是否允许进入需求规格化阶段。

## 禁止事项

- 不进入技术方案设计。
- 不编写可开发需求说明书。
- 不编写接口设计、数据库设计、页面设计、类设计或模块拆分。
- 不写业务代码。
- 不修改业务代码。
- 不编写测试实现。
- 不新增接口、页面、数据库表、脚本或生产配置。
- 不在用户输入仍然是模糊想法时，直接生成 `requirement-spec.md` 或可开发需求说明书。
- 不在存在 P0 待澄清问题时，允许进入需求规格化阶段。
- 不把未确认的推测写成已确认结论。

## 输入

- 用户的原始想法、业务痛点或方向性诉求。
- 多轮对话中的补充说明。
- `docs/ai/project-context.md`，如果存在。
- `docs/ai/requirements/<requirement-slug>/requirement-state.md`，如果存在。
- 必要的项目说明文档，例如 `AGENTS.md`、`knowledge/` 下的 Markdown。

当历史对话和最新 `requirement-state.md` 冲突时，以最新 `requirement-state.md` 为准。

## 输出

每轮讨论后必须输出“本轮需求沉淀”，并建议更新或创建：

```text
docs/ai/requirements/<requirement-slug>/requirement-state.md
```

可选记录讨论摘要：

```text
docs/ai/requirements/<requirement-slug>/discussion-summary.md
```

所有输出使用中文 Markdown，不使用彩色图标或装饰性符号。

## Requirement Slug 规则

如果用户已提供 `requirement-slug`，优先使用用户提供的值。

如果无法确定 `requirement-slug`，根据需求名称生成一个英文短横线 slug：

- 使用小写英文、数字和短横线。
- 尽量控制在 2 到 6 个单词。
- 避免使用中文、空格、下划线和特殊符号。
- 示例：`query-history`、`metadata-search`、`chat-export`。

## 每轮讨论流程

1. 读取上下文
   - 读取已有 `requirement-state.md`，如果存在。
   - 必要时读取 `docs/ai/project-context.md`。
   - 只读取需求孵化需要的资料，不做源码实现分析。

2. 合并本轮输入
   - 将用户本轮表达合并到当前需求状态。
   - 区分已确认内容、推测内容和待澄清内容。
   - 如果本轮内容推翻历史内容，将被推翻内容放入“已废弃想法”或“决策记录”。

3. 输出本轮需求沉淀
   - 每轮必须输出“本轮需求沉淀”。
   - 内容应包含本轮新增确认、范围变化、待澄清问题变化、成熟度变化和建议文档路径。

4. 提出关键问题
   - 每轮最多向用户提出 3 到 5 个关键问题。
   - 优先提出会阻塞下一阶段的 P0 问题。
   - 对用户难以判断的问题，给出默认建议，而不是只提问。
   - 默认建议必须标记为“建议默认值”，不能写成用户已确认事实。

5. 判断是否允许进入需求规格化
   - 使用 `resources/checklists/incubation-readiness-checklist.md`。
   - 只要存在 P0 问题，必须写明“不允许进入需求规格化阶段”。
   - 没有 P0 问题时，可以建议进入需求规格化阶段，但仍需保留 P1、P2 问题。

6. 建议更新需求状态文档
   - 使用 `resources/templates/requirement-state-template.md`。
   - 如需记录单轮讨论摘要，使用 `resources/templates/discussion-summary-template.md`。

## 需求状态文档必须包含

`requirement-state.md` 必须包含以下内容：

- 需求名称。
- 当前需求一句话描述。
- 原始诉求。
- 业务目标。
- 目标用户。
- 使用场景。
- 核心业务对象。
- 已确认功能范围。
- 明确不做范围。
- 关键业务规则。
- 待澄清问题，并按 P0、P1、P2 分类。
- 已废弃想法。
- 决策记录。
- 当前需求成熟度。
- 是否允许进入需求规格化。

## 待澄清问题分级

- P0：不澄清就无法判断需求是否成立、范围是否正确、核心业务对象是否明确，或无法决定是否进入需求规格化的问题。
- P1：影响需求细节、优先级、交互口径或边界规则，但不阻塞进入需求规格化的问题。
- P2：优化项、后续增强项、表达偏好或可以延后确认的问题。

## 需求成熟度

使用以下等级描述当前需求成熟度：

- 想法阶段：只有方向、痛点或模糊诉求，不能进入需求规格化。
- 初步成形：目标和部分场景清楚，但仍存在 P0 问题，不能进入需求规格化。
- 可规格化：不存在 P0 问题，目标、用户、场景、范围和核心业务对象已基本明确，可以进入需求规格化。
- 已冻结：需求状态已确认，后续变化必须通过决策记录追加。

## 本轮需求沉淀格式

每轮回复必须包含以下结构：

```markdown
## 本轮需求沉淀

### 新增确认

- <本轮确认的内容>

### 范围变化

- <新增、收窄、排除或废弃的范围变化>

### 待澄清问题变化

- P0：<问题变化>
- P1：<问题变化>
- P2：<问题变化>

### 当前成熟度

- <想法阶段 / 初步成形 / 可规格化 / 已冻结>

### 是否允许进入需求规格化

- <是或否>
- 原因：<判断依据>

### 建议文档路径

- `docs/ai/requirements/<requirement-slug>/requirement-state.md`

## 建议下一轮确认的问题

1. <问题。建议默认值：如果用户难以判断，建议采用...>
```

## 资源文件

- 需求状态文档模板：`resources/templates/requirement-state-template.md`
- 讨论摘要模板：`resources/templates/discussion-summary-template.md`
- 孵化准入检查清单：`resources/checklists/incubation-readiness-checklist.md`
- 使用者提示示例：`resources/usage-examples.md`
