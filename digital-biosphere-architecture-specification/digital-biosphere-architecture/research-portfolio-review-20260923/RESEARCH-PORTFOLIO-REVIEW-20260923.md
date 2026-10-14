> 仓库同步说明：本文件是 2026-09-23 研究成果复盘的路径脱敏副本，保留原报告结论、失败记录与限制。仅为私有 DBA 仓库的引用性汇报，不修改子项目规范、代码、运行状态或授权。
>
> 来源标记 `repository-name::path` / `project/name::path` 是逻辑定位符，不是已上传工件或可访问 URL。`LOCAL_COCKPIT_EVIDENCE::`、`LOCAL_EXPERIMENT_ARCHIVE::` 和 `INSTALLED_OPERATOR_SKILL::` 表示原审查所用本机来源；原始证据未随本次同步上传。下文历史验证结果并非本次同步重新执行的测试。

# DBA、DCell、TITMAS 及关联研究成果复盘

审查日期：2026-09-23。性质：只读研究资产复盘，不是上线验收、实施授权或新的架构规范。

## 一、先说结论

**我们不是只有一堆概念，也还没有做成一个“无论换哪个智能体都保证成功交付”的系统。**

已经积累的主要成果是：

1. 把任务目标、主体身份、权限边界、证据、评价和历史分开的治理方法。
2. 可运行的证据校验、审查绑定、受限行动闸门和若干参考实现。
3. 更换认知内核时保留身份、使命和经验的本地合成演示，以及一条真实外部模型调用记录。
4. DEB 小型可复现实验与保留失败的工程研究记录。
5. DCell 的实际数据生产、公开产品和仓储读取入口，以及尚未完全闭合的消费、维护链。

**最关键的未证实主张：这些能力组合以后，是否比普通智能体工作流更稳定、更低成本地完成客户任务，尤其是在更换执行智能体后。**

此前把 TITMAS 只概括为“证据核对器”不完整；反过来，将整个项目群的所有目标都算成 TITMAS 已实现能力也不正确。

## 二、审查范围与证据等级

本轮读取 DBA 入口、治理文档与机器状态、DCell 现行宪法和工作台账、各主要项目入口及选定执行/验证记录，并浏览 dcell.net 与 zenodo.cn 公开页面。对前轮 TITMAS 实测采用本对话已经完成的测试与对照结果，不重新跑实验。

覆盖主线：DBA、DST/DEB、DBOS、SAEE、TITMAS、Digital Cell/DCell 模块规范、DCell Cognitive Kernel、dcell.net 数据生产、zenodo.cn 仓储、Agent Evidence、ARO、POP、Token Governor、Agent Health/Immune、TITMAS Health、Media Evidence、Action Gate，以及部分关联应用入口。

这不是全部仓库逐行源码审计，也不是所有论文、专利、线上系统的重新验收。没有重新运行测试、真实任务或付费模型，没有登录服务器、刷新远端 Git、修改源码、提交或部署。部分文件读取输出过大，仅对关键状态和相关章节补读；未读的内容不算已核验。公开网页由浏览工具取得，可能带缓存，不能作为持续在线保证。

证据使用规则：

| 等级 | 本报告怎么解释 |
|---|---|
| 规范/目标 | 说明打算解决什么，不证明已经做到 |
| 本地实现/合成验证 | 说明明确输入和规则下能运行，不证明现实客户价值 |
| 历史真实执行回执 | 说明当时执行过，保留时间、版本和限制，不冒充今天重新运行 |
| 本轮读取到的公开页面 | 说明公开入口提供了这些信息，不证明底层所有能力有效 |
| 客户效果/长期可靠性 | 必须另有实际任务、验收、接续和成本证据，不能从前几类推导 |

## 三、优先发现的问题

### 1. “换智能体仍能保证结果”由三个不同问题组成

**身份连续性**：换模型后，还是同一个主体，使命和经验不丢。

**验收连续性**：换执行者后，仍按同一客户目标和标准工作，旧失败不能被新会话抹掉。

**结果可靠性**：换执行者之后，任务最终确实更容易合格，且成本可接受。

前两项已有规范和局部实现证据；第三项尚未在本次核查材料中形成足够的端到端证明。不能把身份连续性测试 PASS 写成最终结果保证。

### 2. 状态入口存在明显时间与内容不一致

- DBA 的 `PROGRAM-STATUS.md` 首页仍是 2026-08-02 快照，后面追加了不同阶段内容；商业就绪文件的观察日期为 2026-08-12。它们不是 9 月 23 日实时事实。
- Cognitive Kernel 的 `PRODUCT_STATUS.json` 写着真实模型调用未完成；但 `reports/LIVE_MODEL_VALIDATION.json` 记录 2026-08-21 一次千帆调用 PASS。不能只读根状态就宣布没有调用，也不能只拿该调用宣布产品完成。
- Cognitive Kernel 的 SAEE 调用记录存在，但评价模式是合成描述符模拟、结论 HOLD，并有两个主要问题。调用成功与评价通过是两回事。
- DBA 本机最新指针指向 2026-09-22 制品：`pilot_status=LIVE_READ_ONLY_PILOT_FAILED`、`source_coverage_status=PARTIAL`、`result_projection_consistent=true`，Memory 没有加载合格前序制品、未执行跨运行比较。

驾驶舱页面投影一致，只说明展示没有把结果改错，不说明试点通过。本轮未触发新运行，因此不将 9 月 22 日记录当作今天的运行结果。

### 3. 已有负面实证必须影响方向，不能只保留在档案里

Agent Immune 的 2026-07-28 五任务对照记录：25 条建议中，3 条独有有用、5 条重复、17 条误报或不适用；最终任务结果改善为 0。历史决定为 `ABANDON_AGENT_IMMUNE_CODEX_SKILL`，不支持默认加进 Codex 工作流。

最新 TITMAS 对照中，12 对完整样本为 11 对持平、1 对普通审查更好、0 对 TITMAS 更好。这不能证明 TITMAS 没有其他价值，但不能继续声称它已经普遍提高判断准确率。

### 4. 验收体系确实能保留“不合格”，但尚不能自动补足执行能力

鹳雀楼项目当前机器记录为 `NEEDS_REVISION`。候选视频技术检查可以通过，外观和运动语义仍 FAIL；本地 TITMAS outcome review 为 FAIL。远端 Sandbox 只通过元数据 Schema 预检，商业 D29 视频验收接口未部署、没有相应签名回执。

这体现了“技术能跑不等于客户要的结果合格”的边界；但它没有证明 TITMAS 已经把不合格视频修成合格视频，更不能量化为 TITMAS 独有的收益。

### 5. DCell 的实际生产路线，已经不同于早期“数字细胞 Demo”

目前至少需要区分四种含义：

| 名称 | 实际对象 |
|---|---|
| Digital Cell Demo | Identity、Boundary、Evidence、Health、Memory、Reputation 的参考演示 |
| DCell module governance profile | 可选择模块的准入、权限交集、组合和重新核验规范 |
| DCell Cognitive Kernel | 更换模型/能力组件后保持主体身份、使命和经验的私有试点候选 |
| dcell.net | 持续提供智能体所需可信公共状态的数据生产与维护项目 |

这些工作有共同思想，但不是同一个已完成产品。不得用一个演示的通过状态证明另一个生产项目成熟，也不能因为名字相同就合并它们的权限与责任。

## 四、主要研究成果盘点

| 研究线 | 本次找到的实际成果 | 未证明或仍有缺口 |
|---|---|---|
| DBA | 章程、组合、职责、机器入口、来源优先级、只读观察制品 | 不是项目执行引擎；最近指针所指试点失败，Memory 连续比较未形成 |
| DST | 适应、平衡、多样性、韧性、连续性的理论框架及可证伪研究路线 | 未形成普适数字生存规律或意识/生命证明 |
| DEB-001 Lite | 三策略各 3 个体、三阶段、多个种子、Alpha 主运行/重放和原始日志 | 小样本和规则/个体偏置；没有长期策略优劣结论 |
| DEB v0.2 | 112 项要求的语义规范冻结记录 | 冻结记录明确不授权实现；不能称 v0.2 运行实现已完成 |
| DBOS | 身份、生命周期、证据、联邦和规范引用等基础设施工作；历史本地符合性记录 | 部分模块仍是 specification-only；不能据仓库名推断已有完整主体运行时 |
| SAEE | 本地评价、符合性工具、合成描述符评价和研究材料 | 所读实例不执行真实候选智能体；不能从模拟评分判断真实模型优劣 |
| TITMAS 私有平台 | Gate/Receipt/Audit/Health 方向、机器合同、沙箱与本地 outcome 审查工具、前轮完整测试 | 不等于所有商业入口已部署或客户效果已验证；不能保证事实和语义正确 |
| DCell Cognitive Kernel | 255 项测试通过记录、身份/使命/经验连续性合成演示、一条真实模型调用回执 | 商业准备状态 HOLD，SAEE 两项主要发现；未证明真实多模型替换后客户任务连续成功 |
| dcell.net 生产维护 | 真实数据候选、公开产品、受限普通提交、日常任务和维护修正记录 | 社零消费曾 FAIL；动态多产品和新期接续不完整；CPI 接续缺口保留 |
| zenodo.cn | 可见的数据目录、机器读取入口、来源/版本/使用边界展示 | 仓储发布不等于独立消费合格、第三方自然采用或所有数据当前正确 |
| Agent Evidence / EEOAP | 证据对象、验证器、受控边界研究、软件与预印本引用入口 | 引用记录不等于事件真实；源检出与发布版本需要区分 |
| ARO-Audit | 单回执核验、篡改拒绝等公开参考入口 | 不是完整生产审计控制系统 |
| POP | 可迁移 persona 对象与多框架配置投射 | persona 可迁移不等于任务结果等价或法律身份认证 |
| Token Governor | 预算窗口接口与玩具策略参考 | 公开仓不含完整生产路由、策略引擎或成本收益证明 |
| Agent Immune / Agent Health | 静态仓库健康 CLI 与历史发布记录 | 不观察运行时；默认加到 Codex 的增量价值试点为负面结果 |
| TITMAS Health | 稳定性、可观测性和证据完整性评价方向 | 不能把健康分当安全认证或智能体通用能力排名 |
| TITMAS Media Evidence | 媒体审核来源、异议、决定和证据链的本地合成参考实现 | 不是媒体真假鉴定器，不能替代源事实、许可或专业审核责任 |
| TITMAS Action Gate | 确定性闸门、证据适配、MCP 参考、历史 GitHub 沙箱动作记录 | 不等于真实多智能体自治部署已全部验证或客户生产控制可用 |
| Research Agent / EOA | 科研流程、来源审查、证据对象与研究准备材料 | 根入口仍标 preparation-only；不能与其中独立 DEB 子实验混为一项完成状态 |

表中测试、发布和调用数量来自各自已保存回执；本轮没有重新运行这些测试，也没有统一确认它们对应最新远端版本。

## 五、最值得保留的四项资产

### A. 任务和主体不依赖某一个模型的思路

这是用户此前记忆的实际来源之一。Cognitive Kernel 的连续性演示保存相同 `cell_id`、使命摘要和已验证经验，内核从 `heuristic-v1` 切换为 `openai-compatible-v1`，并保留后续经验使用记录。

该演示明确 `synthetic_data_only=true`、使用无真实凭据时的确定性回退；另一份真实千帆调用回执单独存在。两份材料不能拼成“两家真实模型成功接力同一客户任务”。

当前可说：**已验证局部连续性机制，尚未验证普遍交付连续成功。**

### B. 客户目标到最终交付物的审查绑定

已安装 outcome review 规范不是仅检查 JSON。它要求实际看图、看视频或运行客户场景，分别检查领域要求、整体集成和客户目标；不合格须指出位置与返工条件，修改后重新绑定。

精确字节、版本和引用由工具核对，语义判断仍依赖审查主体能力。整个工作模式有价值，但执行者、审查者及工具不足时仍可能失败。

### C. 保留失败、版本和接续历史的工程纪律

DEB 的 Alpha 报告明确记录不同 run_id 导致原始 CSV 不同，只有身份归一化后内容相同，没有把原始字节不一致涂成一致。

DEB 三个验证种子和 Alpha 都出现同一 EFFI1 退出。这是可重复的规则内观察，同时也是个体/规则偏置应被研究的信号，不能直接叫作自然涌现的生存规律。

最新 TITMAS 修正保留原始失败和旧版本，并把本地适配器修正、原回答回放、新调用对照和预算诊断分开。这些是可复核研究资产，而不是成功宣传材料。

### D. 已经交付出去的数据对象

本轮公开页面中能看到社零、PMI、财政、GDP、CPI、ROR 子集等产品入口。其价值是别人能够找到来源、期间、版本、文件和适用条件，而不是只能阅读我们的架构说明。公开页面来源：[DCell](https://dcell.net/)、[zenodo.cn 数据目录](https://zenodo.cn/)。

但是社零记录在目录上仍显示期间及发布机构未明确提取的提示；本地台账保留消费检查 FAIL。已发布和消费者正确使用仍不能合并成同一个通过状态。

9 月 23 日工作台账记录验收/维护时点补丁已部署并通过离线检查，下一真实维护批次为 9 月 24 日；本轮未登录服务器确认，不提前宣称维护修复已获真实业务验证。

## 六、发现、吸收和自主改进到了哪里

不是完全没有发现层：DBA 有能力发现与候选/移交字段、DCell 有需求发现和来源准入路线、3D 流水线有来源缺口门槛，相关项目还有有界修复候选与经验记录。

但需要区分：

1. 找到一个外部能力。
2. 证实它适用于某个真实问题。
3. 在隔离范围接入并验证。
4. 正式任务实际使用。
5. 结果改善且没有成本、权限或可靠性退化。
6. 后续替换模型/版本后仍能持续使用。

**本次没有找到一条足以证明整个项目群已普遍实现上述六步的统一实证链。**已有局部成功和已保留失败，不应升级成“全自动吸收已全面有效”，也不应因此把所有局部能力说成不存在。

## 七、关联应用与研究发表边界

- 3D 建筑视频：已有候选出片和本地审查，但当前视觉/动作不合格、客户验收未取得。这是最直接的结果验收案例。
- 麻将：已有确定性规则引擎、独立策略观察和非学习评测入口，是较明确的可计算验收场景；本轮未重跑牌局，不把可复放规则引擎说成学习智能体优越性。
- 涂鸦海战/墨水舰队：本地功能、浏览器与压力测试记录存在，视觉审查仍有开放项；本地状态为未授权公开部署、素材再分发未澄清。同时 dcell.net 首页可见试玩入口。未比较线上版本及素材，不能据此断言违规，但两个表面需要做精确版本与授权对账。
- 红岩公文：驾驶舱制品仅证实限定仓库元数据观察，不是运行时或客户验收。本轮未进入其完整产品与云恢复证据，保留未完整评估。
- 科研发表：SAEE 本地状态记载历史投稿收讫及未完成的后续状态；Agent Evidence 入口区分软件 DOI 和边界研究预印本；EOA 保留来源审查工作。**本轮未核查投稿后台、全部 DOI 或专利档案，不声明当前录用、同行评审认可或专利授权。**

## 八、对下一步的建议，不构成本轮实施

### 第一优先：验证真正的“换智能体交付”

只选一个能够客观验收的真实任务：执行者 A 留下不完整结果，执行者 B 在没有聊天历史的情况下读取固定目标、工件、失败及证据，继续修复；由独立验收确认结果。

普通交接与 TITMAS/DCell 交接使用相同材料、预算和验收条件。记录最终成功、遗漏要求、返工次数、人工介入、总时长和总成本。失败也保留，不通过换案例或降低门槛制造优势。

这才直接检验用户关心的承诺。本报告不启动该实验。

### 第二优先：让现有状态入口正确反映已发生事实

优先处理根状态与直接回执不一致、旧快照冒充现状、Memory 失败以及本地/服务器/公开网页版本区别。不是再增加一层治理文件，而是使现有入口指向正确的当前证据。

### 第三优先：完成已有数据产品的消费与维护闭环

比继续扩大产品数更有价值的是：一个已有产品被正确消费，真实到期维护按预期运行，失败不刷新最后成功状态，换执行者后能接班。

### 第四优先：按实证选择组件，不强制所有项目都套全栈

Agent Health 的负面试点说明“多加一个审查器”不自动增值。简单任务允许不用 TITMAS；只有版本接续、证据、权限或交付风险确实需要时才组合相应组件。

## 九、最终判断

**核心研究方向没有被这次对照实验否定，但成果叙述必须收敛到已经验证的能力。**

可以继续坚持的方向是：模型可以更换，任务目标、主体身份、证据、责任和维护历史不能随之丢失；交付需要看最终结果，不只看过程与分数。

尚不能承诺的是：这些机制能无条件保证任何智能体完成任何客户任务，或者已经显著提高智能体总体能力。

下一阶段应争取的不是更多 PASS 文档，而是一个可复核的事实：**相同任务与资源条件下，换执行智能体之后，我们比普通交接更少丢要求、更少重复工作，并更可靠地交付。**

## 十、主要核查来源

以下为本轮阅读位置或本对话前轮直接实验材料；路径为来源，不代表本轮重新执行。

- `digital-biosphere-architecture-specification::digital-biosphere-architecture/AGENTS.md`
- `digital-biosphere-architecture-specification::digital-biosphere-architecture/PROGRAM-CHARTER.md`
- `digital-biosphere-architecture-specification::digital-biosphere-architecture/PROGRAM-STATUS.md`
- `digital-biosphere-architecture-specification::digital-biosphere-architecture/architecture/main-constitution-principles.json`
- `digital-biosphere-architecture-specification::digital-biosphere-architecture/architecture/titmas-project-constitution.json`
- `digital-biosphere-architecture-specification::digital-biosphere-architecture/architecture/dcell-module-governance-profile.json`
- `digital-biosphere-architecture-specification::digital-biosphere-architecture/commercial-readiness.json`
- `LOCAL_COCKPIT_EVIDENCE::local-runs/DBA-LOCAL-READONLY-20260922T105347Z/latest.json`
- `INSTALLED_OPERATOR_SKILL::titmas-outcome-review/SKILL.md`
- `LOCAL_EXPERIMENT_ARCHIVE::titmas-review-remediation-20260923-01/TITMAS-TEST-ANALYSIS-REMEDIATION-REPORT.md`（前轮直接实验）
- `dcell-cognitive-kernel::PRODUCT_STATUS.json`
- `dcell-cognitive-kernel::reports/CONTINUITY_DEMO.json`
- `dcell-cognitive-kernel::reports/LIVE_MODEL_VALIDATION.json`
- `dcell-cognitive-kernel::reports/SAEE_VALIDATION.json`
- `project/dcell.net::PROJECT_CONSTITUTION.md`
- `project/dcell.net::FINAL_GOAL.md`
- `project/dcell.net::WORKBOARD.md`
- `project/zenodo.cn::AGENTS.md`
- `digital-biosphere-research-agent-pilot::prototype/deb001-lite-simulator/output/DEB-001-LITE-ALPHA-001/DEB-001-LITE-ALPHA-001-EXECUTION-REPORT-v0.1.md`
- `digital-biosphere-research-agent-pilot::prototype/deb001-lite-simulator/DEB-001-LITE-REPLICATION-COMPARISON-REPORT-v0.1.md`
- `digital-biosphere-research-agent-pilot::prototype/deb001-lite-simulator/DEB-001-LITE-v0.2-SPECIFICATION-FREEZE-ACTION-v0.1.md`
- `agent-health::AGENT_IMMUNE_CODEX_INCREMENTAL_VALUE_REPORT.md`
- `SAEE::SAEE_AGENT_INVOCATION_EVALUATION_RESULT_REPORT.md`
- `agent-evidence::docs/research-entry.md`
- `project/3d-building::jobs/guanque-pilot/delivery/current-status.json`
- `project/ink-fleet::project-status.json`

本轮只新增这份汇报，不改变任何项目事实、规范、代码、授权或运行状态。
