# 需求孵化准入检查清单

用于判断一个需求是否可以从需求孵化阶段进入需求规格化阶段。

## 文档完整性

- [ ] 已创建独立需求目录：`docs/ai/requirements/<requirement-slug>/`
- [ ] 已建议创建或更新 `requirement-state.md`
- [ ] `requirement-state.md` 包含需求名称
- [ ] `requirement-state.md` 包含当前需求一句话描述
- [ ] `requirement-state.md` 包含原始诉求
- [ ] `requirement-state.md` 包含业务目标
- [ ] `requirement-state.md` 包含目标用户
- [ ] `requirement-state.md` 包含使用场景
- [ ] `requirement-state.md` 包含核心业务对象
- [ ] `requirement-state.md` 包含已确认功能范围
- [ ] `requirement-state.md` 包含明确不做范围
- [ ] `requirement-state.md` 包含关键业务规则
- [ ] `requirement-state.md` 包含待澄清问题，并按 P0、P1、P2 分类
- [ ] `requirement-state.md` 包含已废弃想法
- [ ] `requirement-state.md` 包含决策记录
- [ ] `requirement-state.md` 包含当前需求成熟度
- [ ] `requirement-state.md` 包含是否允许进入需求规格化

## 内容成熟度

- [ ] 当前需求不是只有模糊想法或单句方向性诉求
- [ ] 业务目标清楚
- [ ] 目标用户清楚
- [ ] 至少一个主要使用场景清楚
- [ ] 核心业务对象清楚
- [ ] 已确认功能范围和明确不做范围可以区分
- [ ] 关键业务规则已有初步沉淀
- [ ] 历史对话与最新 `requirement-state.md` 无未解决冲突
- [ ] 当前不存在 P0 待澄清问题

## P0 阻断规则

只要满足以下任一条件，就必须判定为存在 P0 问题，不允许进入需求规格化阶段：

- 需求仍停留在模糊想法、业务痛点或方向性诉求，尚未形成清晰需求状态。
- 需求名称或一句话描述无法确定。
- 业务目标无法判断。
- 目标用户无法判断。
- 使用场景无法判断。
- 核心业务对象无法判断。
- 已确认功能范围和明确不做范围无法区分。
- 关键业务规则完全未知。
- 最新 `requirement-state.md` 与历史对话存在冲突但没有决策记录。

## 问题提问规则

- 每轮最多向用户提出 3 到 5 个关键问题。
- 优先提出 P0 问题。
- 对用户难以判断的问题，必须给出建议默认值。
- 建议默认值不能写成已确认事实，除非用户明确接受。

## 输出结论格式

存在 P0 时：

```markdown
## 本轮需求沉淀

### 当前成熟度

- <想法阶段 / 初步成形>

### 是否允许进入需求规格化

- 否
- 原因：当前仍存在 P0 待澄清问题。

### P0 待澄清问题

1. <问题。建议默认值：<默认建议>>
```

不存在 P0 时：

```markdown
## 本轮需求沉淀

### 当前成熟度

- 可规格化

### 是否允许进入需求规格化

- 是
- 原因：当前不存在 P0 待澄清问题，需求目标、目标用户、使用场景、核心业务对象和范围边界已基本明确。

### 下一步

- 可以进入需求规格化阶段，基于 `requirement-state.md` 输出 `requirement-spec.md`。
```
