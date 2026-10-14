# DBA Weekly Cockpit v0.1

DBA 周检驾驶舱是张斌本人使用的内部只读观察工具。它先发现信号，再核验来源，最后生成通俗中文页面。页面不是事实源，也不授予项目执行、发布或整改权限。

## 三种明确模式

- `--mode demo`：使用冻结输入，输出确定性演示制品。
- `--mode live-read-only-pilot`：在批准的来源白名单内执行一次实时只读观察。
- `--mode capability-discovery-auto`：只查询批准的公开元数据，完成 AC-0 发现、身份解析、去重、证据准入、AC-1 参考吸收和跨运行记忆。

兼容入口 `--demo` 仍等同于 `--mode demo`。实时模式不会把固定依赖候选文件当作本轮结果。

## Discovery First

Discovery 只表示“发现了候选”。候选必须经过 Evidence Admission。发现不等于准入、监测、建议、授权或整改。

## 12 个小 Cell

12 个逻辑 Cell 在同一 Python 进程中运行。来源适配器只是调用与规范化层，不是新 Cell。单个发现 Cell 失败时显示 `PARTIAL_DISCOVERY_NOT_ASSESSED`；三个发现 Cell 全部失败时显示 `DISCOVERY_UNAVAILABLE`。

## 实时只读来源

试点仅观察：

- 5 个已登记项目视图，不做账号级仓库枚举；
- `dcell.net` 的 4 个公开 GET 端点；
- DBA `site` 的 `npm audit --omit=dev --json`；
- 同一工作流、主分支、成功且未过期的上一轮实时制品。

私有跨仓库凭据缺失时输出 `NOT_ASSESSED_CREDENTIAL_UNAVAILABLE`。旧快照不会替代实时观察，也不会被涂成绿色。

## Memory 边界

第二轮只读加载第一轮 `latest.json`，按 `finding_id + project_id + finding_type` 比较 `NEW / CONTINUING / CLOSED / REAPPEARED`。观察时间变化不会制造新发现。历史制品不会被覆盖。

能力发现模式读取最近一次成功、main 分支、Schema 兼容且摘要正确的能力注册表制品。无合格制品时明确从 DCDAT-001 启动；无效制品标记为拒绝，不会静默从空注册表开始。

## 自动能力发现边界

自动发现只使用 arXiv Atom/API、GitHub 公开搜索与公开仓库元数据、已登记官方引用、DCDAT-001 和可选仓库内提示。它不下载 PDF、不克隆仓库、不执行外部代码、不安装依赖，也不把参考吸收解释为采用。

## 本地生成 Demo

在 `digital-biosphere-architecture` 目录运行：

    python3 cockpit/weekly/run_weekly.py --mode demo --output-dir cockpit/weekly/demo

页面无需服务器，不访问外网，不加载 CDN 或外部字体。

## 测试

    python3 -m unittest discover -s cockpit/weekly/tests -v

## 人工与每日工作流

在 GitHub Actions 中选择 `DBA Weekly Cockpit Candidate` 可以执行人工只读观察。每日定时入口在 `01:00 UTC`（北京时间 `09:00`）触发，并继续受仓库变量 `DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED == true` 约束。定时运行固定使用 `live-read-only-pilot` 和 `second` 序列；变量缺失或不是 `true` 时只记录禁用状态，不执行观察。

独立的公开能力发现入口每周一 `01:00 UTC` 触发，仅受 `DBA_AUTOMATIC_CAPABILITY_DISCOVERY_ENABLED == true` 约束。启用该变量不会启用完整项目周检，能力发现 Job 不注入私有跨仓库令牌。

## 不可变边界

驾驶舱不修改来源仓库，不创建或合并 PR，不部署，不执行依赖修复，不访问红岩运行时，不生成新的权限，也不把实时观察升级为 canonical truth。
