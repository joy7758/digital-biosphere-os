# DBOS Developer Concepts v0.1（DBOS 开发者核心概念 v0.1）

状态：`DOCUMENTED_FOR_LOCAL_PREVIEW`（本地预览文档化）

DBOS v0.1 使用五类 Core Object Representation（核心对象表示）。它们都是调用方声明的不可变数据结构；对象存在不代表其引用的现实主体、行为或事实已经存在。

## Five Core Objects（五类核心对象）

| 对象 | 回答的问题 | 核心引用 | 明确不产生 |
|---|---|---|---|
| Entity Object（实体对象） | “声明的是谁？” | Owner、Source、Lifecycle | 实体激活、Agent、Permission |
| Capability Object（能力对象） | “声明的能力边界是什么？” | Entity、Scope、Constraints | Capability Grant、Permission、执行权 |
| Execution Object（执行对象） | “一次外部执行如何被记录？” | Entity、Task、Context、Input、Output | 任务执行、Execution Result（执行结果）、Runtime |
| Evidence Reference Object（证据引用对象） | “证据材料在哪里？” | Execution、Evidence Source | Truth（真相结论）、证据升级、历史修改 |
| Verification Object（验证对象） | “谁以什么类型记录了验证状态？” | Target、Verification Type、Status | 事实认证、授权、Permission |

## Shared Contract（公共契约）

五类对象都包含：

```text
object_id
object_type
version
source
status
created_at
updated_at
limitations
```

类型专属 ID 必须与 `object_id` 相等。SDK 不生成 ID，不把 `null` 换成当前时间，也不把 `UNKNOWN` 推断为更高状态。

## Relationship Model（关系模型）

```text
Entity Object（实体对象）
  <- Capability Object（能力对象）声明边界
  <- Execution Object（执行对象）引用外部执行记录
       <- Evidence Reference Object（证据引用对象）指向材料
            <- Verification Object（验证对象）表达限定验证状态
```

箭头表示引用关系，不表示 Authority（权力）、信任传递或权限继承。每个对象都必须独立满足自己的模式和证据要求。

## Creation, Serialization, Validation（创建、序列化、验证）

这三个动作必须分开理解：

1. Creation（创建表示）：调用方提供字段，SDK 创建内存数据结构；
2. Serialization（序列化）：把数据结构复制为 `dict` 或 JSON；
3. Validation（验证）：Validator 检查机器模式、ID 一致性、引用形状和禁止的治理效果。

任何一步都不会自动执行下一步，也不会创建现实实体。

## Result Boundary（结果边界）

Validation Result（验证结果）描述本次本地检查。它不是 Verification Object，也不构成独立 Verification（事实验证）：

```text
STRUCTURAL_VALIDATION_NE_FACT_VERIFICATION=true
OBJECT_NE_AUTHORITY=true
CAPABILITY_NE_PERMISSION=true
REFERENCE_NE_TRUTH=true
```

可运行入口见 [`developer-quickstart.md`](developer-quickstart.md)。字段级规范见仓库根目录的五份 `*-object-contract.md` 与 `schemas/*-object-schema.yaml`。
