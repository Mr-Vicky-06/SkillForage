# Antigravity Surface Compatibility & Precedence Matrix

**Document Date:** 3 November 2026  
**Audited Runtime:** Standalone Google Antigravity IDE (v2.6.0) / AGY CLI (v1.4.12) on Windows 11 x64  
**Format:** Pure Markdown (.md)  

---

### 1. Cross-Surface Support Matrix

Antigravity operates across 4 distinct execution surfaces. Customization capabilities vary by surface:

| Customization Primitive | Antigravity IDE (Host) | Antigravity App | AGY CLI | Antigravity SDK | Compatibility Notes |
|---|:---:|:---:|:---:|:---:|---|
| **Agent Skills (`SKILL.md`)** | ✅ Fully Supported | ✅ Fully Supported | ✅ Supported | ✅ Supported | Universal standard across all surfaces. |
| **Workspace Instructions (`AGENTS.md`)**| ✅ Supported | ✅ Supported | ✅ Supported | ⚠️ Partial | Injected into system prompt every turn. |
| **Modular Rules (`.agents/rules/*.md`)**| ✅ Supported | ✅ Supported | ⚠️ Partial | ⚠️ Partial | CLI does not support manual `@rule` mentions. |
| **Custom Subagents (`agents/*.md`)** | ✅ Supported | ✅ Supported | ⚠️ Limited | ✅ Supported | Custom subagent delegation active in IDE & SDK. |
| **Plugin Packages (`plugin.json`)** | ✅ Supported | ✅ Supported | ✅ Supported | ⚠️ Indirect | `agy plugin validate --strict` supported on CLI. |
| **Lifecycle Hooks (`hooks.json`)** | ✅ Supported | ✅ Supported | ✅ Supported | ❌ Unsupported | Fails open on non-zero exit code. |
| **MCP Servers (`mcp_config.json`)** | ✅ Supported | ✅ Supported | ✅ Supported | ✅ Supported | Streamable HTTP & stdio only. SSE deprecated. |
| **Discovery Manifests (`*.json`)** | ✅ Supported | ✅ Supported | ⚠️ Shallow | ⚠️ Shallow | Overcomes single-level directory scan depth. |
| **Sidecars (`sidecar.json`)** | ❌ **Unsupported** | ✅ Supported | ❌ Unsupported | ❌ Unsupported | App-only background daemon. Disabled in IDE. |
| **Legacy Workflows (`*.yaml`)** | ❌ **Retired** | ❌ **Retired** | ❌ **Retired** | ❌ **Retired** | Cutoff: 19 Oct 2026. Route to `/migrate-workflows`. |

---

### 2. Loading Precedence & Collision Resolution

When assets share identical names across multiple scopes, Antigravity applies strict precedence:

```text
HIGHEST PRECEDENCE (Overrides all others)
  1. Project Workspace:      <workspace>/.agents/skills/<name>/
  2. Local Project Rules:     <workspace>/.agents/rules/<name>.md
  3. Active Plugin Bundles:   <workspace>/.agents/plugins/<plugin>/
  4. Global User Scope:       %USERPROFILE%/.gemini/config/skills/<name>/
  5. Built-in Antigravity:    Internal IDE engine defaults
LOWEST PRECEDENCE
```

#### Collision Handling Rules:
1. **Workspace overrides Global:** A skill or rule defined in `.agents/skills/foo` completely shadows `%USERPROFILE%\.gemini\config\skills\foo`.
2. **Plugins preserve Namespace:** Plugin components should be referenced with their plugin provenance to prevent name hijacking.
3. **Scan Depth Limitation:** Antigravity only scans immediate child folders (depth = 1). Subdirectories nested deeper than 1 level are ignored unless explicitly declared in a discovery manifest (`skills.json`).

---

### 3. Surface-Specific Quirks & Guardrails

| Surface | Known Quirk / Limitation | SkillForge Guardrail |
|---|---|---|
| **Standalone IDE** | Sidecar daemons are not launched. | Marked `APP_ONLY`, set to `enabled_state = 'disabled'`. |
| **AGY CLI** | Rule mentions via `@rule-name` fail silently. | Use `always_on` or `glob` triggers; avoid `manual` triggers. |
| **MCP Transports** | `httpUrl` and `http_sse` rejected in v2.6.0. | Parser flags `deprecated_transport` and warns user. |
| **Subagent Tool Hang** | Misspelled tool names in agent frontmatter cause subagent to hang. | Parser strictly validates tool names against available tool schema. |

---
*Matrix validated against official Antigravity specification.*

