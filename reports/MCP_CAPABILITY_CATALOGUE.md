# Antigravity MCP Capability Catalogue & Security Audit

**Audit Date:** 3 November 2026  
**Audited Runtime:** Antigravity IDE v2.6.0  
**Source Configuration:** `%USERPROFILE%\.gemini\config\mcp_config.json`  
**Format:** Pure Markdown (.md)  

---

### 1. Executive Summary

Model Context Protocol (MCP) serves as Antigravity’s **executable capability integration layer**, exposing structured tools, resources, and prompts to the agent. MCP servers are **not knowledge skills**; they are executable RPC integrations.

SkillForge catalogs MCP servers in `ecosystem_assets` and their exposed functions in `mcp_capabilities`, enforcing strict risk classification, redacting sensitive environment variables, and mandating explicit user approvals for state-mutating actions.

---

### 2. Host MCP Server Census (15 Configured Servers)

| Server ID | Transport | Execution Target / Command | Auth Mechanism | Risk Class | Permission Policy |
|---|---|---|---|---|:---:|
| `skillforge` | `stdio` | `python -m skillforge.mcp_server.server` | Local Stdio | `read_only` | Auto-allowed |
| `playwright` | `stdio` | `npx -y @playwright/mcp` | Local Stdio | `state_mutating` | Ask |
| `comfy-mcp` | `stdio` | `python -m comfy_mcp` | Local Stdio | `state_mutating` | Ask |
| `ruflo` | `stdio` | `node build/index.js` | Local Stdio | `agentic_coordinator` | Ask |
| `notebooks` | `stdio` | `python -m notebooks_mcp` | Local Stdio | `read_only` | Ask |
| `visualization`| `stdio` | `python -m vis_mcp` | Local Stdio | `read_only` | Ask |
| `data-agent-kit`| `stdio`| `python -m data_agent_kit` | Google ADC | `state_mutating` | Ask |
| `datacloud_bigquery_remote` | `streamable_http` | `https://datacloud.googleapis.com/mcp/bigquery` | OAuth 2.0 | `read_only` | Ask |
| `datacloud_spanner_remote` | `streamable_http` | `https://datacloud.googleapis.com/mcp/spanner` | OAuth 2.0 | `read_only` | Ask |
| `datacloud_alloydb_remote` | `streamable_http` | `https://datacloud.googleapis.com/mcp/alloydb` | OAuth 2.0 | `read_only` | Ask |
| `datacloud_cloud-sql_remote` | `streamable_http` | `https://datacloud.googleapis.com/mcp/cloudsql`| OAuth 2.0 | `state_mutating` | Ask |
| `datacloud_knowledge_catalog_remote` | `streamable_http` | `https://datacloud.googleapis.com/mcp/catalog`| OAuth 2.0 | `read_only` | Ask |
| `datacloud_dataproc_remote` | `streamable_http` | `https://datacloud.googleapis.com/mcp/dataproc`| OAuth 2.0 | `state_mutating` | Ask |
| `gitlab-orbit` | `stdio` | `node dist/index.js` | PAT Token | `state_mutating` | Ask |
| `bigquery` | `stdio` | `python -m bigquery_mcp` | Google ADC | `read_only` | Ask |

---

### 3. Capability Taxonomy & Risk Classes

```text
+-----------------------------------------------------------------------+
|                       MCP CAPABILITY TAXONOMY                         |
+--------------------------+-----------------------+--------------------+
| READ_ONLY                | STATE_MUTATING        | DESTRUCTIVE        |
| - Schema discovery       | - Browser click/fill  | - Database drop    |
| - SQL SELECT queries     | - Git branch checkout | - Cloud deletion   |
| - File AST parsing       | - Test execution      | - Secret write     |
| Default: Low Risk        | Default: Ask Mode     | Default: Prompt    |
+--------------------------+-----------------------+--------------------+
```

#### Detailed Capability Breakdown:
1. **`skillforge` (18 Tools)**:
   - `search_skills`, `load_skill`, `recommend_skills`, `analyze_project`, `explain_recommendation`
   - `graph_query`, `graph_neighbors`, `skillforge_health`, `list_ecosystem_assets`
   - `get_asset_details`, `recommend_project_setup`, `validate_ecosystem_asset`
   - **Risk:** `read_only`. Fast in-memory SQLite CTE queries and vector fusion.
2. **`playwright` (24 Tools)**:
   - `browser_navigate`, `browser_click`, `browser_type`, `browser_snapshot`, `browser_take_screenshot`
   - **Risk:** `state_mutating`. Interacts with live browser sessions. Requires Ask permission.
3. **Datacloud Remote Servers (6 Endpoints)**:
   - Streamable HTTP protocol backed by Google Cloud OAuth credentials.
   - Enforces read-only database query execution with zero token leakage into repository files.

---

### 4. Zero Credential Exposure Guarantee

SkillForge’s `MCPConfigParser` enforces strict security hygiene:
- Only environment variable **names** (e.g. `GITLAB_TOKEN`, `BIGQUERY_PROJECT`) are indexed for dependency checking.
- Actual credentials, bearer tokens, and passwords are **never written to `data/registry.db`** or emitted in CLI reports.
- All MCP tool calls default to `Ask` mode, ensuring no autonomous destructive actions occur without user approval.

---
*Catalog generated and audited by SkillForge Ecosystem Engine.*

