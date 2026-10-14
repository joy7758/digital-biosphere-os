import type { Locale } from "./site-content";
import { Footer, Header } from "./site-shell";
import { StructuredPageData } from "./structured-page-data";

const wheelUrl =
  "https://redcrag.cn/downloads/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl";

const copy = {
  zh: {
    lang: "zh-CN",
    kicker: "COMMERCIAL EVALUATION / 商业评估",
    title: "商业评估包 v0.2",
    lead: "公开、只读、无副作用的执行可追责评估入口，已通过双 Provider、四角色智能体首次运行验证。",
    status: "4/4 智能体推荐用于离线评估；4/4 拒绝生产采购",
    start: "10 分钟开始",
    install: "在独立 Python 环境中安装公开 Developer Preview wheel，然后验证同源合成对象。",
    meaningTitle: "这个 PASS 证明什么",
    meaning: [
      "对象满足 DBOS v0.1 本地结构约束",
      "没有声明被禁止的治理副作用",
      "对象内部引用结构一致",
      "Validator 没有修改输入对象",
    ],
    limitsTitle: "这个 PASS 不证明什么",
    limits: [
      "不证明 Entity 真实存在、已经注册或激活",
      "不授予 Capability、Authority 或 Permission",
      "不把 Evidence 提升为 Truth",
      "不构成生产发布、安全认证、客户采用或 SLA",
    ],
    resourcesTitle: "完整资料",
    resourcesLead: "以下文件直接由本次远端验证过的 DBA 源码生成并随网站发布。",
    boundary:
      "Commercial Evaluation Pack 表示可独立评估，不表示已经存在可购买的生产商业产品。",
    back: "返回首页",
  },
  en: {
    lang: "en",
    kicker: "COMMERCIAL EVALUATION",
    title: "Commercial Evaluation Pack v0.2",
    lead: "A public, read-only, side-effect-free execution-accountability evaluation entry validated by four agent roles across two providers.",
    status: "4/4 recommend offline evaluation; 4/4 reject production purchase",
    start: "Start in 10 minutes",
    install: "Install the public Developer Preview wheel in an isolated Python environment, then validate the same-origin synthetic object.",
    meaningTitle: "What PASS establishes",
    meaning: [
      "The object satisfies local DBOS v0.1 structural constraints",
      "No prohibited governance side effect is declared",
      "Embedded references are locally consistent",
      "The validator does not mutate the input",
    ],
    limitsTitle: "What PASS does not establish",
    limits: [
      "No real Entity existence, registration, or activation",
      "No Capability, Authority, or Permission grant",
      "No promotion of Evidence into Truth",
      "No production release, certification, customer adoption, or SLA",
    ],
    resourcesTitle: "Complete materials",
    resourcesLead: "These files are generated from the remotely validated DBA source and shipped with this website.",
    boundary:
      "Commercial Evaluation Pack means independently evaluable. It does not mean an available production commercial offering.",
    back: "Back to home",
  },
} as const;

const resources = [
  ["Latest machine manifest", "/TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.json"],
  ["Evaluation guide", "/TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.md"],
  ["10-minute First Run", "/TITMAS-FIRST-RUN-v0.1.md"],
  ["Agent First Run report", "/TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-REPORT-v0.1.md"],
  ["Composite machine result", "/commercial-evaluation-agent-first-run/composite-result.v0.1.json"],
  ["Technical receipt", "/commercial-evaluation-agent-first-run/technical-first-run-receipt.v0.1.json"],
  ["JSON Schema", "/architecture/schemas/titmas-commercial-evaluation-pack.schema.v0.2.json"],
  ["Synthetic Entity Object", "/examples/titmas-first-run/entity-object.synthetic.v0.1.json"],
] as const;

export function CommercialEvaluationPage({ locale }: { locale: Locale }) {
  const c = copy[locale];
  const home = locale === "zh" ? "/" : "/en/";

  return (
    <div className="site" lang={c.lang}>
      <Header locale={locale} section="commercial" />
      <StructuredPageData
        locale={locale}
        path={locale === "zh" ? "/commercial-evaluation/" : "/en/commercial-evaluation/"}
        title={c.title}
        description={c.lead}
        type="TechArticle"
      />
      <main id="main-content">
        <section className="evaluation-hero">
          <div className="section-shell">
            <p className="section-kicker">{c.kicker}</p>
            <h1>{c.title}</h1>
            <p>{c.lead}</p>
            <div className="evaluation-status">
              <span>PASS</span>
              <code>AGENT_FIRST_RUN_VALIDATED</code>
              <code>AVAILABLE_OFFERING=false</code>
              <strong>{c.status}</strong>
            </div>
          </div>
        </section>

        <section className="section evaluation-start">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">FIRST RUN</p>
              <h2>{c.start}</h2>
              <p>{c.install}</p>
            </div>
            <pre>
              <code>{`python3 -m venv .venv-titmas
. .venv-titmas/bin/activate
python -m pip install ${wheelUrl}
curl -fsS https://redcrag.cn/examples/titmas-first-run/entity-object.synthetic.v0.1.json -o entity.json
dbos-validate entity.json`}</code>
            </pre>
          </div>
        </section>

        <section className="section evaluation-boundaries">
          <div className="section-shell evaluation-columns">
            <article>
              <span className="evaluation-label evaluation-label-pass">PASS MEANS</span>
              <h2>{c.meaningTitle}</h2>
              <ul>{c.meaning.map((item) => <li key={item}>{item}</li>)}</ul>
            </article>
            <article>
              <span className="evaluation-label evaluation-label-limit">PASS ≠ TRUTH</span>
              <h2>{c.limitsTitle}</h2>
              <ul>{c.limits.map((item) => <li key={item}>{item}</li>)}</ul>
            </article>
          </div>
        </section>

        <section className="section evaluation-resources">
          <div className="section-shell">
            <div className="section-heading">
              <p className="section-kicker">AGENT-READABLE</p>
              <h2>{c.resourcesTitle}</h2>
              <p>{c.resourcesLead}</p>
            </div>
            <div className="evaluation-resource-list">
              {resources.map(([label, href]) => (
                <a href={href} key={href}>
                  <span>{label}</span>
                  <code>{href}</code>
                  <b>↗</b>
                </a>
              ))}
            </div>
            <p className="evaluation-boundary-note">{c.boundary}</p>
            <a className="text-link" href={home}>{c.back}<span>→</span></a>
          </div>
        </section>
      </main>
      <Footer locale={locale} />
    </div>
  );
}
