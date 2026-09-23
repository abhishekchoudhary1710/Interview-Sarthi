const escape = value => String(value ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function assessmentText(report) {
  return [report.coverage || "", report.assessment_scope || "", ...(report.competencies || []).map(c =>
    `${c.label}: ${c.score === null ? "Not assessed" : `${c.score}/10 (${c.status})`}. ${c.explanation}${c.evidence_turns.length ? ` Evidence: transcript turns ${c.evidence_turns.join(", ")}.` : ""}`)].join("\n");
}

export function assessmentHtml(report, transcript = []) {
  if (!report.competencies) return "";
  return `<div class="card"><span class="label">Assessment coverage</span>
    <p>${escape(report.coverage)}</p><p class="muted">${escape(report.assessment_scope)}</p>
    ${report.competencies.map(c => `<div class="q"><h3>${escape(c.label)} · ${c.score === null ? "Not assessed" : `${escape(c.score)} / 10${c.status === "limited" ? " · Limited evidence" : ""}`}</h3>
      <p>${escape(c.explanation)}</p>
      ${c.evidence_turns.map(n => `<p class="said">Evidence (turn ${n}): ${escape(transcript[n - 1]?.text || "")}</p>`).join("")}</div>`).join("")}</div>`;
}
