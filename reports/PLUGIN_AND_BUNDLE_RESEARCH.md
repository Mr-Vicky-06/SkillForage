# Plugin Bundles & Build with Google Research Blueprint

**Audit Date:** 3 November 2026  
**Audited Runtime:** Antigravity IDE v2.6.0, AGY CLI v1.4.12  
**Format:** Pure Markdown (.md)  

---

### 1. Executive Summary

A plugin is Antigravity’s official distribution package. Unlike an isolated skill folder, a plugin bundles multiple customization primitives under a single versioned manifest (`plugin.json`).

SkillForge models plugins as **first-class containers** (`plugin_bundle`), linking their child skills, subagents, MCP servers, and hooks via `ecosystem_components` without double-counting or inflating the skill inventory.

---

### 2. The 10 Official "Build with Google" Bundles

| Bundle Name | Upstream Repository / Source | Included Primitives | Primary Focus | Acquisition Disposition |
|---|---|---|---|---|
| **Modern Web Guidance** | `GoogleChrome/modern-web-guidance` | Skills, Rules | Web performance, accessibility, Core Web Vitals | Installed (v1.0.4) |
| **Firebase** | `firebase/agent-skills` | Skills, MCP | Auth, Firestore, Security rules, Cloud Functions | Installed (v1.0.0) |
| **Science Skills** | `google-deepmind/science-skills` | 38 Skills, PyMOL | Genomics, structural biology, cheminformatics | Installed (v1.1.0) |
| **Chrome DevTools MCP**| `ChromeDevTools/chrome-devtools-mcp` | MCP Server, Tools | Browser DOM inspection, performance profiling | Installed (v0.21.0) |
| **Android CLI** | `android/agent-tools` | 3 Skills, Sidecars | Android emulator control, Compose preview | Installed (v1.0.16) |
| **Google Antigravity SDK**| `google/antigravity-sdk` | Python SDK, Skills | Autonomous multi-agent coordination & policies | Mirrored locally |
| **Data Agent Kit** | `googlecloudplatform/data-agent-kit` | MCP, 12 Skills | BigQuery, Spark, dbt, Cloud Composer | Configured in MCP |
| **Google Maps Platform**| `googlemaps/agent-skills` | Skills, APIs | Geocoding, Places, routing, geofencing | Discovery candidate |
| **Dart and Flutter** | `flutter/ai-tooling` | Skills, MCP | Cross-platform UI, widget tree inspection | Discovery candidate |
| **Google Cloud Dev** | `GoogleCloudPlatform/agent-skills` | Skills, CLI | Cloud Run, GKE, Terraform, IAM, Secret Mgr | Discovery candidate |

---

### 3. Plugin Manifest Schema & Directory Specification

A valid Antigravity plugin follows this strict directory layout:

```text
<plugin-root>/
├── plugin.json                 # Primary package manifest
├── README.md                   # Human-readable documentation
├── skills/                     # Bundled Agent Skills
│   └── <skill-name>/
│       └── SKILL.md            # Skill name MUST match folder name
├── agents/                     # Bundled Subagent profiles
│   └── <agent-name>.md
├── rules/                      # Bundled modular rules
│   └── <rule-name>.md
├── mcp_config.json             # Bundled MCP server definitions
├── hooks.json                  # Bundled lifecycle hooks
└── sidecars/                   # Bundled App sidecar daemons (App only)
    └── <sidecar-name>/
        └── sidecar.json
```

#### Manifest Validation Rules (`agy plugin validate --strict`):
1. **Name Matching:** The `name` inside `SKILL.md` frontmatter must strictly match the parent directory name.
2. **Read-Only Installation:** The installed plugin directory under `%USERPROFILE%\.gemini\config\plugins\<plugin>` is treated as **read-only** by the Antigravity engine and may be overwritten on update.
3. **Writable Plugin Data:** Writable state must never be stored inside the plugin directory. Plugins use the `${PLUGIN_DATA}` environment variable, which resolves to an isolated workspace cache.

---

### 4. External High-Signal Discovery Catalogs

SkillForge indexes external community catalogs as **discovery references**, applying strict static audits before ingesting any component:

| Catalog Source | URL | Focus | Ingestion Policy |
|---|---|---|---|
| **skills.sh** | `https://skills.sh` | Cross-agent skill telemetry & install counts | Telemetry index only. Popularity is not a safety verdict. |
| **VoltAgent** | `github.com/VoltAgent/awesome-agent-skills`| Curated community skills | Static AST scan; require license & prompt-injection audit. |
| **Anthropic Skills**| `github.com/anthropics/skills` | Architecture, testing, devops | Inspect component licenses individually; verify Antigravity compat. |
| **Superpowers** | `github.com/obra/superpowers` | Engineering workflows | Deduplicate against existing 851 skills before import. |

---
*Report recorded in SkillForge Ecosystem Fabric.*

