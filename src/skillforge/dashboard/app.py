"""Lightweight Offline Local Dashboard for SkillForge."""

import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from skillforge.database.repository import SkillRepository
from skillforge.mcp_server.tools import SkillForgeTools


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SkillForge - Local Intelligent Skill Library</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --badge-inst: #10b981;
      --badge-off: #64748b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 24px; line-height: 1.5; }
    .container { max-width: 1200px; margin: 0 auto; }
    header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
    h1 { font-size: 24px; font-weight: 700; color: var(--accent); }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .stat-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; text-align: center; }
    .stat-val { font-size: 28px; font-weight: 700; color: var(--accent); }
    .stat-label { font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    .panel { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 24px; }
    .panel h2 { font-size: 18px; margin-bottom: 12px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
    .search-box { display: flex; gap: 8px; margin-bottom: 16px; }
    input[type="text"] { flex: 1; background: #0b1120; border: 1px solid var(--border); color: var(--text); padding: 10px 14px; border-radius: 6px; font-size: 14px; }
    button { background: var(--accent); color: #0b1120; border: none; padding: 10px 20px; font-weight: 600; border-radius: 6px; cursor: pointer; transition: 0.2s; }
    button:hover { background: var(--accent-hover); }
    .skill-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 14px; }
    .skill-card { background: #0b1120; border: 1px solid var(--border); border-radius: 6px; padding: 14px; }
    .skill-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
    .skill-title { font-weight: 600; font-size: 16px; color: #e2e8f0; }
    .badge { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
    .badge-installed { background: #064e3b; color: #34d399; }
    .badge-offline { background: #334155; color: #cbd5e1; }
    .skill-desc { font-size: 13px; color: var(--muted); margin-bottom: 10px; height: 40px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
    .skill-meta { font-size: 11px; color: #64748b; display: flex; justify-content: space-between; border-top: 1px solid #1e293b; padding-top: 6px; }
    .rec-box { background: #0b1120; border: 1px dashed var(--accent); border-radius: 6px; padding: 16px; margin-top: 12px; white-space: pre-wrap; font-family: monospace; font-size: 13px; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>SkillForge Dashboard</h1>
        <p style="color: var(--muted); font-size: 13px;">Local Intelligent Skill Library & Context-Aware Router</p>
      </div>
      <div>
        <span class="badge badge-installed">Offline Local Registry (127.0.0.1)</span>
      </div>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-val">{TOTAL_SKILLS}</div>
        <div class="stat-label">Total Indexed Skills</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{INSTALLED_COUNT}</div>
        <div class="stat-label">Actively Installed</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{OFFLINE_COUNT}</div>
        <div class="stat-label">Offline Skill Book</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{CATEGORIES_COUNT}</div>
        <div class="stat-label">Categories</div>
      </div>
    </div>

    <!-- Recommendation Preview Sandbox -->
    <div class="panel">
      <h2>Context-Aware Recommendation Sandbox</h2>
      <p style="color: var(--muted); font-size: 13px; margin-bottom: 12px;">Simulate Antigravity skill selection with real project architecture context.</p>
      <form method="GET" action="/">
        <div class="search-box">
          <input type="text" name="task" placeholder="Enter task (e.g. Build a Python FastAPI service with pytest or React Next.js UI)" value="{TASK_VALUE}">
          <input type="text" name="project" placeholder="Project directory path (optional)" value="{PROJECT_VALUE}" style="max-width: 300px;">
          <button type="submit">Recommend</button>
        </div>
      </form>
      {RECOMMENDATION_OUTPUT}
    </div>

    <!-- Catalog Explorer -->
    <div class="panel">
      <h2>Indexed Skills Catalog</h2>
      <div class="skill-list">
        {SKILL_CARDS}
      </div>
    </div>
  </div>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    repo: SkillRepository = None
    tools: SkillForgeTools = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        task = params.get("task", [""])[0]
        project = params.get("project", [""])[0]

        stats = self.repo.get_stats()
        total_skills = stats.get("total_skills", 0)

        by_source = stats.get("by_source", {})
        installed_count = sum(v for k, v in by_source.items() if "installed" in k)
        offline_count = by_source.get("offline_book", 0)
        categories_count = len(stats.get("by_category", {}))

        # Handle recommendation query
        rec_html = ""
        if task:
            res = self.tools.recommend_skills(task=task, project_path=project if project else None)
            rec_html = f"<div class='rec-box'><strong>Recommended Output:</strong>\n\n{res['explanation']}</div>"

        # List skills sample (first 40)
        skills = self.repo.list_skills(limit=40)
        cards = []
        for s in skills:
            is_inst = "installed" in s.source_type.value
            badge_class = "badge-installed" if is_inst else "badge-offline"
            badge_text = "Installed" if is_inst else "Offline Book"
            cards.append(f"""
            <div class="skill-card">
              <div class="skill-header">
                <span class="skill-title">{s.name}</span>
                <span class="badge {badge_class}">{badge_text}</span>
              </div>
              <div class="skill-desc">{s.description or "No description provided."}</div>
              <div class="skill-meta">
                <span>Cat: {s.category}</span>
                <span>Quality: {int(s.quality_score * 100)}%</span>
              </div>
            </div>
            """)

        html = (
            HTML_TEMPLATE
            .replace("{TOTAL_SKILLS}", str(total_skills))
            .replace("{INSTALLED_COUNT}", str(installed_count))
            .replace("{OFFLINE_COUNT}", str(offline_count))
            .replace("{CATEGORIES_COUNT}", str(categories_count))
            .replace("{TASK_VALUE}", task)
            .replace("{PROJECT_VALUE}", project)
            .replace("{RECOMMENDATION_OUTPUT}", rec_html)
            .replace("{SKILL_CARDS}", "\n".join(cards))
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        # Quiet standard logging
        pass


def get_db_path() -> Path:
    env_p = os.environ.get("SKILLFORGE_DB_PATH")
    if env_p and Path(env_p).is_file():
        return Path(env_p)
    # Target repository root: D:\setup\antigravity-skillforge\data\registry.db
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    return repo_root / "data" / "registry.db"


def start_dashboard(host: str = "127.0.0.1", port: int = 8765):
    db_path = get_db_path()
    repo = SkillRepository(db_path)
    tools = SkillForgeTools(repo)

    DashboardHandler.repo = repo
    DashboardHandler.tools = tools

    server_address = (host, port)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"SkillForge local dashboard running at http://{host}:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
        httpd.server_close()

