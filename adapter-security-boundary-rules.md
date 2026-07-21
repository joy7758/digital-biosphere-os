# DBOS Adapter Security Boundary Rules v0.1（DBOS 适配器安全边界规则 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

执行效果：`NONE`

## 1. Namespace Isolation（命名空间隔离）

- Adapter 自身引用必须使用独立 `extension:<adapter-id>` Namespace（命名空间）；
- 外部系统对象必须保留其 `external:<authority-id>` Namespace；
- Adapter 不得创建、签发或返回自称由其拥有的 `dbio` 规范身份；
- 裸 ID、类名、文件路径和当前工作目录不能作为 Namespace 证据；
- External → DBOS 映射只产生候选关系，不转移 Owner（所有者）或 Architecture Authority（架构权力）；
- Namespace 冲突必须返回 `CONFLICT/AMBIGUOUS`，不能覆盖或按加载顺序选择。

## 2. Reference Restrictions（引用限制）

- 所有引用必须包含显式类型、Namespace、版本、Source 和状态；
- 默认不跟随 Alias（别名）、symlink（符号链接）、mirror（镜像）或 successor（后继）；
- Reference lookup（引用查找）不产生 Truth、Trust、Capability、Permission 或 Activation；
- Adapter 不能把不可解析引用改写为本地路径后声称 `RESOLVED`；
- Adapter 不能修改 `registry/entities.yaml`、规范 Evidence 或历史 Verification；
- 输出引用必须保留调用方输入与映射来源，禁止丢弃 provenance（来源链）。

## 3. Version Compatibility（版本兼容）

每次映射必须同时固定四个版本轴：

```text
adapter_version
mapping_profile_version
external_system_version
dbos_object_contract_version
```

规则：

- 禁止把 `latest/main/current` 当作精确兼容版本；
- 缺少任一必需版本时保持 `UNKNOWN`；
- 不支持的外部或 DBOS 版本返回 `VERSION_MISMATCH`；
- 兼容声明必须限定外部版本、DBOS 版本、测试环境和映射范围；
- 新版本不得覆盖旧映射报告、失败记录或限制；
- Breaking Change（破坏性变更）需要新的 Mapping Profile 与迁移说明。

## 4. Failure Handling（失败处理）

Adapter 必须：

- fail closed（失败关闭）；
- 返回结构化、可解释错误；
- 保留原输入引用、失败步骤和未映射字段；
- 禁止 silent drop（静默丢弃）、默认成功、自动补字段或无记录重试；
- 禁止自动修复后伪装成首次 `PASS`；
- 在部分输入可映射时仍不得产生部分规范登记；
- Validator 返回非 `PASS` 时原样停止，不改变结果优先级。

## 5. Validator Integrity（验证器完整性）

第三方 Adapter 禁止：

- monkey patch（运行时替换）或包装核心 Validator 以删除规则；
- 提供同名弱化 Validator 并称为 DBOS 官方结果；
- 缓存旧 `PASS` 代替当前输入验证；
- 忽略 Schema digest（模式摘要）、版本或错误；
- 把 Adapter unit test（单元测试）当作 DBOS Validation Result（验证结果）；
- 从 Validator `PASS` 推导 Registration、Authorization、Permission、Verification 或 Compatibility。

```text
ADAPTER_CAN_OVERRIDE_VALIDATOR=false
ADAPTER_CAN_MINT_VALIDATION_RESULT=false
VALIDATOR_RULE_REDUCTION_FORBIDDEN=true
```

## 6. Evidence Integrity（证据完整性）

- Adapter 只输出 Evidence Reference（证据引用），不成为规范 Evidence Store（证据存储）；
- 证据正文、摘要、时间戳和签名缺失时必须保持缺失，禁止生成替代值；
- Adapter 转换不能改变历史 hash（摘要）、来源、状态或限制；
- 外部 Evidence 更新必须形成新版本或追加记录，不能覆盖旧记录；
- Adapter 供应商、付费状态或框架品牌不提高 E/V 等级。

## 7. Supply-chain and Privacy Boundary（供应链与隐私边界）

未来第三方 Adapter 必须：

- 独立声明 Repository（仓库）、Owner、License（许可证）、依赖范围和安全联系人；
- 使用最小权限，不读取未声明文件、凭据、环境变量或个人信息；
- 默认不访问网络，不发送 Evidence 正文或输入输出；
- 网络、文件和凭据访问必须由调用方另行显式授权并可审计；
- 支持撤销、受影响版本识别和安全事件通知；
- 被撤销或不可用时，不得阻止访问已有 DBOS 规范身份和历史证据。

## 8. Authority Boundary（权力边界）

Adapter Owner、Maintainer（维护者）、Vendor（供应商）或 Sponsor（资助者）均不因其角色获得：

- DBOS Architecture Authority；
- Entity、Capability、Evidence 或 Verification 的所有权；
- Permission 决策权；
- Validator 规则修改权；
- 外部框架治理权。

```text
ADAPTER_AUTHORITY_EFFECT=NONE
ADAPTER_PERMISSION_EFFECT=NONE
ADAPTER_EVIDENCE_MUTATION_EFFECT=NONE
ADAPTER_RUNTIME_EFFECT=NONE
ADAPTER_EVOLUTION_EFFECT=NONE
```

## 9. Required Negative Tests for Future Implementations（未来实现必须具备的负向测试）

未来每个具体 Adapter 至少必须证明它拒绝：

1. 使用 Adapter Namespace 冒充 `dbio`；
2. 从 Tool 或 role 自动创建 Agent/Capability；
3. 从外部 `passed=true` 自动生成 DBOS Verification `PASS`；
4. 携带 Permission 或 Authority 效果的候选对象；
5. 修改、覆盖或删除 Evidence；
6. 跳过或弱化核心 Validator；
7. 不支持版本被自动升级；
8. 未授权网络、凭据或文件访问。

本阶段只定义这些要求，不创建测试代码或具体 Adapter。
