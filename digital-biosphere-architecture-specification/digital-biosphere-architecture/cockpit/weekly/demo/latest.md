# DBA 每周驾驶舱

- 快照编号：`DBA-WEEKLY-2026-W35`
- 观察时间：`2026-08-29T00:30:00+08:00`
- 总体状态：`PASS_WITH_NOT_ASSESSED`
- 视图边界：只读观察；不构成项目真值、执行授权或发布授权。
- 来源模式：`RETAINED_SNAPSHOT`
- 发现可用性：`AVAILABLE`

## 本周一句话

本周共纳入5个项目视图：2个稳定，1个需关注，1个盲区，1个尚未评估。共收集6项信号，其中1项已通过证据准入，5项被拒绝或待确认；有2项需要人工决定。

## 本周需要你决定

### 是否启动依赖安全专项复核

历史记录2个，本周扫描4个，当前存在状态冲突。

### 是否授权刷新 TITMAC Scout 的只读状态

当前状态来源缺少足够新鲜度；刷新仍需单独、只读、限定范围的人工授权。

## 项目状态

### DBA 驾驶舱

- 状态：`ATTENTION`（依赖审计状态待复核）
- 来源标签：`RETAINED_SNAPSHOT`
- 说明：本周实时扫描报告4个高危依赖包，而驾驶舱历史权威记录仍为2个。两者尚未对齐，需要核对锁文件、扫描范围和是否进入实际运行环境。
- 注意：候选包：image-size, js-yaml, nanoid, vinext；可利用性尚未评估。

### 红岩公文

- 状态：`STABLE`（当前主线稳定）
- 来源标签：`RETAINED_SNAPSHOT`
- 说明：现有权威快照可读取，本周驾驶舱未修改红岩项目。
- 注意：该视图不替代红岩专用对话中的项目判断。

### TITMAS 支撑层

- 状态：`NOT_ASSESSED`（升级状态未评估）
- 来源标签：`RETAINED_SNAPSHOT`
- 说明：组件状态来源已过期，不能转化为本周升级建议。
- 注意：需要新的只读证据后再评估。

### 数字细胞演示

- 状态：`STABLE`（参考演示稳定）
- 来源标签：`RETAINED_SNAPSHOT`
- 说明：冻结参考演示及其既有验证记录可读取；本周未授权新增执行。
- 注意：该状态不构成生产就绪或认证。

### TITMAC 侦察

- 状态：`BLIND_SPOT`（检查盲区）
- 来源标签：`RETAINED_SNAPSHOT`
- 说明：当前只读状态来源缺少足够新鲜度，不能据此判定项目正常或异常。
- 注意：如需刷新，必须获得单独只读授权。

## 本周发现信号

共记录 6 项信号；已准入 1 项；被拒绝或待确认 5 项。

首次快照，尚不能判断这些信号是否相对于上周新增。

### OpenBao（机密与密钥管理组件）候选

- 准入标签：待人工确认候选
- 观察状态：`DISCOVERED`
- 说明：OpenBao（机密与密钥管理组件）仍是待确认候选；应先刷新当前版本与安全事实。
- 来源：`project-discovery:public-adjacent-candidate`

### 依赖安全状态出现待复核冲突

- 准入标签：已通过证据准入
- 观察状态：`CONFLICT_CANDIDATE`
- 说明：本周实时扫描报告4个高危依赖包，历史权威记录仍为2个；候选包为image-size, js-yaml, nanoid, vinext。
- 来源：`cockpit/weekly/inputs/live-dependency-audit-candidate-2026-08-29.json`

### TITMAS 组件矩阵状态待刷新

- 准入标签：未通过准入或来源过期
- 观察状态：`STALE`
- 说明：现有组件矩阵不能自动获得本周当前状态权威。
- 来源：`titmas-component-adoption-matrix-v1.0.json`

### TITMAC Scout 当前只读状态待刷新

- 准入标签：未通过准入或来源过期
- 观察状态：`UNKNOWN`
- 说明：现有投影没有提供足够新鲜度，不能推断当前状态。
- 来源：`cockpit/projections/titmac-scout.json`

### 红岩公文与 DBA 驾驶舱的声明关系

- 准入标签：待人工确认候选
- 观察状态：`DECLARED`
- 说明：这是已声明的项目关系，不是新漏洞，也不授予跨项目控制权。
- 来源：`cockpit/source-registry.json`

### TITMAS 支撑层与数字细胞演示的声明关系

- 准入标签：待人工确认候选
- 观察状态：`DECLARED`
- 说明：这是引用关系，不代表部署、认证、运行绑定或新的安全事实。
- 来源：`cockpit/source-registry.json`

## 检查盲区

### TITMAC Scout 的只读状态尚未刷新 · `NOT_ASSESSED`

- 状态：`NOT_ASSESSED`
- 影响：当前周检不能确认其最新检查、版本与运行状态。

### 依赖漏洞的远端运行绑定未观察 · `NOT_ASSESSED`

- 状态：`NOT_ASSESSED`
- 影响：当前只能确认扫描候选与历史记录冲突，不能确认这些包是否进入实际远端运行路径。

## 技术证据

- 机器总体状态：`PASS_WITH_NOT_ASSESSED`
- 原始观察时间：`2026-08-29T00:30:00+08:00`
- 逻辑 Cell 数量：12
- 依赖审计状态：`CONFLICT_REQUIRES_REVIEW`
- 实时来源成功数：0
- 来源未评估数：0
- 上轮实时制品已读取：`False`

固定问题仅查询当前快照，不访问外部服务，也不产生执行命令。
