"use client";

import { useRef, useState } from "react";
import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";
import styles from "./media-evidence/media-evidence-demo.module.css";

const REFERENCE_COMMIT = "7eac452f66a2b7de525543f80b9a7cf1465ef9a1";

const scenarios = {
  zh: [
    {
      id: "lifecycle",
      label: "正常生命周期",
      title: "从生成请求到可携带审计包复核",
      summary: "各状态都是本地合成记录，不代表现实授权、身份认证或内容真实。",
      steps: [
        ["生成请求", "已记录（RECORDED）", "希望生成一条人工智能新闻视频。"],
        ["授权状态记录", "已批准（APPROVED）", "仅表示演示中的授权记录状态。"],
        ["智能体执行记录", "已记录（RECORDED）", "关联 Producer-Agent、模拟模型和输出引用。"],
        ["多来源证据", "已规范化（NORMALIZED）", "来源声明、检测观察和水印观察并列保留。"],
        ["审核决定", "暂缓（HOLD）", "授权主体记录业务决定，不判断绝对真假。"],
        ["可携带审计包复核", "本地校验通过（PASS）", "文件清单、哈希和引用在本地演示规则内通过。"],
      ],
      result: "生命周期记录完成（GOVERNANCE_COMPLETE）",
    },
    {
      id: "conflict",
      label: "证据冲突",
      title: "保留冲突，而不是强制制造假确定",
      summary: "不同主体可以留下不同观察；异议和处置只记录治理状态。",
      steps: [
        ["来源声明", "存在（AVAILABLE）", "模拟来源声明存在；本站不执行真实 C2PA 验证。"],
        ["检测模型", "结果异常（ANOMALY_DETECTED）", "模拟检测模型给出异常观察。"],
        ["人工复核", "需要复核（REQUIRES_HUMAN_REVIEW）", "人工观察不覆盖其他证据。"],
        ["异议记录", "异议开启（OPEN）", "冲突原因和目标证据引用被记录。"],
        ["补充证据", "已提供（PROVIDE_MORE_EVIDENCE）", "响应补充材料，不自动裁决真假。"],
        ["处置与决定", "处置升级（ESCALATED）· 暂缓（HOLD）", "处置升级到人工流程并暂缓发布。"],
      ],
      result: "治理状态已记录（GOVERNANCE_STATE_RECORDED）",
    },
    {
      id: "tamper",
      label: "篡改检测",
      title: "文件变化可以触发失败关闭",
      summary: "哈希检查只能说明字节是否与清单一致，不能证明内容真实。",
      steps: [
        ["原始合成审计包", "本地校验通过（PASS）", "Manifest、文件清单与 SHA-256 一致。"],
        ["修改媒体文件", "检测到变化（HASH_MISMATCH）", "模拟文件修改后仍保留旧哈希。"],
        ["重新离线复核", "本地校验拒绝（FAIL）", "完整性检查失败并停止升级状态。"],
      ],
      result: "篡改样例被拒绝（REJECTED）",
    },
  ],
  en: [
    {
      id: "lifecycle",
      label: "Normal lifecycle",
      title: "From creation request to portable-package review",
      summary: "Every state is synthetic and local; none establishes real authorization, identity, or content truth.",
      steps: [
        ["Creation request", "Recorded (RECORDED)", "Request a synthetic AI news video."],
        ["Authorization record", "Approved (APPROVED)", "A synthetic authorization-record state only."],
        ["Agent execution record", "Recorded (RECORDED)", "Associate Producer-Agent, a simulated model, and an output reference."],
        ["Multi-source evidence", "Normalized (NORMALIZED)", "Retain provenance, detector, and watermark observations in parallel."],
        ["Review decision", "Hold (HOLD)", "Record a business decision without determining absolute truth."],
        ["Portable package review", "Local check passed (PASS)", "Files, hashes, and references pass the local demo rules."],
      ],
      result: "Lifecycle recorded (GOVERNANCE_COMPLETE)",
    },
    {
      id: "conflict",
      label: "Evidence conflict",
      title: "Preserve conflict instead of manufacturing certainty",
      summary: "Different actors can retain different observations; Challenge and Resolution record governance state only.",
      steps: [
        ["Provenance statement", "Available (AVAILABLE)", "A simulated statement exists; no real C2PA validation runs."],
        ["Detector", "Anomaly detected (ANOMALY_DETECTED)", "A simulated detector records an abnormal observation."],
        ["Human review", "Review required (REQUIRES_HUMAN_REVIEW)", "The human observation does not overwrite other evidence."],
        ["Challenge", "Open (OPEN)", "The conflict reason and target evidence reference are recorded."],
        ["Additional evidence", "Provided (PROVIDE_MORE_EVIDENCE)", "The response adds material without truth adjudication."],
        ["Resolution and decision", "Escalated (ESCALATED) · Hold (HOLD)", "Escalate to a human process and hold publication."],
      ],
      result: "Governance state recorded (GOVERNANCE_STATE_RECORDED)",
    },
    {
      id: "tamper",
      label: "Tamper detection",
      title: "File changes trigger fail-closed verification",
      summary: "A hash check can show byte inconsistency; it cannot prove content truth.",
      steps: [
        ["Original synthetic package", "Local check passed (PASS)", "Manifest, file list, and SHA-256 agree."],
        ["Modified media file", "Change detected (HASH_MISMATCH)", "The simulated file changes while the old hash remains."],
        ["Offline recheck", "Local check failed (FAIL)", "Integrity fails and the state does not advance."],
      ],
      result: "Tampered fixture rejected (REJECTED)",
    },
  ],
} as const;

export function MediaEvidenceDemoPage({ locale }: { locale: Locale }) {
  const items = scenarios[locale];
  const [activeIndex, setActiveIndex] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const path = locale === "zh" ? "/demo/media-evidence/" : "/en/demo/media-evidence/";
  const industry = locale === "zh" ? "/industry/media-evidence/" : "/en/industry/media-evidence/";

  function select(index: number, focus = false) {
    const next = (index + items.length) % items.length;
    setActiveIndex(next);
    if (focus) window.requestAnimationFrame(() => tabRefs.current[next]?.focus());
  }

  return (
    <div className="site" lang={locale === "zh" ? "zh-CN" : "en"}>
      <Header locale={locale} section="mediaDemo" />
      <StructuredPageData locale={locale} path={path} title={locale === "zh" ? "TITMAS 媒体证据在线演示" : "TITMAS Media Evidence demo"} description={locale === "zh" ? "三个纯前端本地合成场景，展示生命周期、冲突治理和篡改检测。" : "Three frontend-only synthetic scenarios for lifecycle, conflict governance, and tamper detection."} type="TechArticle" dateModified="2026-08-01" />
      <main className={styles.page} id="main-content">
        <div className={styles.boundaryBanner} role="note">
          <strong>{locale === "zh" ? "本地合成参考演示" : "Local synthetic reference demo"}</strong>
          <span>{locale === "zh" ? "本演示仅展示记录结构、引用关系、生命周期和文件完整性检查。不提供内容真实性认证、身份认证、法律证据或生产审核服务。" : "This demo shows record structure, references, lifecycle, and file-integrity checks only. It provides no content-truth, identity, legal-evidence, or production-review service."}</span>
        </div>

        <section className={styles.hero}>
          <div className={styles.shell}>
            <p className={styles.kicker}>{locale === "zh" ? "TITMAS 媒体证据 / v0.1.0" : "TITMAS MEDIA EVIDENCE / v0.1.0"}</p>
            <h1>{locale === "zh" ? "媒体证据治理生命周期演示" : "Media evidence governance lifecycle demo"}</h1>
            <p>{locale === "zh" ? "选择一个场景，查看证据对象、引用链、异议记录、审核决定与可携带审计包如何协同。" : "Choose a scenario to inspect how Evidence Objects, reference chains, Challenges, Decisions, and portable audit packages work together."}</p>
            <div className={styles.truth}><code>SYNTHETIC_DATA_ONLY</code><code>NO_UPLOAD</code><code>NO_EXTERNAL_API</code><code>NO_PERSISTENCE</code></div>
          </div>
        </section>

        <section className={styles.demoSection}>
          <div className={styles.shell}>
            <div className={styles.tabs} role="tablist" aria-label={locale === "zh" ? "演示场景" : "Demo scenarios"} onKeyDown={(event) => {
              if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
                event.preventDefault();
                select(activeIndex + (event.key === "ArrowRight" ? 1 : -1), true);
              }
            }}>
              {items.map((scenario, index) => <button type="button" role="tab" id={`media-tab-${scenario.id}`} aria-controls={`media-panel-${scenario.id}`} aria-selected={index === activeIndex} tabIndex={index === activeIndex ? 0 : -1} key={scenario.id} ref={(node) => { tabRefs.current[index] = node; }} onClick={() => select(index)}><span>0{index + 1}</span>{scenario.label}</button>)}
            </div>

            {items.map((scenario, index) => (
              <article className={styles.panel} role="tabpanel" id={`media-panel-${scenario.id}`} aria-labelledby={`media-tab-${scenario.id}`} hidden={index !== activeIndex} key={scenario.id}>
                <header><p className={styles.kicker}>{locale === "zh" ? "场景" : "Scenario"} 0{index + 1}</p><h2>{scenario.title}</h2><p>{scenario.summary}</p></header>
                <ol className={styles.timeline}>
                  {scenario.steps.map(([label, status, detail], stepIndex) => <li key={`${label}-${status}`}><span className={styles.stepNumber}>{String(stepIndex + 1).padStart(2, "0")}</span><div><h3>{label}</h3><strong>{status}</strong><p>{detail}</p></div></li>)}
                </ol>
                <footer><span>{locale === "zh" ? "演示结果" : "Demo result"}</span><strong>{scenario.result}</strong></footer>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.details}>
          <div className={styles.shell}>
            <div className={styles.detailGrid}>
              <article><span>{locale === "zh" ? "技术架构（ARCHITECTURE）" : "ARCHITECTURE"}</span><h2>{locale === "zh" ? "技术架构" : "Technical architecture"}</h2><p>{locale === "zh" ? "生成请求 → 授权状态记录 → 智能体执行记录 → 证据对象 → 证据链 → 异议记录 → 审核决定 → 可携带审计包" : "Request → Authorization → Agent Execution → Evidence Object → Chain → Challenge → Decision → Portable Package"}</p></article>
              <article><span>{locale === "zh" ? "已实现范围（IMPLEMENTED SCOPE）" : "IMPLEMENTED SCOPE"}</span><h2>{locale === "zh" ? "当前实现范围" : "Current scope"}</h2><p>{locale === "zh" ? "结构检查、SHA-256 完整性、引用顺序、冲突保留和本地包复核。" : "Structure checks, SHA-256 integrity, reference ordering, conflict retention, and local package review."}</p></article>
              <article><span>{locale === "zh" ? "未实现能力（NOT IMPLEMENTED）" : "NOT IMPLEMENTED"}</span><h2>{locale === "zh" ? "未实现能力" : "Not implemented"}</h2><p>{locale === "zh" ? "真实模型、真实 C2PA、外部身份、线上审核、数据库、区块链和法律证据服务。" : "Real models, real C2PA, external identity, online review, databases, blockchain, and legal-evidence services."}</p></article>
            </div>
            <div className={styles.release}>
              <dl><div><dt>{locale === "zh" ? "版本（VERSION）" : "VERSION"}</dt><dd>v0.1.0</dd></div><div><dt>{locale === "zh" ? "参考提交（REFERENCE COMMIT）" : "REFERENCE COMMIT"}</dt><dd><code>{REFERENCE_COMMIT}</code></dd></div><div><dt>{locale === "zh" ? "数据政策（DATA POLICY）" : "DATA POLICY"}</dt><dd>SYNTHETIC_DATA_ONLY</dd></div></dl>
              <nav><a href="/media-evidence-reproduction.md">{locale === "zh" ? "查看复现说明" : "Reproduction guide"}<span>→</span></a><a href={`${industry}#capability-boundaries`}>{locale === "zh" ? "查看项目边界" : "Project boundaries"}<span>→</span></a><a href="/media-evidence-profile.json">{locale === "zh" ? "读取机器配置" : "Machine profile"}<span>→</span></a></nav>
            </div>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
