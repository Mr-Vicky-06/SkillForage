# SkillForge Local Intelligence Fabric (SLIF)
# Google Antigravity Integration & Host Surface Validation Report

**Document Date:** November 3, 2026  
**Antigravity Environment:** Antigravity IDE / App v2.6.0, `agy` CLI v1.4.12  
**Host Operating System:** Windows 11 Enterprise x64  
**Integration Protocol:** Model Context Protocol (MCP) via Official Python SDK (`mcp.server.mcpserver.MCPServer`)  
**Verification Target:** SLIF P0 Security Hardening Sprint  

---

## 1. Executive Overview & Host Boundary Analysis

A critical principle of rigorous systems engineering is **never to claim security guarantees that cannot be proven or enforced at the architectural boundary**. 

Google Antigravity 2.6.0 integrates with external knowledge and tools through two distinct mechanisms:
1. **Host-Native File Scanning:** The Antigravity IDE natively scans designated file paths on startup and injects skill summaries directly into the agent's system prompt context.
2. **Model Context Protocol (MCP) Tools:** Antigravity queries external tool servers over `stdio` using the standard JSON-RPC 2.0 protocol.

Understanding this division is essential for understanding where SkillForge's security boundaries begin and end.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Google Antigravity 2.6.0 Host                        │
│                                                                        │
│  ┌──────────────────────────────┐    ┌──────────────────────────────┐  │
│  │ Native Builtin Skills (9)    │    │ Global User Skills (44)      │  │
│  │ (Built into Antigravity App) │    │ (%USERPROFILE%\.gemini\...)  │  │
│  └──────────────┬───────────────┘    └──────────────┬───────────────┘  │
│                 │                                   │                  │
│                 ▼                                   ▼                  │
│       [ IDE System Prompt Assembler (Always Injected In Full) ]        │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │ JSON-RPC (stdio)
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│             SkillForge Local Intelligence Fabric (SLIF)                │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ SLIF FastMCP Server (stdio)                                      │  │
│  │ Endpoints: recommend_skills, load_skill, approve_skills, etc.     │  │
│  └──────────────────┬───────────────────────────────────────────────┘  │
│                     │                                                  │
│                     ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Human Approval Gate (ApprovalTokenManager)                       │  │
│  │ - PENDING -> APPROVED -> CONSUMED state machine                  │  │
│  │ - 128-bit cryptographic tokens (SF-XXXXXXXXXXXXXXXX)             │  │
│  │ - Replay prevention & conversation binding                       │  │
│  └──────────────────┬───────────────────────────────────────────────┘  │
│                     │                                                  │
│                     ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ SLIF Specialist Vault (749 Skills)                               │  │
│  │ - 724 Offline Engineering Book Skills (Extracted & Cleaned)      │  │
│  │ - 25 Empirical Research Intelligence Skills                      │  │
│  │ - Sandboxed Local Executor (Allowlisted Environment)             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Real Installed Surface Audit

An empirical inspection of the host workstation revealed the exact layout of skills and configurations:

### 2.1. Host-Native Directories (Bypass Warning)
- **Builtin Skills (9 skills):** Located at `C:\Users\ASUS\.gemini\antigravity\builtin\skills\`  
  *(e.g., `antigravity-guide`, `generative_ui`, `automation`, `plugin`, `agy-customizations`).*
- **Global Config Skills (44 skills):** Located at `C:\Users\ASUS\.gemini\config\skills\` and plugin directories  
  *(e.g., `karpathy-guidelines`, `agent-memory-systems`, `gcp-data-pipelines`, `bigquery-sql`, science plugins).*
- **Local Project Skills (6 skills):** Located at `D:\setup\.agents\skills\`  
  *(e.g., `ui-ux-pro-max`, `banner-design`, `brand`, `design-system`, `slides`, `playwright-cli`).*

> [!IMPORTANT]
> **Host Native Limitation:** Any skill file residing physically inside `%USERPROFILE%\.gemini\config\skills\` or `d:\setup\.agents\skills\` is read directly by Antigravity's internal prompt builder at conversation initialization. This process occurs entirely inside Antigravity's host process before any MCP tool is invoked.
> 
> Therefore, **SkillForge does NOT claim to gate or restrict native skills already installed in Antigravity's native directories**. Those skills are part of the user's permanent base prompt.

### 2.2. SkillForge Specialist Vault (Strictly Gated)
- **Specialist Vault Skills (749 skills):**
  - **724 Offline Engineering Skills:** Extracted from foundational engineering literature (`vault/skills/offline_book/`).
  - **25 Research Intelligence Skills:** Authored with functional scripts and manifests (`vault/skills/research/`).
- **Storage Location:** Located exclusively within `d:\setup\antigravity-skillforge\vault\`.
- **Access Path:** These 749 skills are **not** placed in Antigravity's native directory. They can **only** be accessed by Antigravity via the SkillForge FastMCP server.
- **Enforcement:** Every request to retrieve instructions (`load_skill`, `skillforge_load_approved_skills`) or run helper scripts (`skillforge_execute_script`) passes directly through the `ApprovalTokenManager`.

---

## 3. MCP Tool Configuration & Client Registration

The SkillForge MCP server is registered in Antigravity's global configuration (`%USERPROFILE%\.gemini\antigravity\mcp_config.json`):

```json
{
  "mcpServers": {
    "skillforge": {
      "command": "D:/setup/antigravity-skillforge/.venv/Scripts/python.exe",
      "args": [
        "-m",
        "skillforge.mcp_server.server"
      ],
      "env": {
        "SKILLFORGE_DB_PATH": "D:/setup/antigravity-skillforge/data/registry.db",
        "SKILLFORGE_STRICT_OFFLINE": "false"
      }
    }
  }
}
```

### Registered Tools (24 Tools Total):
1. **Catalog & Discovery:** `skillforge_status`, `search_skills`, `list_skills`, `validate_skill`, `explain_recommendation`.
2. **Project Profiling:** `analyze_project`, `list_project_profiles`, `recommend_project_setup`.
3. **Knowledge Graph:** `graph_query`, `graph_neighbors`, `skillforge_health`.
4. **Antigravity Ecosystem:** `list_ecosystem_assets`, `get_asset_details`, `validate_ecosystem_asset`.
5. **SLIF Gated Workflow:** `skillforge_recommend_skills`, `skillforge_approve_skills`, `skillforge_load_approved_skills`, `skillforge_decline_skills`, `load_skill`, `read_skill_resource`.
6. **Execution & Verification:** `skillforge_execute_script`, `skillforge_cross_source_verify`, `record_skill_feedback`.

---

## 4. Host Provenance Limitations & Transparent Guarantees

In accordance with our professional engineering baseline, we transparently document the exact security guarantees and limitations of the integration:

### 4.1. What SLIF Guarantees:
1. **Zero Unapproved Vault Injections:** None of the 749 specialist vault skills can be loaded into context or executed without an approved token.
2. **Replay Prevention:** A token can only be consumed once. Attempting to reload a skill with a previously consumed token fails.
3. **Execution Isolation:** Subprocesses executing local skill scripts run with a scrubbed `SAFE_ENV_ALLOWLIST`, cannot access the network in offline mode, are bounded by a 30s timeout, and cannot escape their skill directory.
4. **Independent Research Checks:** Cross-source verification independently parses and corroborates factual evidence rather than trusting caller-provided flags.

### 4.2. What SLIF Cannot Prevent (Host-Level Limitations):
1. **Native Directory Inclusion:** Antigravity will automatically load any file placed into `%USERPROFILE%\.gemini\config\skills\` on startup. SLIF cannot intercept native IDE file scanning.
2. **LLM Prompt Provenance:** Because the Antigravity host communicates with MCP tools over JSON-RPC, the MCP server receives tool arguments from the LLM. If the LLM generates an approval tool call without human input, the MCP server cannot verify the human physical keystrokes unless the host IDE provides signed turn provenance. 
3. **Direct File System Access:** If a human user or external script accesses `vault/skills/` directly via the OS file explorer, SLIF runtime policies do not apply outside the Python runtime.

---

## 5. Conclusion & Operational Recommendation

The integration between Google Antigravity and SkillForge Local Intelligence Fabric successfully creates an authorized, context-aware bridge. Antigravity users retain complete control over specialist skill activation, while the host IDE remains responsive and unencumbered by massive static prompts.
