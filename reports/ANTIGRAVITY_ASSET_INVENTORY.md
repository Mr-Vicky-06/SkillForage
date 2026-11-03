# Antigravity Comprehensive Asset Inventory

**Audit Date:** 3 November 2026  
**Environment:** Windows 11 x64, Antigravity IDE v2.6.0, AGY CLI v1.4.12  
**Registry Database:** `d:\setup\antigravity-skillforge\data\registry.db`  
**Format:** Pure Markdown (.md)  

---

### 1. Master Inventory Summary

| Inventory Dimension | Count | Primary Storage / Source | Status / Integrity |
|---|---|---|---|
| **Total Distinct Skills** | **851** | `data/registry.db` (`skills` table) | VERIFIED (Zero inflation) |
| **Total Ecosystem Assets** | **53** | `data/registry.db` (`ecosystem_assets`) | VERIFIED |
| **Bundled Components** | **139** | `data/registry.db` (`ecosystem_components`)| VERIFIED |
| **Registered MCP Servers** | **15** | `%USERPROFILE%\.gemini\config\mcp_config.json` | VERIFIED |
| **Mapped MCP Capabilities**| **15** | `data/registry.db` (`mcp_capabilities`) | VERIFIED (Secrets Redacted) |
| **Installed Plugins** | **8** | `%USERPROFILE%\.gemini\config\plugins\` | VERIFIED (7 active in CLI) |
| **Custom Agents** | **10** | Global `config/agents/` (6) + Plugin (4) | VERIFIED |
| **Workspace Instructions**| **2** | Global `AGENTS.md` + Workspace `AGENTS.md` | VERIFIED |
| **Discovery Manifests** | **4** | `.agents/` (`skills`, `rules`, `agents`, `plugins`) | VERIFIED |
| **Supplemental Packs** | **11** | `D:\setup\skillforge-ecosystem-sources/` | VERIFIED |

---

### 2. Installed Plugins Census (8 Plugins)

| Plugin Name | Version | Source | Bundled Skills | Bundled Agents | CLI Enabled | Exact Path |
|---|---|---|---|---|---|---|
| `agent-skills` | 0.6.15 | antigravity | 25 skills | 4 agents | Yes | `%USERPROFILE%\.gemini\config\plugins\agent-skills` |
| `android-cli-plugin` | 1.0.16625370 | antigravity-plugins-official | 3 skills | 0 agents | Yes | `%USERPROFILE%\.gemini\config\plugins\android-cli-plugin` |
| `chrome-devtools-plugin` | 0.21.0 | antigravity | 0 skills | 0 agents | Yes | `%USERPROFILE%\.gemini\config\plugins\chrome-devtools-plugin` |
| `firebase` | 1.0.0 | antigravity | 0 skills | 0 agents | Yes | `%USERPROFILE%\.gemini\config\plugins\firebase` |
| `googlecloudtools.datacloud_telemetry` | 1.0.0 | internal | 0 skills | 0 agents | Yes | `%USERPROFILE%\.gemini\config\plugins\googlecloudtools.datacloud_telemetry` |
| `modern-web-guidance-plugin` | 1.0.4 | antigravity | 0 skills | 0 agents | Yes | `%USERPROFILE%\.gemini\config\plugins\modern-web-guidance-plugin` |
| `science` | 1.1.0 | antigravity-plugins-official | 38 skills | 0 agents | Yes | `%USERPROFILE%\.gemini\config\plugins\science` |
| `google-antigravity-sdk` | 1.0.0 | local-disk | 1 skill | 0 agents | Standby | `%USERPROFILE%\.gemini\config\plugins\google-antigravity-sdk` |

---

### 3. Custom Subagents Census (10 Agents)

| Agent Name | Scope | Role / Focus | Allowed Tools | Model Tier | Policy |
|---|---|---|---|---|---|
| `data-ml-engineer` | Global | Data pipelines, ML harnesses, SQL models | read_file, run_command | inherit | ask |
| `frontend-engineer` | Global | Responsive web, accessibility, Tailwind | read_file, write_file, edit_file | inherit | ask |
| `python-engineer` | Global | Python services, async workflows, CLI | read_file, write_file, edit_file | inherit | ask |
| `qa-engineer` | Global | Test suites, regression verification | read_file, run_command | inherit | ask |
| `security-reviewer`| Global | Security flaws, injection risks, auth | read_file | pro | ask |
| `software-architect`| Global| Module mapping, data flow, architecture | read_file | pro | ask |
| `code-reviewer` | Plugin | Multi-axis code review before merge | read_file, run_command | inherit | ask |
| `security-auditor` | Plugin | Threat modeling, vulnerability scanning| read_file | pro | ask |
| `test-engineer` | Plugin | Test writing, coverage analysis | read_file, write_file, edit_file | inherit | ask |
| `web-performance-auditor` | Plugin | Core Web Vitals, performance profiling | read_file | inherit | ask |

---

### 4. Registered MCP Servers (15 Servers)

| Server Identifier | Transport | Command / Target | Auth Mode | Risk Class |
|---|---|---|---|---|
| `skillforge` | stdio | `python -m skillforge.mcp_server.server` | Local Stdio | read_only / verified |
| `playwright` | stdio | `npx -y @playwright/mcp` | Local Stdio | browser_automation |
| `comfy-mcp` | stdio | `python -m comfy_mcp` | Local Stdio | state_mutating |
| `ruflo` | stdio | `node build/index.js` | Local Stdio | agentic_orchestration |
| `notebooks` | stdio | `python -m notebooks_mcp` | Local Stdio | read_only |
| `visualization` | stdio | `python -m vis_mcp` | Local Stdio | read_only |
| `data-agent-kit` | stdio | `python -m data_agent_kit` | ADC / GCP | state_mutating |
| `datacloud_bigquery_remote` | streamable_http | Remote Cloud Endpoint | Google OAuth | read_only |
| `datacloud_spanner_remote` | streamable_http | Remote Cloud Endpoint | Google OAuth | read_only |
| `datacloud_alloydb_remote` | streamable_http | Remote Cloud Endpoint | Google OAuth | read_only |
| `datacloud_cloud-sql_remote`| streamable_http | Remote Cloud Endpoint | Google OAuth | read_only |
| `datacloud_knowledge_catalog_remote`| streamable_http| Remote Cloud Endpoint | Google OAuth | read_only |
| `datacloud_dataproc_remote`| streamable_http | Remote Cloud Endpoint | Google OAuth | read_only |
| `gitlab-orbit` | stdio | `node gitlab-orbit.js` | PAT Token | state_mutating |
| `bigquery` | stdio | `python -m bigquery_mcp` | ADC / GCP | read_only |

---

### 5. Workspace Instructions & Discovery Manifests

| Asset Name | Scope | Type | Path | Status |
|---|---|---|---|---|
| `AGENTS.md` (Global) | Global | `workspace_instruction` | `%USERPROFILE%\.gemini\AGENTS.md` | VERIFIED |
| `AGENTS.md` (Workspace) | Workspace | `workspace_instruction` | `d:\setup\antigravity-skillforge\AGENTS.md` | VERIFIED |
| `skills.json` | Workspace | `discovery_manifest` | `d:\setup\skillforge-ecosystem-sources\manifests\skills.json` | VERIFIED |
| `rules.json` | Workspace | `discovery_manifest` | `d:\setup\skillforge-ecosystem-sources\manifests\rules.json` | VERIFIED |
| `agents.json` | Workspace | `discovery_manifest` | `d:\setup\skillforge-ecosystem-sources\manifests\agents.json` | VERIFIED |
| `plugins.json` | Workspace | `discovery_manifest` | `d:\setup\skillforge-ecosystem-sources\manifests\plugins.json` | VERIFIED |

---
*Inventory verified against live database and filesystem.*
