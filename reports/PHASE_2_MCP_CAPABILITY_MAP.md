# SkillForge Evolution Program (SEP)
## Phase 2: MCP Capability Map & Environment Harness

**Report Date:** 2026-11-03  
**Status:** Completed & Verified  
**Configuration Source:** `%USERPROFILE%\.gemini\config\mcp_config.json`  

---

### 1. Executive Summary

As part of Phase Two of the SkillForge Evolution Program (SEP), we inspected the complete Model Context Protocol (MCP) environment configuration. A total of 15 MCP servers are registered across local and remote providers. This capability map defines the operational topology, tool surface, invocation patterns, and roles each server plays across the engineering, retrieval, verification, and visual quality phases of SkillForge's self-evolution.

---

### 2. Registered MCP Servers Inventory

| Server Name | Transport / Type | Execution Target / URL | Primary Purpose | Role in SEP |
| :--- | :--- | :--- | :--- | :--- |
| **`skillforge`** | Local `stdio` (Python FastMCP) | `D:\setup\antigravity-skillforge\.venv\Scripts\python.exe -m skillforge.mcp_server.server` | Skill retrieval, analysis, recommendation, resource loading, feedback | **Core Under Test & Evolution** |
| **`playwright`** | Local `stdio` (Node npx) | `npx -y @playwright/mcp@latest` | Headless/Headed browser automation, DOM snapshotting, visual regression, screenshots | **UI & Verification Harness** |
| **`ruflo`** | Local `stdio` (Node npx) | `npx -y ruflo@latest mcp start` | Swarm orchestration, memory retrieval, code diff analysis, task execution | **Agentic Pattern Reference** |
| **`comfy-mcp`** | Local `stdio` (Python CLI) | `comfy-mcp.exe` -> `comfy.exe` | Image generation, diffusion pipeline control | Creative/Asset generation |
| **`notebooks`** | Local Node Proxy | `googlecloudtools.datacloud-1.0.0-universal/mcp_servers/cli/mcp_proxy_bundle.js` | Interactive Jupyter/Python notebook execution | Data science workflows |
| **`visualization`** | Local Node Proxy | `googlecloudtools.datacloud-1.0.0-universal/mcp_servers/cli/mcp_proxy_bundle.js` | Data charting and visual analytics | Data exploration |
| **`data-agent-kit`** | Local Node Proxy | `googlecloudtools.datacloud-1.0.0-universal/mcp_servers/cli/mcp_proxy_bundle.js` | BigQuery/Datacloud Agent capabilities | Enterprise data agents |
| **`datacloud_bigquery_remote`** | Remote SSE / OAuth | `https://bigquery.googleapis.com/mcp` | Cloud data warehousing queries & schemas | Enterprise data access |
| **`datacloud_spanner_remote`** | Remote SSE / OAuth | `https://spanner.googleapis.com/mcp` | Globally distributed relational DB | Enterprise DB |
| **`datacloud_alloydb_remote`** | Remote SSE / OAuth | `https://alloydb.googleapis.com/mcp` | PostgreSQL-compatible transactional/HTAP | Enterprise DB |
| **`datacloud_cloud-sql_remote`** | Remote SSE / OAuth | `https://sqladmin.googleapis.com/mcp` | Managed MySQL/Postgres/SQL Server | Enterprise DB |
| **`datacloud_knowledge_catalog_remote`** | Remote SSE / OAuth | `https://dataplex.googleapis.com/mcp` | Data governance, policy, lineage | Catalog & governance |
| **`datacloud_dataproc_remote`** | Remote SSE / OAuth | `https://dataproc-${REGION}.googleapis.com/mcp` | Managed Apache Spark / Hadoop | Big Data processing |
| **`gitlab-orbit`** | Remote SSE / npx | `npx -y mcp-remote https://gitlab.com/api/v4/orbit/mcp` | GitLab issues, merge requests, CI pipelines | Source repository ops |
| **`bigquery`** | Remote SSE / OAuth | `https://bigquery.googleapis.com/mcp` | Direct BigQuery SQL & dataset discovery | Enterprise data |

---

### 3. Deep-Dive: Core MCP Tool Mapping for SkillForge Evolution

#### 3.1 `skillforge` (V0 Baseline Tool Surface)
- **`skillforge_status`**: Provides database connectivity, skill counts (851 skills across 18 categories), and database file size.
- **`search_skills`**: Lexical FTS5 search with query expansion, category filters, and limit/offset pagination.
- **`analyze_project`**: Inspects a directory to identify languages, frameworks, dependencies, and project types.
- **`recommend_skills`**: Scores and ranks skills against project context and specific user tasks.
- **`load_skill`**: Retrieves full skill metadata and parsed markdown content from disk or database.
- **`read_skill_resource`**: Reads supplementary scripts, references, or assets bundled with a skill.
- **`list_skills`**: Enumerates skills filtered by category, tags, or trust status.
- **`validate_skill`**: Validates `SKILL.md` frontmatter, schema conformance, and security safety flags.
- **`record_skill_feedback`**: Logs user interaction signals (useful/not useful) for retrieval learning.

*Planned V1 Enhancements to `skillforge`:*
- `explain_recommendation`: Returns full score breakdown (BM25 score, graph distance, tag boost, decay factor).
- `graph_query`: Cypher-like / relational multi-hop entity traversal.
- `graph_neighbors`: Inspects prerequisite, complements, and conflict edges for any given skill.
- `list_project_profiles`: Returns persistent architectural fingerprints of analyzed projects.
- `skillforge_health`: Comprehensive database integrity, FTS index health, and cache statistics.

#### 3.2 `playwright` (Verification & Visual Inspection)
- **`browser_navigate`**: Direct browser navigation to local dashboard `http://127.0.0.1:8765`.
- **`browser_snapshot`**: Accessibility tree and DOM structure capture for testing interactive elements.
- **`browser_take_screenshot`**: High-resolution PNG visual captures proving dashboard state, navigation, and chart rendering.
- **`browser_click` / `browser_fill_form` / `browser_press_key`**: User simulation for testing search inputs, tab switches, and filter clicks.
- **`browser_console_messages` / `browser_network_requests`**: Diagnostics for frontend JavaScript exceptions or failed API calls.

*Role in SEP:* Validates Phase 9 Dashboard overhaul across all 10 views without manual browser clicking.

#### 3.3 `ruflo` (Agent & Memory Patterns Reference)
- Tools: `memory_store`, `memory_retrieve`, `agentdb_graph-query`, `coordination_topology`.
- *Role in SEP:* Architectural reference for local Graph and Memory patterns (implemented natively in SkillForge via SQLite and zero external dependencies).

---

### 4. Lifecycle & Integration Protocols

1. **Local-First Stdio Guarantee:** The SkillForge MCP server runs strictly within `D:\setup\antigravity-skillforge\.venv` over standard I/O (`stdio`).
2. **Isolation & Concurrency Safety:** FastMCP tool executions dispatched across worker threads maintain `check_same_thread=False` on the SQLite engine with WAL mode active.
3. **Zero-Telemetry Policy:** All metadata queries, graph queries, and recommendations resolve against local SQLite tables without external network roundtrips.

---
*Verified by SEP Engine Phase 2.*

