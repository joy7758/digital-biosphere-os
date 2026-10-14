import { content, gateRows, repositoryBaselines, type Locale } from "./site-content";
import { Footer, Header } from "./site-shell";

export function StatusPage({ locale }: { locale: Locale }) {
  const c = content[locale];
  const copy = locale === "zh"
    ? {
        eyebrow: "VERIFIABLE STATUS / 可验证状态",
        title: "TITMAS 商业基础设施成熟度计划进行中",
        lead: "有界服务、PostgreSQL 数据平面与运行指标已建立；CR-01 结构恢复通过，但 2 条历史 Receipt 的签名无法验证，完整恢复闸门阻塞且 RTO 尚未建立。",
        observed: "观察时间",
        current: "当前商业成熟度状态",
        baselines: "远程基线",
        gates: "验证闸门",
        visibility: "可见性",
        next: "下一步",
        nextBody: "CR01-D02 已批准设计但未批准实施。下一步 CR01-D03 决定是否实施“不可变异常清单 + 租户级锚定清洁 epoch”及是否例外增加 PR 和部署额度；此前不修改 Gateway、不迁移数据库、不重启 CR-01 或 72 小时稳定性测试。",
        back: "返回首页",
        groups: [
          {
            title: "商业候选服务",
            rows: [
              ["SERVICE_READY", "true"],
              ["COMMERCIAL_TECHNICAL_READY", "false"],
              ["PAID_BETA_READY", "false"],
              ["PRODUCTION_READY", "false"],
              ["DATABASE_DEPLOYMENT_EVIDENCE_RECORDED", "true"],
              ["CR01_STATUS", "BLOCKED_LEDGER_INTEGRITY"],
              ["CR01_D02_STATUS", "ACCEPTED_DESIGN_ONLY"],
              ["LEDGER_TRANSITION_IMPLEMENTATION_AUTHORIZED", "false"],
              ["BACKUP_RESTORE_DRILL_PASS", "false"],
              ["RESTORE_RTO_STATUS", "NOT_ESTABLISHED"],
            ],
          },
          {
            title: "智能体优先原则",
            rows: [
              ["AGENT_ABSOLUTE_PRIORITY", "true"],
              ["PRIMARY_OPERATIONAL_CUSTOMER", "AI_AGENT"],
              ["HUMAN_USABILITY_PRIMARY_GATE", "false"],
              ["AGENT_PRIORITY_GRANTS_AUTHORITY", "false"],
            ],
          },
          {
            title: "Stage 5.7 结果",
            rows: [
              ["VALID_SCENARIO_RUNS", "24"],
              ["DISTINCT_PROVIDERS", "3"],
              ["EXACT_MODELS", "4"],
              ["AGENT_SELECTION_AUDITOR", "PASS"],
              ["OPTION_D_RANKED_FIRST", "24/24"],
              ["OPTION_D_EXCLUSIVE", "7/24"],
            ],
          },
          {
            title: "历史人类兼容性观察",
            rows: [
              ["E01_CLASSIFICATION", "LEGACY_OPTIONAL"],
              ["E01_STATUS", "EXPIRED_ACCESS_REVOKED_NO_CONTRIBUTION_OBSERVED"],
              ["E01_IS_PROGRAM_GATE", "false"],
              ["E01_EXTENSION_AUTHORIZED", "false"],
              ["COMPENSATED_HUMAN_TRIAL_STRATEGY", "RETIRED"],
            ],
            note: "E01 已到期且仓库访问已撤销；未观察到参与者 Fork、PR 或反馈，Human Disposition 仍未记录。该历史观察不阻塞 Agent 原生主线。",
          },
          {
            title: "尚未完成",
            rows: [
              ["PUBLIC_PROTOCOL_RELEASED", "false"],
              ["FORMAL_STANDARD_CHANGE_AUTHORIZED", "false"],
              ["COMMERCIAL_ACCESS_GRANTED", "false"],
              ["TITMAS_COMMUNITY_ESTABLISHED", "false"],
              ["COMMERCIAL_ECOSYSTEM_ESTABLISHED", "false"],
              ["PRODUCTION_READY", "false"],
            ],
          },
        ],
      }
    : {
        eyebrow: "VERIFIABLE STATUS",
        title: "TITMAS commercial infrastructure maturity program in progress",
        lead: "The bounded service, PostgreSQL data plane, and operational metrics exist. CR-01 structural restoration passed, but 2 historical Receipt signatures could not be verified; full recovery is blocked and RTO is not established.",
        observed: "Observed at",
        current: "Current commercial maturity status",
        baselines: "Remote baselines",
        gates: "Validation gates",
        visibility: "Visibility",
        next: "Next step",
        nextBody: "CR01-D02 approved design, not implementation. CR01-D03 must decide whether to implement an immutable exception manifest plus Tenant-scoped anchored clean epochs and whether to grant PR and deployment-cap exceptions. Gateway changes, database migration, CR-01 restart, and the 72-hour soak remain closed.",
        back: "Back to home",
        groups: [
          {
            title: "Commercial candidate service",
            rows: [
              ["SERVICE_READY", "true"],
              ["COMMERCIAL_TECHNICAL_READY", "false"],
              ["PAID_BETA_READY", "false"],
              ["PRODUCTION_READY", "false"],
              ["DATABASE_DEPLOYMENT_EVIDENCE_RECORDED", "true"],
              ["CR01_STATUS", "BLOCKED_LEDGER_INTEGRITY"],
              ["CR01_D02_STATUS", "ACCEPTED_DESIGN_ONLY"],
              ["LEDGER_TRANSITION_IMPLEMENTATION_AUTHORIZED", "false"],
              ["BACKUP_RESTORE_DRILL_PASS", "false"],
              ["RESTORE_RTO_STATUS", "NOT_ESTABLISHED"],
            ],
          },
          {
            title: "Agent-priority principle",
            rows: [
              ["AGENT_ABSOLUTE_PRIORITY", "true"],
              ["PRIMARY_OPERATIONAL_CUSTOMER", "AI_AGENT"],
              ["HUMAN_USABILITY_PRIMARY_GATE", "false"],
              ["AGENT_PRIORITY_GRANTS_AUTHORITY", "false"],
            ],
          },
          {
            title: "Stage 5.7 result",
            rows: [
              ["VALID_SCENARIO_RUNS", "24"],
              ["DISTINCT_PROVIDERS", "3"],
              ["EXACT_MODELS", "4"],
              ["AGENT_SELECTION_AUDITOR", "PASS"],
              ["OPTION_D_RANKED_FIRST", "24/24"],
              ["OPTION_D_EXCLUSIVE", "7/24"],
            ],
          },
          {
            title: "Historical human compatibility observation",
            rows: [
              ["E01_CLASSIFICATION", "LEGACY_OPTIONAL"],
              ["E01_STATUS", "EXPIRED_ACCESS_REVOKED_NO_CONTRIBUTION_OBSERVED"],
              ["E01_IS_PROGRAM_GATE", "false"],
              ["E01_EXTENSION_AUTHORIZED", "false"],
              ["COMPENSATED_HUMAN_TRIAL_STRATEGY", "RETIRED"],
            ],
            note: "E01 expired and repository access was revoked. No participant Fork, PR, or feedback was observed, and Human Disposition remains unrecorded. This historical observation does not block the agent-native mainline.",
          },
          {
            title: "Not completed",
            rows: [
              ["PUBLIC_PROTOCOL_RELEASED", "false"],
              ["FORMAL_STANDARD_CHANGE_AUTHORIZED", "false"],
              ["COMMERCIAL_ACCESS_GRANTED", "false"],
              ["TITMAS_COMMUNITY_ESTABLISHED", "false"],
              ["COMMERCIAL_ECOSYSTEM_ESTABLISHED", "false"],
              ["PRODUCTION_READY", "false"],
            ],
          },
        ],
      };

  return (
    <div className="site status-page" lang={c.lang}>
      <Header locale={locale} section="status" />
      <main id="main-content">
        <section className="status-hero">
          <div className="section-shell">
            <p className="section-kicker">{copy.eyebrow}</p>
            <h1>{copy.title}</h1>
            <p>{copy.lead}</p>
            <div className="observed-chip"><span>{copy.observed}</span><strong>2026-07-31 · Asia/Shanghai</strong></div>
          </div>
        </section>
        <section className="section status-detail-section current-truth-section">
          <div className="section-shell">
            <h2>{copy.current}</h2>
            <div className="current-truth-grid">
              {copy.groups.map((group) => (
                <article key={group.title}>
                  <h3>{group.title}</h3>
                  <dl>
                    {group.rows.map(([label, value]) => (
                      <div key={label}>
                        <dt>{label}</dt>
                        <dd>{value}</dd>
                      </div>
                    ))}
                  </dl>
                  {"note" in group && group.note ? <p>{group.note}</p> : null}
                </article>
              ))}
            </div>
          </div>
        </section>
        <section className="section status-detail-section">
          <div className="section-shell">
            <h2>{copy.baselines}</h2>
            <div className="baseline-table" role="table">
              {repositoryBaselines.map((repo) => (
                <div className="baseline-row" key={repo.key} role="row">
                  <strong role="cell">{repo.key}</strong>
                  <span role="cell">{locale === "zh" ? repo.labelZh : repo.label}</span>
                  <code role="cell">{repo.commit.slice(0, 12)}</code>
                  <span className={`visibility visibility-${repo.visibility}`} role="cell">{repo.visibility}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
        <section className="section status-detail-section alt">
          <div className="section-shell">
            <h2>{copy.gates}</h2>
            <div className="gate-list">
              {gateRows.map((gate) => (
                <article key={gate.id}>
                  <span className={`state state-${gate.state.toLowerCase()}`}>{gate.state}</span>
                  <code>{gate.id}</code>
                  <p>{gate[locale]}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
        <section className="section next-gate-section">
          <div className="section-shell next-gate-card">
            <span>ADR-035 / STAGE 5.7</span>
            <div><h2>{copy.next}</h2><p>{copy.nextBody}</p></div>
            <a className="button button-secondary" href={locale === "zh" ? "/" : "/en/"}>{copy.back}</a>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
