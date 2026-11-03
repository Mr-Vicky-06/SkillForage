# Antigravity Extensibility Ecosystem Research & Architecture Guide

**Snapshot Date:** 3 November 2026  
**Target Environment:** Standalone Google Antigravity IDE (v2.6.0) / AGY CLI (v1.4.12) on Windows 11 x64  
**Format:** Pure Markdown (.md)  

---

### 1. Executive Summary

Antigravity’s extensibility ecosystem is substantially broader than standard Agent Skills. While an **Agent Skill** represents on-demand procedural knowledge loaded via progressive disclosure, Antigravity officially defines **10 distinct extensibility primitives**.

Flattening these primitives into a generic "skill" table corrupts catalog provenance, leaks unnecessary context, and confuses execution boundaries. SkillForge models them as typed first-class entities within the **Antigravity Ecosystem Registry**.

```text
+-------------------------------------------------------------------------------+
|                    THE 10 ANTIGRAVITY EXTENSIBILITY PRIMITIVES                |
+--------------------------+------------------------------+---------------------+
| 1. Agent Skills          | 2. Rules (AGENTS.md / glob)  | 3. Custom Agents    |
| 4. Plugin Bundles        | 5. Lifecycle Hooks           | 6. MCP Servers      |
| 7. Discovery Manifests   | 8. App Sidecars (Daemons)    | 9. Legacy Workflows |
| 10. Official Bundles     |                              |                     |
+--------------------------+------------------------------+---------------------+
```

---

### 2. Comprehensive Primitive Taxonomy

| # | Primitive Type | Canonical File / Format | Primary Role | Context Lifecycle | Surface Support |
|---|---|---|---|---|---|
| **1** | `agent_skill` | `SKILL.md` (+ scripts, refs) | Reusable domain procedure | Progressive disclosure (loaded just-in-time) | IDE, App, CLI, SDK |
| **2** | `agent_rule` | `.agents/rules/*.md` | Hard constraint / invariant | Trigger-based (`always_on`, `model_decision`, `glob`) | IDE, App, CLI |
| **3** | `workspace_instruction`| `AGENTS.md`, `GEMINI.md` | Workspace baseline conventions | Always-on (injected into every turn) | IDE, App, CLI |
| **4** | `custom_agent` | `.agents/agents/*.md` | Delegated execution profile | Isolated subagent context with dedicated tools | IDE, App |
| **5** | `plugin_bundle` | `plugin.json` | Distributable multi-asset container | Package manager lifecycle (`agy plugin`) | IDE, App, CLI |
| **6** | `lifecycle_hook` | `hooks.json` | Event-driven shell automation | Fires on `SessionStart`, `PreToolUse`, `Stop`, etc. | IDE, App, CLI |
| **7** | `mcp_server` | `mcp_config.json` | Capability & tool integration | Dynamic tool schema registration via stdio/HTTP | IDE, App, CLI |
| **8** | `discovery_manifest` | `skills.json`, `rules.json` | Deep scan path directory pointer | Resolves folders outside 1-level scan depth | IDE, App |
| **9** | `sidecar` | `sidecar.json` | Managed background service | Persistent daemon process (App surface only) | App Only |
| **10**| `legacy_workflow` | `.agents/workflows/*.yaml` | Deprecated single-file automation | Retired on 19 October 2026. Needs migration. | Archived |

---

### 3. Deep Dive into Key Primitives

#### 3.1 Rules vs. Skills (Context Economics)
* **Rules (`AGENTS.md`, `.agents/rules/*.md`)**: Rules enforce non-negotiable boundaries (e.g. "never modify production databases without confirmation", "no secrets in commits"). 
  - `always_on`: Loaded on every model turn. Must be kept compact (< 2 KB).
  - `glob`: Loaded only when active files match patterns (e.g. `tests/**/*.py`).
  - `model_decision`: Loaded dynamically when the agent determines rule relevance.
* **Skills (`SKILL.md`)**: Reusable procedural knowledge. Only the title and short description are visible at start; the full instructions are fetched on-demand via progressive disclosure.

#### 3.2 Plugins as Multi-Asset Containers
A plugin is a versioned package, **not a single skill**. A single plugin like `agent-skills` (v0.6.15) bundles:
- 25 distinct Agent Skills (`code-review-and-quality`, `test-driven-development`, etc.)
- 4 custom subagents (`code-reviewer`, `security-auditor`, `test-engineer`, `web-performance-auditor`)
- 0 MCP servers and 0 hooks.
In SkillForge, `agent-skills` is indexed as 1 `plugin_bundle`, linking to 25 skills and 4 agents via `ecosystem_components`. It does **not** inflate the total skills counter.

#### 3.3 Lifecycle Hooks & Fail-Open Safety Warning
Antigravity supports 6 hook lifecycle events:
- `SessionStart`: Runs once when session initializes.
- `PreToolUse` / `PostToolUse`: Fires before/after tool execution (e.g. running linters).
- `PreInvocation` / `PostInvocation`: Fires before/after LLM turns.
- `Stop`: Runs right before agent hands control back to user.
> [!WARNING]
> Official Antigravity documentation explicitly states that **non-zero hook exits are logged as errors and execution proceeds (failing open)**. Hooks must never serve as the sole security boundary.

#### 3.4 The 19 October 2026 Legacy Workflow Cutoff
The legacy single-file `.agents/workflows/*.yaml` format was officially retired on **19 October 2026**. SkillForge indexes legacy workflows as `legacy_workflow` with status `RETIRED`, and routes them to the `/migrate-workflows` conversion pipeline.

---

### 4. Canonical Filesystem Directory Matrix

```text
D:\setup\
├── .agents\                        # Machine-wide workspace scope
│   ├── skills\<name>\SKILL.md
│   ├── rules\<name>.md
│   └── agents\<name>.md
├── antigravity-skillforge\          # Project-specific workspace scope
│   ├── .agents\
│   │   ├── skills\
│   │   ├── rules\
│   │   ├── agents\
│   │   ├── plugins\
│   │   ├── mcp_config.json
│   │   └── hooks.json
│   └── AGENTS.md
└── %USERPROFILE%\.gemini\          # Global user scope
    ├── AGENTS.md
    └── config\
        ├── skills\
        ├── rules\
        ├── agents\
        ├── plugins\
        └── mcp_config.json
```

---
*Report generated and validated by SkillForge Ecosystem Engine.*
