# DBOS Execution Object Contract v0.1（DBOS 执行对象契约 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

对象实例状态：`NOT_CREATED`

## 1. Definition（定义）

Execution Object（执行对象）是对一次外部执行声明或惰性执行记录的受范围投影。它连接 Entity、Task、Context、Input 和可选 Output 引用，不启动模型、工具、进程或 Runtime。

```text
EXECUTION_OBJECT_NE_EXECUTION_COMMAND=true
EXECUTION_OBJECT_NE_EXECUTION_RESULT=true
EXECUTION_OBJECT_NE_RUNTIME=true
```

## 2. Complete Field Set（完整字段集合）

Execution Object 必须包含公共字段：

`object_id`、`object_type`、`version`、`source`、`status`、`created_at`、`updated_at`、`limitations`

以及以下专属字段：

`execution_id`、`entity_reference`、`task_reference`、`context_reference`、`input_reference`、`output_reference`

`status` 使用公共字段，并承担本对象的执行记录状态语义。

## 3. Field Semantics（字段语义）

| 字段 | 语义 | 约束 |
|---|---|---|
| `object_id` | 对象标识 | 必须等于 `execution_id` |
| `object_type` | 核心对象类型 | 必须为 `EXECUTION` |
| `execution_id` | 惰性执行记录 ID | 不证明执行发生 |
| `entity_reference` | 相关 Entity 引用 | 不创建或激活 Entity |
| `task_reference` | 外部任务声明引用 | DBOS 不规划或运行任务 |
| `context_reference` | 既有 Execution Context 引用 | 不创建 Runtime 或 Context |
| `input_reference` | 输入或输入快照引用 | 不复制或验证输入正文 |
| `output_reference` | 可选输出引用 | 可以为 `null`；非空不表示结果已验证 |
| `status` | 执行记录状态 | v0.1 只允许 `UNKNOWN/CREATED` |

## 4. Status Boundary（状态边界）

当前 `entity_support/execution_registry.py` 的实现事实只支持 `CREATED`。因此 v0.1 Object Contract 不定义 `RUNNING/SUCCESS/COMPLETED` 等执行结果状态。

- `UNKNOWN`：Source 无法充分确认记录状态；
- `CREATED`：惰性记录已形成，不表示任务已启动。

未来完成、失败、重试或取消语义需要新的契约版本和真实运行证据。

## 5. Validation Rules（验证规则）

必须返回错误的情况：

- `object_id != execution_id`；
- `object_type != EXECUTION`；
- Entity、Task、Context 或 Input 引用缺失；
- `status` 超过 `UNKNOWN/CREATED`；
- `output_reference` 非空就自动声明成功；
- 对象包含模型选择、工具调用命令、调度、重试或 Permission 字段；
- 创建对象时启动 Runtime、进程、模型或工具。

## 6. Explicit Non-effects（明确无效果）

Execution Object 不等于：

- Execution Result（执行结果）；
- 已完成、成功或失败的任务；
- Runtime instance（运行时实例）；
- Agent behavior（智能体行为）；
- Event、Evidence 或 Attestation（证明）；
- Permission 或执行授权。

```text
EXECUTION_RECORD_EFFECT=REFERENCE_ONLY
MODEL_EXECUTION_EFFECT=NONE
TOOL_INVOCATION_EFFECT=NONE
RUNTIME_EFFECT=NONE
PERMISSION_EFFECT=NONE
```
