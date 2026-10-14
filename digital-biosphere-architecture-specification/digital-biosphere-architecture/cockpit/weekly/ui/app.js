(() => {
  "use strict";
  const snapshot = JSON.parse(document.getElementById("weekly-snapshot").textContent);
  const el = (id) => document.getElementById(id);
  const text = (value, fallback = "") => value === undefined || value === null || value === "" ? fallback : String(value);
  const first = (...values) => values.find((value) => value !== undefined && value !== null && value !== "");
  const escapeHtml = (value) => text(value).replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const severity = (status) => {
    const value = text(status, "UNKNOWN").toUpperCase();
    if (["PASS", "STABLE", "NORMAL", "ADMITTED"].includes(value)) return ["good", "稳定"];
    if (value === "OBSERVED") return ["neutral", "已观察"];
    if (["ATTENTION", "FAIL", "BLOCKED", "CONFLICT_REQUIRES_REVIEW"].includes(value)) return ["warn", "需关注"];
    if (["BLIND_SPOT", "NOT_ASSESSED", "UNKNOWN", "DISCOVERY_UNAVAILABLE", "PASS_WITH_NOT_ASSESSED"].includes(value)) return ["unknown", "尚未完整评估"];
    return ["neutral", "已记录"];
  };
  const pill = (status, showCode = false) => {
    const [klass, label] = severity(status);
    const suffix = showCode ? ` · ${escapeHtml(status)}` : "";
    return `<span class="status-pill ${klass}">${escapeHtml(label)}${suffix}</span>`;
  };
  const localTime = (value) => {
    if (!value) return "观察时间未知";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return text(value);
    const parts = new Intl.DateTimeFormat("zh-CN", {
      timeZone: "Asia/Shanghai", year: "numeric", month: "long", day: "numeric",
      hour: "2-digit", minute: "2-digit", hour12: false
    }).formatToParts(date);
    const map = Object.fromEntries(parts.map((part) => [part.type, part.value]));
    return `${map.year}年${map.month}月${map.day}日 ${map.hour}:${map.minute}`;
  };

  const projects = snapshot.projects || snapshot.project_views || [];
  const discoveries = snapshot.discoveries || [];
  const decisions = snapshot.decisions || [];
  const changeGroups = Array.isArray(snapshot.changes)
    ? snapshot.changes
    : Object.entries(snapshot.changes || {}).flatMap(([group, items]) =>
        (items || []).map((item) => typeof item === "string" ? {group, summary:item} : {group, ...item}));
  const blindSpots = snapshot.blind_spots || [];
  const cells = snapshot.cell_runs || [];
  const counts = snapshot.counts || {};
  const memory = snapshot.memory || {};
  const capability = snapshot.capability_discovery || {};
  const capabilityHighlights = snapshot.capability_highlights || [];
  const capabilityGroups = snapshot.capability_groups || [];
  const livePilot = snapshot.mode === "LIVE_READ_ONLY_OBSERVATION_PILOT";
  const coverageStatus = first(snapshot.source_coverage_status, counts.source_not_assessed > 0 ? "PARTIAL" : "COMPLETE");

  el("pilot-indicator").textContent = livePilot ? "实时只读试点" : "保留快照 Demo";

  const [overallClass] = severity(snapshot.overall_status);
  el("overall-signal").innerHTML = coverageStatus === "PARTIAL" ? `<span class="status-pill ${overallClass}">需关注</span><div style="margin-top:16px">部分检查尚未完成</div>` : `<span class="status-pill ${overallClass}">已完成</span><div style="margin-top:16px">本轮来源覆盖完整</div>`;
  el("weekly-sentence").textContent = text(snapshot.weekly_sentence_zh);
  el("hero-metrics").innerHTML = [
    ["项目", projects.length],
    ["实时来源", first(counts.live_source_success, 0)],
    ["未评估来源", first(counts.source_not_assessed, 0)],
    ["来源覆盖", coverageStatus],
    ["试点状态", first(snapshot.pilot_status, "NOT_APPLICABLE")],
    ["发现状态", first(snapshot.discovery_state, "UNKNOWN")],
    ["上轮制品", memory.PREVIOUS_LIVE_ARTIFACT_LOADED === true ? "已读取" : "未读取"],
    ["依赖高危", first(snapshot.dependency_audit_state?.live_candidate_high_count, "未评估")]
  ].map(([label, value]) => `<div class="metric"><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>`).join("");
  const firstDecision = decisions[0] || {};
  el("hero-decision").innerHTML = `<strong>最先查看：</strong>${escapeHtml(first(firstDecision.title_zh, "当前没有登记的决定"))}`;
  el("as-of").textContent = `观察时间 ${localTime(first(snapshot.observed_at, snapshot.as_of))}`;

  el("decision-list").innerHTML = decisions.length ? decisions.map((item, index) => `
    <article class="decision-card">
      <div class="meta-row"><span>决定 ${String(index + 1).padStart(2, "0")}</span><span>需人工判断</span></div>
      <h3>${escapeHtml(first(item.title_zh, item.title, item.decision_needed, "待人工决定"))}</h3>
      <p>${escapeHtml(first(item.why_zh, item.why, item.summary, item.human_explanation, "查看来源证据后决定。"))}</p>
      <small>来源：${escapeHtml(first(item.source_cell_id, snapshot.decisions_source, "HANDOFF_CELL"))}</small>
    </article>`).join("") : `<article class="decision-card"><h3>本周没有登记的决定</h3><p>这不表示没有风险；请同时查看盲区。</p></article>`;

  const rawQueries = snapshot.preset_queries || [
    {question:"本周需要决定什么？", answer:"查看待决定事项。"},
    {question:"本周收集到什么信号？", answer:"查看本周发现信号与准入标签。"},
    {question:"哪些事项仍是盲区？", answer:"查看检查盲区。"}
  ];
  const querySource = Array.isArray(rawQueries)
    ? rawQueries
    : Object.entries(rawQueries).map(([question, answer]) => ({question, answer}));
  el("preset-query").innerHTML = querySource.map((item, index) => `
    <option value="${index}">${escapeHtml(item.question)}</option>`).join("");
  el("query-answer").textContent = querySource[0] ? querySource[0].answer : "当前快照没有预设回答。";
  el("run-query").addEventListener("click", () => {
    const selected = querySource[Number(el("preset-query").value)];
    el("query-answer").textContent = selected ? selected.answer : "当前快照没有对应回答。";
  });

  el("discovery-list").innerHTML = discoveries.slice(0, 9).map((item) => `
    <article class="signal-card">
      <span class="status-pill neutral">${escapeHtml(first(item.admission_label_zh, "待人工确认候选"))}</span>
      <h3>${escapeHtml(first(item.title_zh, item.display_name_zh, item.display_name, item.subject, item.title, item.project_id, "发现信号"))}</h3>
      <p>${escapeHtml(first(item.details_zh, item.note, item.human_explanation, "没有附加说明。"))}</p>
      <small>观察状态：${escapeHtml(first(item.observed_state, item.current_state, item.status, "UNKNOWN"))}</small>
    </article>`).join("") || `<p>当前没有登记的发现信号。</p>`;

  if (Object.keys(capability).length) {
    el("capability-discovery-panel").hidden = false;
    el("capability-summary").innerHTML = `
      <div class="meta-row"><span>External Capability Discovery · 外部能力发现</span><span>AC-1 Reference Only</span></div>
      <h3>自动发现与参考吸收</h3>
      <p>${escapeHtml(first(capability.human_summary_zh, "本轮没有可用摘要。"))}</p>
      <div class="capability-metrics">
        ${[
          ["原始候选", capability.raw_candidate_count || 0],
          ["新参考", capability.new_reference_count || 0],
          ["更新", capability.updated_reference_count || 0],
          ["冲突", capability.conflict_count || 0],
          ["未评估来源", capability.source_not_assessed_count || 0],
          ["代码采用", capability.code_adopted || 0],
          ["运行时变化", capability.runtime_changed ? "是" : "否"]
        ].map(([label, value]) => `<span><strong>${escapeHtml(value)}</strong>${escapeHtml(label)}</span>`).join("")}
      </div>`;
    const highlights = capabilityHighlights.slice(0, 5).map((item) => `
      <article class="signal-card">
        <span class="status-pill neutral">${escapeHtml(first(item.observation_state, "CONTINUING_REFERENCE"))}</span>
        <h3>${escapeHtml(first(item.name, item.candidate_id))}</h3>
        <p>${escapeHtml(first(item.capability_group, "OTHER_OR_UNCLASSIFIED"))}</p>
        <small>身份：${escapeHtml(first(item.identity_status, "UNKNOWN"))} · AC-2：${escapeHtml(first(item.ac2_readiness_status, "NOT_READY"))}</small>
      </article>`).join("");
    const groups = capabilityGroups.map((group) => `
      <div class="cell-row"><strong>${escapeHtml(group.group)}</strong><br>${escapeHtml((group.members || []).join(" · "))}</div>`).join("");
    el("capability-groups").innerHTML = highlights + groups || "<p>没有可展示的能力组。</p>";
  }

  el("change-list").innerHTML = changeGroups.map((item) => `
    <article class="timeline-item">
      <time>${escapeHtml(first(item.observed_at, snapshot.observed_at, snapshot.as_of))}</time>
      <div><h3>${escapeHtml(item.group === "observed_this_week" ? "本周发生" : "尚不能形成周间趋势")}</h3><p>${escapeHtml(first(item.summary, item.title_zh, "没有可用说明。"))}</p></div>
    </article>`).join("") || `<article class="timeline-item"><time>${escapeHtml(first(snapshot.observed_at, snapshot.as_of))}</time><div><h3>首次快照，无周间比较</h3><p>首次快照，尚不能判断这些信号是否相对于上周新增。</p></div></article>`;

  el("project-grid").innerHTML = projects.map((project, index) => `
    <article class="project-card">
      <span class="project-index">${String(index + 1).padStart(2, "0")}</span>
      <h3>${escapeHtml(first(project.display_name_zh, project.display_name, project.name, project.project_id))}</h3>
      <span class="source-label">${escapeHtml(first(project.source_label, "RETAINED_SNAPSHOT"))}</span>
      ${pill(first(project.status, project.state))}
      <p><strong>${escapeHtml(first(project.status_zh, "状态待解释"))}</strong><br>${escapeHtml(first(project.why_zh, project.human_summary, project.summary, project.explanation, "没有可用的人类解释。"))}<br><br>${escapeHtml(first(project.attention_zh, project.impact_zh, ""))}</p>
    </article>`).join("");

  el("blindspot-list").innerHTML = blindSpots.map((item) => `
    <article class="blindspot"><h3>${escapeHtml(first(item.title_zh, item.title, item.subject, "未评估盲区"))}</h3><p>${escapeHtml(first(item.impact_zh, item.human_explanation, item.summary, item.reason, "缺少足够证据。"))}</p></article>`).join("") || `<article class="blindspot"><h3>盲区清单为空</h3><p>空清单不构成全面覆盖证明。</p></article>`;

  const projectEvidence = projects.map((project) => `<div class="cell-row">项目标识 · ${escapeHtml(first(project.project_id))}<br>证据 · ${escapeHtml((project.technical_evidence || []).join(" · "))}</div>`).join("");
  const cellEvidence = cells.map((cell) => `<div class="cell-row">细胞标识 · ${escapeHtml(first(cell.cell_id, cell.id))}<br>${pill(first(cell.status), true)}</div>`).join("");
  el("technical-evidence").innerHTML = `
    <div class="cell-row">快照编号 · ${escapeHtml(snapshot.snapshot_id)}</div>
    <div class="cell-row">机器总体状态 · ${escapeHtml(snapshot.overall_status)}</div>
    <div class="cell-row">工作流执行状态 · ${escapeHtml(first(snapshot.workflow_execution_status, "NOT_APPLICABLE"))}</div>
    <div class="cell-row">来源覆盖状态 · ${escapeHtml(coverageStatus)}</div>
    <div class="cell-row">试点状态 · ${escapeHtml(first(snapshot.pilot_status, "NOT_APPLICABLE"))}</div>
    <div class="cell-row">结果投影一致 · ${escapeHtml(first(snapshot.result_projection_consistent, "NOT_APPLICABLE"))}</div>
    <div class="cell-row">原始观察时间 · ${escapeHtml(snapshot.observed_at)}</div>
    <div class="cell-row">发现可用性 · ${escapeHtml(first(snapshot.discovery_state, "UNKNOWN"))}</div>
    <div class="cell-row">Memory · ${escapeHtml(first(memory.status, "NOT_ASSESSED"))}</div>
    <div class="cell-row">外部能力发现 · ${escapeHtml(first(capability.status, "NOT_APPLICABLE"))}</div>
    <div class="cell-row">自动化边界 · ${escapeHtml(first(capability.automation_scope, "NOT_APPLICABLE"))}</div>
    <div class="cell-row">代码采用 · ${escapeHtml(first(capability.code_adopted, 0))}</div>
    <div class="cell-row">运行时变化 · ${escapeHtml(first(capability.runtime_changed, false))}</div>
    ${projectEvidence}${cellEvidence}`;
})();
