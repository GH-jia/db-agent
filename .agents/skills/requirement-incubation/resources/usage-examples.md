# 使用示例

本文件只作为使用者提示，不是需求输出模板。

## 示例一：新需求孵化

```text
使用 requirement-incubation skill，围绕“给数据库 agent 增加查询历史记录功能”进行需求孵化。
输出到 docs/ai/requirements/query-history/requirement-state.md。
如果存在 P0 问题，不要进入规格化阶段。
不要写业务代码。
```

## 示例二：已有需求继续澄清

```text
使用 requirement-incubation skill，继续完善 docs/ai/requirements/query-history/requirement-state.md。
根据本轮讨论更新已确认事实、范围边界和待澄清问题。
如果历史对话与最新需求文档冲突，以最新需求文档为准。
不要写业务代码。
```

## 示例三：只判断是否可进入下一阶段

```text
使用 requirement-incubation skill，检查 docs/ai/requirements/query-history/requirement-state.md 是否满足进入需求规格化阶段的条件。
请使用 incubation-readiness-checklist.md。
如果存在 P0 问题，输出阻塞原因和必须回答的问题。
不要写业务代码。
```
