# 需求规格化就绪检查清单

用于判断 `requirement-spec.md` 是否可以形成冻结版，并进入开发实现阶段。

## 输入检查

- [ ] 已优先读取 `docs/ai/requirements/<requirement-slug>/requirement-state.md`
- [ ] 已读取 `docs/ai/project-context.md`，如果存在
- [ ] 已确认 `requirement-state.md` 是否存在
- [ ] 已确认 `requirement-state.md` 是否存在 P0 问题
- [ ] 已按项目技术栈选择 tech-profile，或明确标记“技术栈未知”

## 文档完整性检查

- [ ] `requirement-spec.md` 包含需求背景
- [ ] `requirement-spec.md` 包含业务目标
- [ ] `requirement-spec.md` 包含用户角色
- [ ] `requirement-spec.md` 包含本次实现范围
- [ ] `requirement-spec.md` 包含非本次范围
- [ ] `requirement-spec.md` 包含功能清单
- [ ] `requirement-spec.md` 包含业务流程
- [ ] `requirement-spec.md` 包含业务规则
- [ ] `requirement-spec.md` 包含数据需求
- [ ] `requirement-spec.md` 包含接口需求
- [ ] `requirement-spec.md` 包含权限要求
- [ ] `requirement-spec.md` 包含异常场景
- [ ] `requirement-spec.md` 包含兼容性要求
- [ ] `requirement-spec.md` 包含验收标准
- [ ] `requirement-spec.md` 包含后续扩展项
- [ ] `requirement-spec.md` 包含版本冻结说明

## 验收标准检查

- [ ] 验收标准使用表格形式
- [ ] 每条验收标准有编号
- [ ] 每条验收标准包含场景
- [ ] 每条验收标准包含前置条件
- [ ] 每条验收标准包含操作
- [ ] 每条验收标准包含期望结果
- [ ] 每条验收标准包含优先级
- [ ] 每条验收标准都可验证
- [ ] 不存在“体验良好”“性能更好”“页面正常”等不可验证表达

## 范围控制检查

- [ ] 本次实现范围来自 `requirement-state.md` 或用户明确确认
- [ ] 非本次范围已保留
- [ ] 没有擅自扩展需求范围
- [ ] 后续扩展项没有混入本次实现范围

## 阻断规则

满足以下任一条件时，不允许生成冻结版 `requirement-spec.md`：

- 找不到 `requirement-state.md`，且用户未明确允许生成“未冻结草案”。
- `requirement-state.md` 中仍存在 P0 问题。
- 需求规格中仍存在 P0 规格缺口。
- 本次实现范围无法判断。
- 非本次范围缺失，导致范围边界不清。
- 验收标准不可验证。
- 数据需求、接口需求或权限要求对本需求是关键内容，但仍为空。
- 技术栈未知，且该信息会影响接口、数据、页面或兼容性要求。
- 规格内容擅自扩大了需求状态文档中的范围。

## 缺口问题规则

- 只提出少量具体问题。
- 问题必须按 P0、P1、P2 管理。
- 优先提出 P0 问题。
- P0 问题必须阻止冻结。
- P1、P2 问题可以进入未冻结草案或可评审草案，但需明确风险。

## 输出结论格式

存在 P0 时：

```markdown
## 规格化结论

- 文档状态：未冻结草案
- 是否允许生成冻结版：否
- 是否允许进入开发实现阶段：否
- 阻塞原因：
  - P0：<问题>
- 下一步：退回需求孵化阶段，先更新 `requirement-state.md`。
```

不存在 P0 且完整时：

```markdown
## 规格化结论

- 文档状态：冻结版
- 是否允许生成冻结版：是
- 是否允许进入开发实现阶段：是
- 依据：需求状态无 P0 问题，规格范围清晰，验收标准可验证，版本冻结说明已记录。
```
