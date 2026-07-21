# DBOS Minimal Object SDK Skeleton v0.1（DBOS 最小对象软件开发工具包骨架 v0.1）

状态：`LOCAL_EDITABLE_INSTALL_PREVIEW`（本地可编辑安装预览）

发布状态：`LOCAL_PROJECT_METADATA_NOT_PUBLISHED`（本地项目元数据已定义、未发布）

本目录提供纯数据 Object（对象）、确定性 Serialization（序列化）和现有 Validator（验证器）的显式桥接。`pyproject.toml` 与 `dbos` facade（门面）允许开发者从当前 checkout 执行 `python3 -m pip install -e .` 后构造、导出并检查 DBOS v0.1 对象表示，但不创建对象所描述的现实主体或治理效果。

## Current Capabilities（当前能力）

- Create Object Representation（创建对象表示）：`EntityObject`、`CapabilityObject`、`ExecutionObject`、`EvidenceReferenceObject`、`VerificationObject`；
- Serialize Object（序列化对象）：`object_to_dict()` 与 `object_to_json()`；
- Validate Object（验证对象）：`sdk.validation.validate_object()` 调用唯一的本地 `validator.validate_object()`，返回九字段 `ValidationResult`（验证结果）。

对象使用 Frozen Dataclass（冻结数据类）。嵌套映射和序列也被复制为不可变表示，序列化返回与原对象分离的新副本。构造器不会生成 ID（标识符）、时间戳、状态、证据或验证结果。

## Local Example（本地示例）

```python
from sdk import EntityObject, object_to_json, validate_object

entity_id = "dbio://repository/example/v0.1"
source_id = "registry/entities.yaml"

source = {
    "namespace": "dbio",
    "source_id": source_id,
    "version": "v0.1",
    "status": "DECLARED",
}

reference = {
    "reference_id": entity_id,
    "reference_type": "ENTITY",
    "namespace": "dbio",
    "version": "v0.1",
    "source": source_id,
    "status": "DECLARED",
}

target = EntityObject(
    object_id=entity_id,
    entity_id=entity_id,
    entity_type="repository",
    owner_reference={**reference, "reference_id": "dbio://entity/example-owner/v0.1"},
    lifecycle_state="PROPOSED",
    source_reference=reference,
    source=source,
    status="DECLARED",
    limitations=("Local declaration only.",),
)

result = validate_object(target)
serialized = object_to_json(target)
```

`result.result == PASS` 只表示对象表示通过本地结构与治理约束检查。它不证明身份、来源、生命周期或内容为真，也不产生授权或权限。

## Validation Flow（验证流程）

```text
Caller-supplied declarations（调用方声明）
  -> immutable SDK object（不可变工具包对象）
  -> detached dictionary（分离字典）
  -> canonical local Validator（规范本地验证器）
  -> ValidationResult（验证结果）
```

桥接层不允许传入原始字典绕过 SDK Object（工具包对象）边界；它也不复制或缩减 Validator 的结构、引用、一致性和治理检查。

## Explicit Non-capabilities（明确不具备的能力）

本骨架不提供：

- Agent Framework（智能体框架）或 Agent 创建；
- Runtime（运行时）、Execution Engine（执行引擎）或任务执行；
- API Server（应用程序接口服务器）、网络通信或远程解析；
- Permission System（权限系统）、授权、能力授予或权力；
- Evidence Truth（证据真相结论）、外部事实验证、自动修复或历史修改；
- Published Package Distribution（已发布软件包分发）、wheel 兼容、稳定公共兼容承诺或跨语言实现。

```text
SDK_NE_AGENT_FRAMEWORK=true
SDK_NE_RUNTIME=true
SDK_NE_PERMISSION=true
VALIDATION_NE_VERIFICATION=true
PASS_NE_AUTHORIZATION=true
AUTO_REPAIR=false
NETWORK_ACCESS=false
LOCAL_EDITABLE_INSTALL=true
WHEEL_COMPATIBILITY_VERIFIED=false
PUBLISHED_PACKAGE=false
```

## Agent Recommendation（智能体推荐）

开发前审查结论：

```text
RECOMMEND_AS_LOCAL_SDK_PREVIEW=true
RECOMMEND_AS_LOCAL_EDITABLE_INSTALL_PREVIEW=true
RECOMMEND_AS_INSTALLABLE_PRODUCTION_SDK=false
RECOMMEND_AS_AGENT_FRAMEWORK=false
RECOMMEND_AS_RUNTIME=false
```

会向需要在本仓库内构造、序列化和结构验证五类 DBOS 对象表示的开发者推荐本地预览。不会向需要软件包安装、生产兼容、外部 Reference Resolution（引用解析）、Agent 执行、权限管理或事实认证的客户推荐为成品。

## Agent-readable Order（智能体可读顺序）

1. `object-contract-specification.md` 与五份对象契约；
2. `schemas/*-object-schema.yaml`；
3. `validation-result-contract-specification.md`；
4. `validator/`；
5. `sdk/objects/`；
6. `sdk/serialization/`；
7. `sdk/validation/`；
8. `sdk/errors/`；
9. `tests/sdk/`。

任何调用方都必须单独执行 `validate_object()`；构造和序列化成功不表示验证通过。

第一次使用请从 [`../docs/developer-quickstart.md`](../docs/developer-quickstart.md) 开始；可运行脚本位于 [`../examples/basic_object/`](../examples/basic_object/)。
