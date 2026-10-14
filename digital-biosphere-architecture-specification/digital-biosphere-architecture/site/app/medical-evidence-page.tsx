"use client";

import { useState } from "react";
import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";
import styles from "./medical-evidence/medical-evidence.module.css";

const SAMPLE_UDI = "999.TEST.UDI.DICOM.0001";
const DIRECTION_SOURCE =
  "https://github.com/joy7758/titmas/tree/292e83aaafa4ada5a6089bcde7bbebf0e70045b4";

const copy = {
  zh: {
    breadcrumb: ["TITMAS 首页", "医疗证据基础设施", "参考 Demo"],
    eyebrow: "REFERENCE DEMO / 医疗证据方向",
    title: "UDI-DICOM Evidence Validator Demo",
    lead: "这是 TITMAS 医疗证据方向的第一个参考实现：输入明确的模拟 UDI，查看设备身份、影像对象与外部证据之间的引用关系如何表达。",
    banner: "概念演示 · 仅含模拟数据 · 非生产就绪 · 不代表真实合规或认证",
    label: "模拟 UDI",
    helper: "仅在当前浏览器中使用；不会上传，也不会查询真实登记库。",
    button: "展开模拟验证报告",
    reset: "重置",
    idle: "等待验证",
    closed: "SYNTHETIC_REFERENCE_PASS",
    invalid: "仅允许使用以 999.TEST. 开头的模拟标识符。",
    steps: [
      ["Identity", "设备身份", "解析模拟 UDI，并建立设备身份锚点。"],
      ["Imaging", "影像对象", "检查 DICOM 元数据与身份引用的映射。"],
      ["Evidence", "外部证据", "检查 Manifest 对影像与证据引用的闭合。"],
    ],
    resultTitle: "三段模拟证据关系",
    resultBody: "该界面只是解释预设模拟数据之间的引用关系，不执行医疗 Validator，也不评价设备、临床流程或 AI 决策是否安全、正确或合规。",
    flow: ["Synthetic DICOM Metadata + UDI Evidence Manifest", "Reference UI", "Evidence Receipt", "Verification Report"],
    output: [["Evidence Status", "SYNTHETIC PASS"], ["Identity", "REFERENCE MATCH"], ["Registry", "NOT QUERIED"], ["Evidence Chain", "STRUCTURE COMPLETE"]],
    boundariesTitle: "这个 Demo 明确不证明什么",
    boundaries: ["不证明设备物理或临床安全", "不构成监管认证或合规背书", "不代表真实医院部署或生产就绪"],
    sourceCta: "查看已发布的方向文档",
  },
  en: {
    breadcrumb: ["TITMAS home", "Medical Evidence Infrastructure", "Reference demo"],
    eyebrow: "REFERENCE DEMO / MEDICAL EVIDENCE DIRECTION",
    title: "UDI-DICOM Evidence Validator Demo",
    lead: "The first reference implementation for the TITMAS medical evidence direction: enter an explicitly synthetic UDI to inspect references across device identity, an imaging object, and external evidence.",
    banner: "Concept demo · Synthetic data only · Not production-ready · No compliance or certification claim",
    label: "Synthetic UDI",
    helper: "Used only in this browser. Nothing is uploaded and no real registry is queried.",
    button: "Show synthetic verification report",
    reset: "Reset",
    idle: "Awaiting validation",
    closed: "SYNTHETIC_REFERENCE_PASS",
    invalid: "Use a synthetic identifier beginning with 999.TEST. only.",
    steps: [
      ["Identity", "Device identity", "Parse the synthetic UDI and establish an identity anchor."],
      ["Imaging", "Imaging object", "Check the mapping between DICOM metadata and the identity reference."],
      ["Evidence", "External evidence", "Check whether the Manifest closes its imaging and evidence references."],
    ],
    resultTitle: "Three-part synthetic evidence relationship",
    resultBody: "This interface only explains references in preset synthetic data. It does not implement a medical validator or assess whether a device, clinical workflow, or AI decision is safe, correct, or compliant.",
    flow: ["Synthetic DICOM Metadata + UDI Evidence Manifest", "Reference UI", "Evidence Receipt", "Verification Report"],
    output: [["Evidence Status", "SYNTHETIC PASS"], ["Identity", "REFERENCE MATCH"], ["Registry", "NOT QUERIED"], ["Evidence Chain", "STRUCTURE COMPLETE"]],
    boundariesTitle: "What this demo explicitly does not prove",
    boundaries: ["No physical or clinical safety claim", "No regulatory certification or compliance endorsement", "No real hospital deployment or production-readiness claim"],
    sourceCta: "Read the published direction documents",
  },
} as const;

export function MedicalEvidencePage({ locale }: { locale: Locale }) {
  const c = copy[locale];
  const root = locale === "zh" ? "/" : "/en/";
  const industry = locale === "zh" ? "/industry/medical-evidence/" : "/en/industry/medical-evidence/";
  const [udi, setUdi] = useState(SAMPLE_UDI);
  const [state, setState] = useState<"idle" | "complete" | "invalid">("idle");

  function validate() {
    setState(udi.trim().startsWith("999.TEST.") ? "complete" : "invalid");
  }

  function reset() {
    setUdi(SAMPLE_UDI);
    setState("idle");
  }

  return (
    <div className="site" lang={locale === "zh" ? "zh-CN" : "en"}>
      <Header locale={locale} section="medical" />
      <StructuredPageData
        locale={locale}
        path={locale === "zh" ? "/demo/medical-evidence/" : "/en/demo/medical-evidence/"}
        title={c.title}
        description={c.lead}
        type="TechArticle"
      />
      <main className={styles.page} id="main-content">
        <div className={styles.banner} role="note">{c.banner}</div>
        <section className={styles.hero}>
          <div className={styles.heroCopy}>
            <nav className={styles.breadcrumb} aria-label={locale === "zh" ? "面包屑导航" : "Breadcrumb"}>
              <a href={root}>{c.breadcrumb[0]}</a><span>/</span>
              <a href={industry}>{c.breadcrumb[1]}</a><span>/</span>
              <span aria-current="page">{c.breadcrumb[2]}</span>
            </nav>
            <p className={styles.eyebrow}>{c.eyebrow}</p>
            <h1>{c.title}</h1>
            <p className={styles.lead}>{c.lead}</p>
            <div className={styles.truthRow}>
              <code>MEDICAL_EVIDENCE_DIRECTION=DEVELOPMENT_DIRECTION</code>
              <code>SYNTHETIC_DATA_ONLY</code>
              <code>REAL_REGISTRY_LOOKUP=false</code>
              <code>VALIDATOR_IMPLEMENTED_HERE=false</code>
            </div>
          </div>

          <div className={styles.validator}>
            <ol className={styles.demoFlow} aria-label={locale === "zh" ? "参考 Demo 流程" : "Reference demo flow"}>
              {c.flow.map((item, index) => <li key={item}><span>0{index + 1}</span><strong>{item}</strong>{index < c.flow.length - 1 && <i>→</i>}</li>)}
            </ol>
            <label htmlFor="medical-evidence-udi">{c.label}</label>
            <div className={styles.inputRow}>
              <input
                id="medical-evidence-udi"
                value={udi}
                onChange={(event) => {
                  setUdi(event.target.value);
                  setState("idle");
                }}
                aria-describedby="medical-evidence-helper medical-evidence-status"
                autoComplete="off"
                spellCheck={false}
              />
              <button type="button" onClick={validate}>{c.button}</button>
            </div>
            <p id="medical-evidence-helper" className={styles.helper}>{c.helper}</p>
            {state === "invalid" && <p id="medical-evidence-status" className={styles.error} role="alert">{c.invalid}</p>}

            <ol className={styles.chain} aria-live="polite">
              {c.steps.map(([name, label, description], index) => (
                <li key={name} className={state === "complete" ? styles.complete : ""}>
                  <span className={styles.stepIndex}>0{index + 1}</span>
                  <div>
                    <code>{name}</code>
                    <strong>{label}</strong>
                    <p>{description}</p>
                  </div>
                  <span className={styles.stepState}>{state === "complete" ? "✓" : "·"}</span>
                </li>
              ))}
            </ol>

            <div className={`${styles.result} ${state === "complete" ? styles.resultVisible : ""}`}>
              <span>{state === "complete" ? c.closed : c.idle}</span>
              <strong>{c.resultTitle}</strong>
              <p>{c.resultBody}</p>
              {state === "complete" && (
                <dl className={styles.outputGrid}>
                  {c.output.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}
                </dl>
              )}
              {state === "complete" && <button type="button" onClick={reset}>{c.reset}</button>}
            </div>
          </div>
        </section>

        <section className={styles.boundaries}>
          <p>INTERPRETATION BOUNDARY</p>
          <h2>{c.boundariesTitle}</h2>
          <div>{c.boundaries.map((item) => <span key={item}>{item}</span>)}</div>
          <a className={styles.sourceLink} href={DIRECTION_SOURCE} target="_blank" rel="noreferrer">
            {c.sourceCta} <span>↗</span>
          </a>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
