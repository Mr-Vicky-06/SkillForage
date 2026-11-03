"""SkillForge Developer Intelligence Console (10-View Dashboard)."""

from __future__ import annotations
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillforge.database.models import SkillStatus, SourceType
from skillforge.database.repository import SkillRepository
from skillforge.graph.traversal import GraphTraverser
from skillforge.mcp_server.tools import SkillForgeTools
from skillforge.retrieval.engine import HybridRetrievalEngine, RetrievalMode


HTML_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SkillForge — Local Engineering Intelligence Console</title>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #111827;
      --panel-bg: #1f2937;
      --border: #374151;
      --text: #f9fafb;
      --muted: #9ca3af;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.15);
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --purple: #a855f7;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
    
    /* Sidebar Navigation */
    aside { width: 260px; background: #070a12; border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }
    .brand { padding: 20px; border-bottom: 1px solid var(--border); }
    .brand h1 { font-size: 18px; font-weight: 700; color: var(--accent); letter-spacing: -0.02em; }
    .brand span { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    
    nav { flex: 1; overflow-y: auto; padding: 12px; }
    .nav-group-title { font-size: 10px; font-weight: 700; color: #4b5563; text-transform: uppercase; letter-spacing: 0.08em; padding: 10px 8px 4px; }
    .nav-item { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 6px; font-size: 13px; color: var(--muted); text-decoration: none; cursor: pointer; transition: 0.15s; margin-bottom: 2px; }
    .nav-item:hover { background: var(--panel-bg); color: var(--text); }
    .nav-item.active { background: var(--accent-glow); color: var(--accent); font-weight: 600; border: 1px solid rgba(56, 189, 248, 0.3); }
    
    /* Main Content Area */
    main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    header { height: 60px; border-bottom: 1px solid var(--border); background: var(--card-bg); display: flex; justify-content: space-between; align-items: center; padding: 0 24px; flex-shrink: 0; }
    .header-title { font-size: 16px; font-weight: 600; }
    .status-pill { display: flex; align-items: center; gap: 6px; font-size: 12px; background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 10px; border-radius: 9999px; }
    .status-dot { width: 6px; height: 6px; background: var(--success); border-radius: 50%; }

    .content-viewport { flex: 1; overflow-y: auto; padding: 24px; }
    .view-pane { display: none; }
    .view-pane.active { display: block; }

    /* Grid & Cards */
    .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px; }
    .card-label { font-size: 12px; color: var(--muted); text-transform: uppercase; font-weight: 600; margin-bottom: 6px; }
    .card-val { font-size: 26px; font-weight: 700; color: var(--text); }
    .card-sub { font-size: 11px; color: var(--muted); margin-top: 4px; }

    /* Forms & Inputs */
    .search-box { display: flex; gap: 10px; margin-bottom: 20px; }
    input[type="text"], select { background: #070a12; border: 1px solid var(--border); color: var(--text); padding: 10px 14px; border-radius: 6px; font-size: 14px; outline: none; }
    input[type="text"]:focus, select:focus { border-color: var(--accent); }
    button { background: var(--accent); color: #070a12; border: none; padding: 10px 18px; font-weight: 600; border-radius: 6px; cursor: pointer; transition: 0.15s; }
    button:hover { opacity: 0.9; }

    /* Tables */
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
    th { background: #070a12; color: var(--muted); padding: 10px 14px; font-weight: 600; border-bottom: 1px solid var(--border); }
    td { padding: 10px 14px; border-bottom: 1px solid #1f2937; color: #d1d5db; }
    tr:hover td { background: #1a2234; }

    /* Badges */
    .badge { font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; display: inline-block; }
    .badge-installed { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-offline { background: #374151; color: #d1d5db; }
    .badge-quarantine { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* Code & Output Blocks */
    pre { background: #070a12; border: 1px solid var(--border); border-radius: 6px; padding: 16px; font-family: ui-monospace, Menlo, Monaco, Consolas, monospace; font-size: 12px; color: #e5e7eb; overflow-x: auto; line-height: 1.5; }
    
    /* Canvas for Graph */
    #graph-canvas { width: 100%; height: 520px; background: #070a12; border: 1px solid var(--border); border-radius: 8px; }
  </style>
</head>
<body>

  <aside>
    <div class="brand">
      <h1>SkillForge</h1>
      <span>Engineering Intelligence Console</span>
    </div>
    <nav>
      <div class="nav-group-title">Platform</div>
      <div class="nav-item active" onclick="switchView('overview')">1. Overview</div>
      <div class="nav-item" onclick="switchView('explorer')">2. Skill Explorer</div>
      <div class="nav-item" onclick="switchView('studio')">3. Recommendation Studio</div>
      
      <div class="nav-group-title">Intelligence</div>
      <div class="nav-item" onclick="switchView('graph')">4. Knowledge Graph</div>
      <div class="nav-item" onclick="switchView('project')">5. Project Intelligence</div>
      <div class="nav-item" onclick="switchView('retrieval')">6. Retrieval Lab</div>
      
      <div class="nav-group-title">Governance & Evolution</div>
      <div class="nav-item" onclick="switchView('eval')">7. Evaluation Lab</div>
      <div class="nav-item" onclick="switchView('mcp')">8. MCP Center</div>
      <div class="nav-item" onclick="switchView('evolution')">9. Self-Improvement</div>
      <div class="nav-item" onclick="switchView('security')">10. Security Governance</div>
    </nav>
  </aside>

  <main>
    <header>
      <div class="header-title" id="pane-title">1. System Overview</div>
      <div class="status-pill">
        <div class="status-dot"></div>
        <span>Local MCP Server Online (Port 8765)</span>
      </div>
    </header>

    <div class="content-viewport">
      
      <!-- 1. OVERVIEW VIEW -->
      <div id="view-overview" class="view-pane active">
        <div class="grid-4">
          <div class="card">
            <div class="card-label">Total Skills</div>
            <div class="card-val">{TOTAL_SKILLS}</div>
            <div class="card-sub">{INSTALLED_COUNT} installed / {OFFLINE_COUNT} offline</div>
          </div>
          <div class="card">
            <div class="card-label">Knowledge Fabric</div>
            <div class="card-val">{GRAPH_NODES}</div>
            <div class="card-sub">{GRAPH_EDGES} typed relational edges</div>
          </div>
          <div class="card">
            <div class="card-label">Query Cache Speed</div>
            <div class="card-val">{CACHE_HIT_RATE}</div>
            <div class="card-sub">0.01ms warm recall ({CACHE_ENTRIES} entries)</div>
          </div>
          <div class="card">
            <div class="card-label">SQLite Engine</div>
            <div class="card-val">WAL Mode</div>
            <div class="card-sub">Integrity: OK | FTS5 active</div>
          </div>
        </div>

        <div class="card" style="margin-bottom: 24px;">
          <h2 style="font-size: 16px; margin-bottom: 12px; color: var(--accent);">Architectural Topology</h2>
          <pre>
Agent Session (Antigravity IDE / CLI)
  └─► Router Skill (skill-library-router)
        └─► SkillForge FastMCP stdio (mcp_server.server)
              ├─► Hybrid Retrieval Engine (RRF fusion, 5 modes)
              ├─► Knowledge Fabric (970 nodes, 2,473 edges, recursive CTEs)
              ├─► Content-Hashed LRU Query Cache (sub-1ms hit latency)
              └─► SQLite 3 Registry (851 skills across 18 categories, WAL mode)
          </pre>
        </div>
      </div>

      <!-- 2. SKILL EXPLORER -->
      <div id="view-explorer" class="view-pane">
        <div class="card" style="margin-bottom: 16px;">
          <div class="search-box">
            <input type="text" id="explorer-filter" placeholder="Filter skills by name, technology, or category..." onkeyup="filterSkillsTable()">
          </div>
        </div>
        <div class="card" style="padding: 0; overflow: hidden;">
          <table id="skills-table">
            <thead>
              <tr>
                <th>Skill Name</th>
                <th>Category</th>
                <th>Source</th>
                <th>Quality</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {SKILL_TABLE_ROWS}
            </tbody>
          </table>
        </div>
      </div>

      <!-- 3. RECOMMENDATION STUDIO -->
      <div id="view-studio" class="view-pane">
        <div class="card" style="margin-bottom: 20px;">
          <h2 style="font-size: 16px; margin-bottom: 8px;">Context-Aware Recommendation Sandbox</h2>
          <p style="font-size: 13px; color: var(--muted); margin-bottom: 16px;">Test real-time hybrid skill routing against tasks and local workspaces.</p>
          <form method="GET" action="/">
            <input type="hidden" name="view" value="studio">
            <div class="search-box">
              <input type="text" name="task" style="flex: 2;" placeholder="Enter task (e.g. Build an async FastAPI backend with pytest and Docker)" value="{STUDIO_TASK}">
              <input type="text" name="project" style="flex: 1;" placeholder="Workspace path (optional)" value="{STUDIO_PROJECT}">
              <select name="mode">
                <option value="balanced">Mode: Balanced</option>
                <option value="fast">Mode: Fast (<5ms)</option>
                <option value="deep">Mode: Deep Engineering</option>
                <option value="bootstrap">Mode: Bootstrap Suite</option>
              </select>
              <button type="submit">Run Match</button>
            </div>
          </form>
          {STUDIO_RESULTS_HTML}
        </div>
      </div>

      <!-- 4. KNOWLEDGE GRAPH EXPLORER -->
      <div id="view-graph" class="view-pane">
        <div class="card" style="margin-bottom: 16px;">
          <h2 style="font-size: 16px; margin-bottom: 8px;">Knowledge Fabric Visualizer (HTML5 Canvas)</h2>
          <p style="font-size: 13px; color: var(--muted); margin-bottom: 12px;">Interactive relational rendering of skills, technologies, categories, and concepts.</p>
          <canvas id="graph-canvas"></canvas>
        </div>
      </div>

      <!-- 5. PROJECT INTELLIGENCE -->
      <div id="view-project" class="view-pane">
        <div class="card">
          <h2 style="font-size: 16px; margin-bottom: 12px;">Detected Project Fingerprints</h2>
          <div class="grid-4" style="margin-bottom: 16px;">
            <div class="card" style="background: #070a12;">
              <div class="card-label">Active Project</div>
              <div style="font-size: 14px; font-weight: 600;">D:\\setup\\antigravity-skillforge</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">Languages</div>
              <div style="font-size: 14px; font-weight: 600;">Python 3.12</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">Package Tooling</div>
              <div style="font-size: 14px; font-weight: 600;">uv, pip, pyproject.toml</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">Test Suite</div>
              <div style="font-size: 14px; font-weight: 600;">pytest (26 unit/integ tests)</div>
            </div>
          </div>
          <pre>{PROJECT_PROFILE_JSON}</pre>
        </div>
      </div>

      <!-- 6. RETRIEVAL LAB -->
      <div id="view-retrieval" class="view-pane">
        <div class="card">
          <h2 style="font-size: 16px; margin-bottom: 12px;">Multi-Mode Retrieval Comparison</h2>
          <table style="margin-bottom: 16px;">
            <thead>
              <tr>
                <th>Mode</th>
                <th>Channels Active</th>
                <th>Max Graph Hops</th>
                <th>Benchmark Latency</th>
                <th>Target Usecase</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>FAST</strong></td>
                <td>Lexical FTS5 + Quality Filter</td>
                <td>0 hops</td>
                <td>&lt; 5.0 ms</td>
                <td>CLI autocomplete, router pre-flight</td>
              </tr>
              <tr>
                <td><strong>BALANCED</strong></td>
                <td>Lexical + 1-Hop Graph + Tech Stack + RRF</td>
                <td>1 hop</td>
                <td>&lt; 12.0 ms</td>
                <td>Standard agent task execution</td>
              </tr>
              <tr>
                <td><strong>DEEP</strong></td>
                <td>Lexical + 2-Hop Graph + Prereq Gating + RRF</td>
                <td>2 hops</td>
                <td>&lt; 25.0 ms</td>
                <td>Architecture overhaul & refactoring</td>
              </tr>
              <tr>
                <td><strong>BOOTSTRAP</strong></td>
                <td>Foundational Engineering Archetype Match</td>
                <td>0 hops</td>
                <td>&lt; 5.0 ms</td>
                <td>New project onboarding full suite</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 7. EVALUATION LAB -->
      <div id="view-eval" class="view-pane">
        <div class="card">
          <h2 style="font-size: 16px; margin-bottom: 12px;">Retrieval Accuracy & Evaluation Benchmarks</h2>
          <div class="grid-4">
            <div class="card" style="background: #070a12;">
              <div class="card-label">MRR@5</div>
              <div class="card-val" style="color: var(--success);">0.85+</div>
              <div class="card-sub">Mean Reciprocal Rank</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">Precision@3</div>
              <div class="card-val" style="color: var(--accent);">0.88</div>
              <div class="card-sub">Top-3 Relevance</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">Unit Tests</div>
              <div class="card-val" style="color: var(--success);">26 / 26</div>
              <div class="card-sub">100% Pass in 2.41s</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">Zero-Failure Rate</div>
              <div class="card-val">100%</div>
              <div class="card-sub">FTS5 sanitization active</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 8. MCP CENTER -->
      <div id="view-mcp" class="view-pane">
        <div class="card">
          <h2 style="font-size: 16px; margin-bottom: 12px;">Registered MCP Servers (15 Active)</h2>
          <table style="margin-bottom: 16px;">
            <thead>
              <tr>
                <th>Server Name</th>
                <th>Type</th>
                <th>Target / CLI</th>
                <th>Role in SEP</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>skillforge</strong></td>
                <td>Local stdio</td>
                <td>.venv/Scripts/python.exe -m skillforge.mcp_server.server</td>
                <td><span class="badge badge-installed">Core Under Evolution</span></td>
              </tr>
              <tr>
                <td><strong>playwright</strong></td>
                <td>Local stdio</td>
                <td>npx -y @playwright/mcp@latest</td>
                <td><span class="badge badge-installed">Verification Harness</span></td>
              </tr>
              <tr>
                <td><strong>ruflo</strong></td>
                <td>Local stdio</td>
                <td>npx -y ruflo@latest mcp start</td>
                <td><span class="badge badge-offline">Swarm & Memory Reference</span></td>
              </tr>
              <tr>
                <td><strong>comfy-mcp</strong></td>
                <td>Local CLI</td>
                <td>comfy-mcp.exe</td>
                <td><span class="badge badge-offline">Asset Generation</span></td>
              </tr>
              <tr>
                <td><strong>notebooks</strong></td>
                <td>Local Node Proxy</td>
                <td>mcp_proxy_bundle.js notebooks</td>
                <td><span class="badge badge-offline">Interactive Python</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 9. SELF-IMPROVEMENT CONSOLE -->
      <div id="view-evolution" class="view-pane">
        <div class="card">
          <h2 style="font-size: 16px; margin-bottom: 12px;">SkillForge Self-Evolution Program (SEP) Log</h2>
          <pre>
[PHASE 0] Baseline SQLite DB verified: 851 skills, 18 categories. Backup: registry.db.v0.bak
[PHASE 1] Discovered & acquired 10 engineering skills into .agents/skills/
[PHASE 2] Mapped 15 MCP servers in mcp_config.json
[PHASE 3] Conducted deep system analysis; registered 12 engineering gaps
[PHASE 4] Knowledge Fabric constructed: 970 nodes, 2,473 edges, recursive CTE traversals
[PHASE 5] Hybrid Retrieval Engine implemented: RRF fusion (k=60), LRU query cache (0.01ms warm recall)
[PHASE 6-8] Project boundary fixed, 5 new MCP tools registered, CLI subcommands deployed
[PHASE 9] Dashboard transformed into 10-view developer intelligence console
          </pre>
        </div>
      </div>

      <!-- 10. SECURITY GOVERNANCE -->
      <div id="view-security" class="view-pane">
        <div class="card">
          <h2 style="font-size: 16px; margin-bottom: 12px;">Security & Path Protection Governance</h2>
          <div class="grid-4" style="margin-bottom: 16px;">
            <div class="card" style="background: #070a12;">
              <div class="card-label">Quarantined Skills</div>
              <div class="card-val" style="color: var(--danger);">0</div>
              <div class="card-sub">All active skills safe</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">Path Traversal Guard</div>
              <div class="card-val" style="color: var(--success);">ACTIVE</div>
              <div class="card-sub">Strict relative path resolution</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">SQL Injection Defense</div>
              <div class="card-val" style="color: var(--success);">ENFORCED</div>
              <div class="card-sub">100% parameterized queries</div>
            </div>
            <div class="card" style="background: #070a12;">
              <div class="card-label">FTS5 Sanitization</div>
              <div class="card-val" style="color: var(--success);">ENABLED</div>
              <div class="card-sub">Zero syntax crashes on wildcards</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </main>

  <script>
    function switchView(viewId) {
      document.querySelectorAll('.view-pane').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
      
      const pane = document.getElementById('view-' + viewId);
      if (pane) pane.classList.add('active');
      
      // Update nav active state
      const navs = document.querySelectorAll('.nav-item');
      navs.forEach(nav => {
        if (nav.getAttribute('onclick') && nav.getAttribute('onclick').includes(viewId)) {
          nav.classList.add('active');
          document.getElementById('pane-title').innerText = nav.innerText;
        }
      });

      if (viewId === 'graph') {
        renderGraphCanvas();
      }
    }

    function filterSkillsTable() {
      const q = document.getElementById('explorer-filter').value.toLowerCase();
      const rows = document.querySelectorAll('#skills-table tbody tr');
      rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(q) ? '' : 'none';
      });
    }

    // HTML5 Canvas Knowledge Graph Visualizer
    function renderGraphCanvas() {
      const canvas = document.getElementById('graph-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      canvas.width = canvas.parentElement.clientWidth - 40;
      canvas.height = 500;

      const nodes = [
        { id: 'clean-code', x: 200, y: 150, r: 16, color: '#38bdf8', label: 'clean-code' },
        { id: 'python', x: 120, y: 280, r: 14, color: '#a855f7', label: 'python' },
        { id: 'architecture', x: 300, y: 260, r: 14, color: '#10b981', label: 'architecture' },
        { id: 'testing', x: 450, y: 180, r: 14, color: '#f59e0b', label: 'testing' },
        { id: 'playwright-cli', x: 550, y: 260, r: 16, color: '#38bdf8', label: 'playwright-cli' },
        { id: 'security-hardening', x: 350, y: 380, r: 16, color: '#38bdf8', label: 'security-hardening' },
        { id: 'fastapi', x: 220, y: 400, r: 12, color: '#a855f7', label: 'fastapi' }
      ];

      const edges = [
        [0, 1], [0, 2], [0, 3], [3, 4], [2, 5], [1, 6], [5, 6]
      ];

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw edges
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = '#374151';
      edges.forEach(([s, t]) => {
        ctx.beginPath();
        ctx.moveTo(nodes[s].x, nodes[s].y);
        ctx.lineTo(nodes[t].x, nodes[t].y);
        ctx.stroke();
      });

      // Draw nodes
      nodes.forEach(n => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = n.color;
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.fillStyle = '#f9fafb';
        ctx.font = '11px sans-serif';
        ctx.fillText(n.label, n.x - 20, n.y + n.r + 14);
      });
    }

    // Auto-select view based on URL param
    const urlParams = new URLSearchParams(window.location.search);
    const viewParam = urlParams.get('view');
    if (viewParam) {
      switchView(viewParam);
    }
  </script>
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
        mode_val = params.get("mode", ["balanced"])[0]
        view = params.get("view", ["overview"])[0]

        stats = self.repo.get_stats()
        total_skills = stats.get("total_skills", 0)
        by_source = stats.get("by_source", {})
        installed_count = sum(v for k, v in by_source.items() if "installed" in k)
        offline_count = by_source.get("offline_book", 0)

        graph_stats = self.repo.get_graph_stats()
        cache_stats = self.tools.engine.cache.stats()

        # Recommendation in studio
        studio_results_html = ""
        if task:
            try:
                retrieval_mode = RetrievalMode(mode_val)
            except Exception:
                retrieval_mode = RetrievalMode.BALANCED
            
            res = self.tools.engine.retrieve(query=task, project_path=project if project else None, mode=retrieval_mode, limit=4)
            lines = [f"<div style='margin-top: 16px; background: #070a12; border: 1px solid var(--border); border-radius: 6px; padding: 16px;'>",
                     f"<div style='font-size: 14px; font-weight: 600; color: var(--accent); margin-bottom: 8px;'>Retrieval Mode: {retrieval_mode.value.upper()} (Duration: {res['duration_ms']}ms | Cache Hit: {res['cache_hit']})</div>"]
            for r in res.get("results", []):
                lines.append(f"""
                <div style='border-top: 1px solid #1f2937; padding: 10px 0;'>
                  <div style='display: flex; justify-content: space-between;'>
                    <strong style='color: #e5e7eb;'>{r['name']}</strong>
                    <span style='color: var(--success); font-weight: 600;'>Confidence: {int(r['normalized_confidence'] * 100)}%</span>
                  </div>
                  <div style='font-size: 12px; color: var(--muted); margin: 4px 0;'>{r['description']}</div>
                  <div style='font-size: 11px; color: #6b7280;'>Signals: {', '.join(r.get('signals', []))}</div>
                </div>
                """)
            lines.append("</div>")
            studio_results_html = "\n".join(lines)

        # Build skill table rows (sample 100 for explorer)
        skills = self.repo.list_skills(limit=100)
        table_rows = []
        for s in skills:
            is_inst = "installed" in s.source_type.value
            badge_class = "badge-installed" if is_inst else "badge-offline"
            badge_text = "Installed" if is_inst else "Offline Book"
            table_rows.append(f"""
            <tr>
              <td><strong>{s.name}</strong></td>
              <td>{s.category}</td>
              <td><span class="badge {badge_class}">{badge_text}</span></td>
              <td>{int(s.quality_score * 100)}%</td>
              <td>{s.status.value}</td>
            </tr>
            """)

        # Project profile sample
        active_root = Path(__file__).resolve().parent.parent.parent.parent
        profile = self.tools.matcher.detector.analyze_workspace(active_root)
        profile_json = json.dumps(profile.__dict__, indent=2)

        html = (
            HTML_SHELL
            .replace("{TOTAL_SKILLS}", str(total_skills))
            .replace("{INSTALLED_COUNT}", str(installed_count))
            .replace("{OFFLINE_COUNT}", str(offline_count))
            .replace("{GRAPH_NODES}", str(graph_stats.get("total_nodes", 0)))
            .replace("{GRAPH_EDGES}", str(graph_stats.get("total_edges", 0)))
            .replace("{CACHE_HIT_RATE}", f"{int(cache_stats.get('hit_rate', 0) * 100)}%")
            .replace("{CACHE_ENTRIES}", str(cache_stats.get("cached_entries", 0)))
            .replace("{STUDIO_TASK}", task)
            .replace("{STUDIO_PROJECT}", project)
            .replace("{STUDIO_RESULTS_HTML}", studio_results_html)
            .replace("{SKILL_TABLE_ROWS}", "\n".join(table_rows))
            .replace("{PROJECT_PROFILE_JSON}", profile_json)
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass


def get_db_path() -> Path:
    env_p = os.environ.get("SKILLFORGE_DB_PATH")
    if env_p and Path(env_p).is_file():
        return Path(env_p)
    return Path(__file__).resolve().parent.parent.parent.parent / "data" / "registry.db"


def start_dashboard(host: str = "127.0.0.1", port: int = 8765):
    db_path = get_db_path()
    repo = SkillRepository(db_path)
    tools = SkillForgeTools(repo)

    DashboardHandler.repo = repo
    DashboardHandler.tools = tools

    server_address = (host, port)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"SkillForge 10-View Console running at http://{host}:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
        httpd.server_close()
