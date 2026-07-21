# DBOS Developer Quick Start v0.1（DBOS 开发者快速入门 v0.1）

状态：`RUNNABLE_LOCAL_PREVIEW`（可运行本地预览）

目标用时：`30 minutes`（30 分钟）

外部可用性研究：`NOT_YET_PERFORMED`（尚未进行）

> DBOS helps AI agents become verifiable digital entities.
>
> DBOS 帮助 AI Agent（人工智能智能体）成为可验证的数字实体。

这里的“帮助”是提供统一对象格式、结构检查和可解释结果，不表示 DBOS 自动创建、运行或验证 Agent。

## 1. What is DBOS（什么是 DBOS）— 0–5 分钟

DBOS 是 Trusted Digital Entity Infrastructure（可信数字实体基础设施）。它让开发者用统一结构描述：

- 一个数字实体是谁；
- 声明了什么能力边界；
- 一次执行如何被引用；
- 证据在哪里；
- 验证记录表达了什么。

当前 v0.1 的本地工具可以：

1. 创建五类 DBOS Object Representation（DBOS 对象表示）；
2. 转换为 `dict` 或 JSON（JavaScript 对象表示法）；
3. 使用本地 Validator（验证器）检查结构和治理边界；
4. 返回统一的 Validation Result（验证结果）。

## 2. What DBOS is not（DBOS 不是什么）

DBOS 不是：

- Foundation Model（基础模型）；
- Agent Framework（智能体框架）；
- Runtime（运行时）或 Execution Engine（执行引擎）；
- Permission System（权限系统）；
- API Server（应用程序接口服务器）。

DBOS 不负责推理、规划、工具调用、任务调度或模型托管。你的应用继续拥有这些行为；DBOS 只提供可检查的基础设施对象与结果语言。

## 3. Prepare the Local Checkout（准备本地检出）— 5–10 分钟

当前 SDK（软件开发工具包）支持从仓库 checkout（检出）进行 local editable install（本地可编辑安装），但不是已发布的软件包，也没有 wheel（分发包）兼容承诺。建议使用隔离环境，并从 DBOS 仓库根目录运行：

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

安装后可运行不依赖路径注入的 facade（门面）示例：

```bash
python3 examples/basic_object/installed_editable_quickstart.py
```

依赖只用于本地 JSON Schema Validation（JSON 模式验证）。`-e .` 表示代码仍来自当前 checkout，不表示包已发布。本快速入门不启动服务、不访问远程 API，也不创建运行时。

## 4. Create a DBOS Object（创建 DBOS 对象表示）— 10–15 分钟

运行：

```bash
python3 examples/basic_object/create_entity_object.py
```

该脚本调用 [`../examples/basic_object/create_entity_object.py`](../examples/basic_object/create_entity_object.py)，创建一个只存在于内存中的 Synthetic Entity Object（合成实体对象表示），然后把它打印为 JSON。

示例使用 `entity_type=repository`，而不是声明真实 Agent 身份。完整对象除了公共字段外，还必须提供 Owner Reference（所有者引用）、Lifecycle State（生命周期状态）和 Source Reference（来源引用）。

最重要的公共字段是：

| 字段 | 含义 | 不代表 |
|---|---|---|
| `object_id` | 对象的稳定标识 | 身份已经认证 |
| `object_type` | 五类核心对象之一 | 对象对应的主体已经创建 |
| `version` | 对象契约版本 | 业务实体版本或模式版本 |
| `source` | 声明来自哪里 | 来源内容一定真实 |
| `status` | 记录当前声明状态 | 生命周期自动变化 |
| `limitations` | 已知限制 | 限制已经被外部复核 |

输出对象包含明确限制：它不是登记记录，不创建真实 Entity（实体），也不授予权限。

## 5. Validate the Object（验证对象表示）— 15–20 分钟

运行：

```bash
python3 examples/basic_object/validate_object.py
```

流程是：

```text
Synthetic declarations（合成声明）
  -> EntityObject（实体对象表示）
  -> detached dictionary（分离字典）
  -> local Validator（本地验证器）
  -> ValidationResult（验证结果）
```

预期输出包含九个字段，并且：

```json
{
  "result": "PASS",
  "validation_id": null,
  "timestamp": null
}
```

`validation_id=null` 和 `timestamp=null` 是诚实状态：本地调用没有持久化验证登记，也不会补造 ID 或执行时间。

## 6. Read the Validation Result（理解验证结果）— 20–25 分钟

| 结果 | 含义 | 开发者动作 |
|---|---|---|
| `PASS` | 本地结构与治理规则通过 | 继续保留限制；不要声称获得授权 |
| `FAIL` | 存在明确结构或规则违反 | 修改调用方输入后重新检查；不改写历史结果 |
| `UNKNOWN` | 缺少本地无法确认的信息 | 保持未知并补充真实来源 |
| `CONFLICT` | ID、来源或选择的模式相互冲突 | 解决冲突，不选择默认成功 |
| `VERSION_MISMATCH` | 对象版本不受当前验证器支持 | 使用兼容版本或完成显式迁移 |

最重要的边界：

```text
PASS_NE_TRUTH=true
PASS_NE_AUTHORIZATION=true
VALIDATION_NE_PERMISSION=true
VALIDATION_NE_EXECUTION=true
```

## 7. Run the Negative Examples（运行负向示例）— 25–30 分钟

运行：

```bash
python3 examples/basic_object/negative/validate_negative_cases.py
```

脚本展示三种失败关闭情况：

1. Capability Object（能力对象）携带禁止的 `permission` 字段：`FAIL`；
2. Entity Object 携带未知顶层字段：`FAIL`；
3. 对象使用不兼容版本 `v9.9`：`VERSION_MISMATCH`。

脚本退出码为 `0` 表示三种错误都被按预期拒绝，不表示这些错误对象已经生效。

## 8. Completion Check（完成检查）

完成本快速入门后，你应该能够回答：

- DBOS 管理的是对象、引用与验证边界，不是 Agent 行为；
- 创建 Object Representation 不等于创建真实 Entity；
- 序列化成功不等于验证通过；
- Validation `PASS` 不产生 Permission；
- `UNKNOWN` 必须保持未知，直到存在可归因材料。

运行仓库级测试入口：

```bash
python3 tools/run_tests.py
```

该入口逐个运行所有 `tests/*` 目录，并在没有发现测试时失败关闭，避免把 `Ran 0 tests` 误读为通过。它只运行本地测试，不创建 Agent、Runtime、Permission、Evidence 或治理状态。

## 9. Next Developer Steps（开发者下一步）

- 运行 [`../examples/multi_agent_trust_demo/`](../examples/multi_agent_trust_demo/) 的三角色确定性可信演示：`python3 -m examples.multi_agent_trust_demo.run_demo`；
- 如果本地也有兼容 SAEE checkout，按 Demo README 的命令运行 DBOS output / SAEE input read-only conformance（输出／输入只读符合性）测试；
- 阅读 [`developer-concepts.md`](developer-concepts.md)，理解五类对象如何连接；
- 阅读 [`integration-boundary.md`](integration-boundary.md)，了解未来框架 Adapter（适配器）的责任边界；
- 阅读 [`../sdk/README.md`](../sdk/README.md)，查看本地 SDK 的全部限制；
- 阅读 [`../validation-result-contract-specification.md`](../validation-result-contract-specification.md)，了解完整结果契约。

下一阶段可以设计 Reference Implementation（参考实现），但必须使用真实、受控、明确授权的外部项目，并另行建立证据；本快速入门本身不是外部集成证明。当前 `pyproject.toml` 只支持本地 Developer Preview 安装，不构成 PyPI、wheel、稳定 API 或生产兼容声明。
