# 使用示例

本文件只作为使用者提示，不是需求输出模板。

## 示例一：后端和前端需求规格化

```text
使用 requirement-specification skill，基于 docs/ai/requirements/query-history/requirement-state.md 编写 requirement-spec.md。
技术栈 profile 使用 backend-python-fastapi 和 frontend-vue3。
输出到 docs/ai/requirements/query-history/requirement-spec.md。
不要写业务代码。
```

## 示例二：只做后端需求规格化

```text
使用 requirement-specification skill，基于 docs/ai/requirements/metadata-query/requirement-state.md 编写 requirement-spec.md。
技术栈 profile 使用 backend-python-fastapi。
重点明确 API、service、dao、数据库和日志规则影响。
不要写业务代码。
```

## 示例三：检查规格是否可进入开发

```text
使用 requirement-specification skill，检查 docs/ai/requirements/query-history/requirement-spec.md 是否满足进入开发实现阶段的条件。
请使用 specification-readiness-checklist.md。
如果存在 P0 问题或验收标准不可测试，输出阻塞原因。
不要写业务代码。
```

## 示例四：Java 后端项目规格化

```text
使用 requirement-specification skill，基于 docs/ai/requirements/order-export/requirement-state.md 编写 requirement-spec.md。
技术栈 profile 使用 backend-java-springboot-mybatis-plus。
重点明确 Controller、Service、Mapper、事务边界和数据表影响。
不要写业务代码。
```

## 示例五：只做前端需求规格化
```text
使用 [$requirement-specification](D:\\PycharmProjects\\db-agent\\.agents\\skills\\requirement-specification\\SKILL.md) ，基于 [requirement-state.md](docs/ai/requirements/element-plus-ui-refresh/requirement-state.md) 编写 requirement-spec.md。 
技术栈 profile 使用 frontend-vue3。
 
不要写业务代码。
```