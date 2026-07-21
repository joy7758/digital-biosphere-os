# DBOS Adapter Object Mapping Model v0.1（DBOS 适配器对象映射模型 v0.1）

状态：`SPECIFICATION_ONLY`

映射实例：`0`

## 1. Mapping Pipeline（映射管线）

```text
External Object（外部对象）
  -> versioned Mapping Profile（版本化映射配置）
  -> explicit field transformation（显式字段转换）
  -> DBOS Object Candidate（DBOS 对象候选表示）
  -> Validator（验证器）
```

映射只产生表示和引用，不创建外部对象、DBOS 规范对象或治理状态。每个输出必须保留外部 ID、来源版本、Adapter 版本、Mapping Profile 版本和已知限制。

## 2. Universal Mapping Rules（通用映射规则）

1. External ID（外部标识）与 DBOS `object_id/entity_id` 是不同身份轴；只能显式关联，不能字符串复制后宣称等价；
2. 外部 Namespace（命名空间）必须保留，禁止裸 ID 自动进入 `dbio`；
3. 一个外部对象映射多个 DBOS 候选时必须分别输出并声明关系，不能合并身份；
4. 多个外部对象映射同一候选时返回 `CONFLICT` 或显式集合，不能按输入顺序覆盖；
5. 未提供或无法证明的值保持 `UNKNOWN/null`；
6. Adapter 不生成时间戳、摘要、Owner、Evidence 或 Verification 结果；
7. 每个候选必须满足对应 Object Contract（对象契约）并通过核心 Validator；
8. Adapter Mapping（适配器映射）不建立 Alias（别名）；Alias 需要独立来源、证据与撤销记录。

## 3. Entity Mapping（实体映射）

允许输入：外部框架中的显式主体、服务、Repository（仓库）或 Artifact（工件）引用。

目标候选：`EntityObject`（实体对象表示）。

必要映射：

| 外部信息 | DBOS 字段 | 规则 |
|---|---|---|
| 外部稳定 ID | `source_reference.reference_id` | 保留外部 Namespace，不冒充规范 Entity ID |
| 外部对象分类 | `entity_type` | 只有证据支持时映射；否则 `UNKNOWN` |
| 责任来源 | `owner_reference` | 必须显式提供，不从账户名或仓库名猜测 |
| 外部状态 | `lifecycle_state` | 使用版本化状态映射；默认 `UNKNOWN/PROPOSED` 上限 |
| 外部来源 | `source` | 保留 Source Owner 与版本 |

禁止从 `Agent` 类名、Role（角色）、Crew 成员、MCP Server 或工具集合自动建立 DBOS `entity_type=agent`。Entity Mapping 只形成候选表示，不登记或激活 Entity。

## 4. Execution Mapping（执行映射）

允许输入：外部框架已经产生的 run、task、callback、tool invocation（工具调用）或结果引用。

目标候选：`ExecutionObject`（执行对象表示）。

规则：

- 只能映射已发生或调用方已声明的外部记录，不能触发执行；
- 必须分别提供 Entity、Task、Context、Input 与 Output 引用；
- 没有输出时保持 `output_reference=null`；
- 外部 `success=true` 不能让 `ExecutionObject` 成为 Execution Result（执行结果）或 Verification `PASS`；
- Adapter 不启动模型、Tool、Agent、Thread（任务）或 Runtime。

## 5. Evidence Mapping（证据映射）

允许输入：外部 Artifact location（工件位置）、event output（事件输出）、trace reference（轨迹引用）或其他可归因材料引用。

目标候选：`EvidenceReferenceObject`（证据引用对象表示）。

规则：

- Adapter 只引用材料，不复制、删除或修改 Evidence Truth（证据事实）；
- 必须保留原始 Source、Execution Reference（执行引用）与限制；
- 没有完整性证明时 `integrity_status` 保持 `UNKNOWN/PENDING`；
- 文件存在、回调完成或摘要字段存在不表示证据已验证；
- Adapter 不提升 E 等级，不生成缺失摘要，也不把外部日志写入规范证据库。

## 6. Verification Mapping（验证映射）

允许输入：外部系统声明的 check、test、review 或 validation record（检查、测试、复核或验证记录）引用。

目标候选：`VerificationObject`（验证对象表示）。

规则：

- 必须声明目标、方法类型、来源与限制；
- 外部 `passed=true` 不能直接成为 DBOS `verification_status=PASS`；
- 无法解析完整验证记录时保持 `UNKNOWN/PENDING`；
- Adapter 自测、框架测试和 DBOS 结构 Validation（结构验证）不是 Independent Verification（独立事实验证）；
- Verification Mapping 不产生 Review Approval（复核批准）、Certification（认证）、Capability Grant 或 Permission。

## 7. Capability Mapping Exclusion（能力映射排除）

v0.1 通用 Adapter 不从 Tool、method、plugin、role 或配置自动生成 `CapabilityObject`。外部可调用性只可成为未来 Capability Claim（能力声明）的候选来源，必须经过单独提案、证据和复核流程。

```text
TOOL_VISIBILITY_NE_VERIFIED_CAPABILITY=true
METHOD_EXISTENCE_NE_CAPABILITY_GRANT=true
CAPABILITY_MAPPING_DEFAULT=NOT_ALLOWED
```

## 8. Mapping Report（映射报告）

未来实现必须为每次转换输出可检查报告，至少说明：

```text
adapter_id
adapter_version
mapping_profile_version
external_system_version
input_reference
candidate_object_references
unmapped_fields
conflicts
limitations
validation_result_references
```

该字段集合只是未来契约方向，本阶段不创建 Schema、报告实例或存储。Mapping Report 不产生 Authority（权力）、Trust（信任）或 Compatibility（兼容性）结论。

## 9. Current State（当前状态）

```text
ENTITY_MAPPING_INSTANCE_COUNT=0
EXECUTION_MAPPING_INSTANCE_COUNT=0
EVIDENCE_MAPPING_INSTANCE_COUNT=0
VERIFICATION_MAPPING_INSTANCE_COUNT=0
CAPABILITY_MAPPING_INSTANCE_COUNT=0
MAPPING_REPORT_COUNT=0
```
