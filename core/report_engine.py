"""
Report Engine
Generates HTML, JSON, and Markdown reports.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

REPORTS_DIR = Path(__file__).parent.parent / "reports"


class ReportEngine:
    def __init__(self):
        REPORTS_DIR.mkdir(exist_ok=True)

    def generate(self, target: str, findings: List[Dict], endpoints: List[str],
                 workflows: List[Dict], elapsed: float) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"m7bla_report_{timestamp}"

        self._write_json(base_name, target, findings, endpoints, workflows, elapsed)
        html_path = self._write_html(base_name, target, findings, endpoints, workflows, elapsed)
        self._write_markdown(base_name, target, findings, endpoints, workflows, elapsed)

        return str(html_path)

    def _write_json(self, name, target, findings, endpoints, workflows, elapsed):
        data = {
            "tool": "m7bla",
            "author": "Sharlix | Milkyway Intelligence",
            "target": target,
            "scan_date": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "summary": {
                "endpoints_discovered": len(endpoints),
                "workflows_mapped": len(workflows),
                "total_findings": len(findings),
                "high": sum(1 for f in findings if f.get("severity") == "HIGH"),
                "medium": sum(1 for f in findings if f.get("severity") == "MEDIUM"),
                "low": sum(1 for f in findings if f.get("severity") == "LOW"),
            },
            "findings": findings,
            "endpoints": endpoints,
            "workflows": workflows,
        }
        path = REPORTS_DIR / f"{name}.json"
        path.write_text(json.dumps(data, indent=2))
        return path

    def _write_html(self, name, target, findings, endpoints, workflows, elapsed):
        high = [f for f in findings if f.get("severity") == "HIGH"]
        medium = [f for f in findings if f.get("severity") == "MEDIUM"]
        low = [f for f in findings if f.get("severity") == "LOW"]

        findings_html = ""
        for f in findings:
            color = {"HIGH": "#ff4444", "MEDIUM": "#ffaa00", "LOW": "#44ff88"}.get(f.get("severity", "LOW"), "#44ff88")
            findings_html += f"""
            <div class="finding">
                <div class="finding-header">
                    <span class="severity" style="color:{color}">[{f.get('severity','?')}]</span>
                    <span class="finding-name">{f.get('name','Unknown Finding')}</span>
                </div>
                <div class="finding-detail">
                    <b>Endpoint:</b> {f.get('endpoint', 'N/A')}<br>
                    <b>Description:</b> {f.get('description', 'N/A')}<br>
                    <b>Payload:</b> <code>{f.get('payload', 'N/A')}</code><br>
                    <b>Impact:</b> {f.get('impact', 'N/A')}
                </div>
            </div>"""

        endpoints_html = "\n".join(f'<li><code>{ep}</code></li>' for ep in endpoints)
        workflow_html = ""
        for i, wf in enumerate(workflows):
            workflow_html += f'<span class="wf-stage">{wf["name"]}</span>'
            if i < len(workflows) - 1:
                workflow_html += ' <span class="arrow">↓</span> '

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>m7bla Report - {target}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

  :root {{
    --bg: #050a0e;
    --surface: #0a1520;
    --border: #00ff9940;
    --green: #00ff99;
    --red: #ff4444;
    --yellow: #ffaa00;
    --blue: #00aaff;
    --text: #c0e0d0;
    --dim: #4a7060;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    padding: 24px;
    min-height: 100vh;
  }}

  .header {{
    border: 1px solid var(--green);
    padding: 20px 28px;
    margin-bottom: 24px;
    position: relative;
    background: linear-gradient(135deg, #0a1520, #050a0e);
  }}

  .header::before {{
    content: '';
    position: absolute;
    top: -1px; left: 20px;
    width: 60px; height: 3px;
    background: var(--green);
  }}

  .logo {{ font-size: 2.2rem; font-weight: 700; color: var(--green); font-family: 'Rajdhani', sans-serif; letter-spacing: 4px; }}
  .tagline {{ color: var(--dim); font-size: 0.85rem; margin-top: 4px; }}
  .meta {{ margin-top: 12px; font-size: 0.8rem; color: var(--dim); }}
  .meta span {{ color: var(--text); }}

  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 24px; }}

  .stat-card {{
    border: 1px solid var(--border);
    padding: 16px;
    background: var(--surface);
    text-align: center;
  }}

  .stat-value {{ font-size: 2rem; font-weight: 700; font-family: 'Rajdhani', sans-serif; }}
  .stat-label {{ font-size: 0.75rem; color: var(--dim); margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }}

  .section {{ margin-bottom: 28px; }}

  .section-title {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--green);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }}

  .finding {{
    border: 1px solid var(--border);
    margin-bottom: 12px;
    background: var(--surface);
  }}

  .finding-header {{
    padding: 10px 16px;
    background: #0a1a10;
    border-bottom: 1px solid var(--border);
    display: flex; gap: 12px; align-items: center;
  }}

  .severity {{ font-weight: 700; font-family: 'Rajdhani', sans-serif; font-size: 0.9rem; }}
  .finding-name {{ font-size: 0.95rem; }}
  .finding-detail {{ padding: 14px 16px; font-size: 0.85rem; line-height: 1.8; color: var(--dim); }}
  .finding-detail b {{ color: var(--text); }}

  code {{
    background: #0a1a10;
    color: var(--green);
    padding: 2px 6px;
    font-size: 0.85em;
    border: 1px solid var(--border);
  }}

  .endpoint-list {{ list-style: none; display: flex; flex-wrap: wrap; gap: 8px; }}
  .endpoint-list li code {{ font-size: 0.8rem; }}

  .workflow-flow {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }}
  .wf-stage {{
    background: #0a1520;
    border: 1px solid var(--green);
    color: var(--green);
    padding: 6px 14px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 1px;
  }}

  .arrow {{ color: var(--dim); font-size: 1.2rem; }}

  .no-findings {{ color: var(--dim); font-style: italic; }}

  .footer {{ border-top: 1px solid var(--border); padding-top: 16px; margin-top: 24px; font-size: 0.75rem; color: var(--dim); text-align: center; }}
</style>
</head>
<body>

<div class="header">
  <div class="logo">M7BLA</div>
  <div class="tagline">Business Logic Abuse Framework — Milkyway Intelligence</div>
  <div class="meta">
    Target: <span>{target}</span> &nbsp;|&nbsp;
    Date: <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span> &nbsp;|&nbsp;
    Duration: <span>{round(elapsed, 1)}s</span> &nbsp;|&nbsp;
    Author: <span>Sharlix</span>
  </div>
</div>

<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-value" style="color:#00ff99">{len(endpoints)}</div>
    <div class="stat-label">Endpoints</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" style="color:#00aaff">{len(workflows)}</div>
    <div class="stat-label">Workflows</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" style="color:#ff4444">{len(high)}</div>
    <div class="stat-label">High</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" style="color:#ffaa00">{len(medium)}</div>
    <div class="stat-label">Medium</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" style="color:#44ff88">{len(low)}</div>
    <div class="stat-label">Low</div>
  </div>
</div>

<div class="section">
  <div class="section-title">Workflow Map</div>
  <div class="workflow-flow">
    {workflow_html if workflow_html else '<span class="no-findings">No workflows mapped</span>'}
  </div>
</div>

<div class="section">
  <div class="section-title">Findings</div>
  {findings_html if findings_html else '<p class="no-findings">No findings recorded in this scan.</p>'}
</div>

<div class="section">
  <div class="section-title">Discovered Endpoints</div>
  <ul class="endpoint-list">
    {endpoints_html if endpoints_html else '<li class="no-findings">None</li>'}
  </ul>
</div>

<div class="footer">
  Generated by m7bla v1.0.0 &mdash; Milkyway Intelligence &mdash; For authorized testing only
</div>

</body>
</html>"""
        path = REPORTS_DIR / f"{name}.html"
        path.write_text(html)
        return path

    def _write_markdown(self, name, target, findings, endpoints, workflows, elapsed):
        lines = [
            "# m7bla Scan Report",
            f"**Target:** {target}  ",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Duration:** {round(elapsed, 1)}s  ",
            f"**Author:** Sharlix | Milkyway Intelligence  ",
            "",
            "## Summary",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Endpoints Discovered | {len(endpoints)} |",
            f"| Workflows Mapped | {len(workflows)} |",
            f"| High Findings | {sum(1 for f in findings if f.get('severity')=='HIGH')} |",
            f"| Medium Findings | {sum(1 for f in findings if f.get('severity')=='MEDIUM')} |",
            f"| Low Findings | {sum(1 for f in findings if f.get('severity')=='LOW')} |",
            "",
            "## Findings",
        ]

        if findings:
            for f in findings:
                lines += [
                    f"### [{f.get('severity','?')}] {f.get('name','Unknown')}",
                    f"- **Endpoint:** `{f.get('endpoint', 'N/A')}`",
                    f"- **Description:** {f.get('description', 'N/A')}",
                    f"- **Payload:** `{f.get('payload', 'N/A')}`",
                    f"- **Impact:** {f.get('impact', 'N/A')}",
                    "",
                ]
        else:
            lines.append("_No findings recorded._")

        lines += ["", "## Endpoints", "```"]
        lines += endpoints
        lines.append("```")
        lines += ["", "---", "_Generated by m7bla v1.0.0 — For authorized testing only_"]

        path = REPORTS_DIR / f"{name}.md"
        path.write_text("\n".join(lines))
        return path
