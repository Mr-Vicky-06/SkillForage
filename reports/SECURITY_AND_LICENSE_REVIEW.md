# Security, Supply-Chain & License Governance Review

**Audit Date:** 3 November 2026  
**Audited Systems:** Antigravity IDE (v2.6.0), SkillForge Registry, 851 Skills, 15 MCP Servers  
**Format:** Pure Markdown (.md)  

---

### 1. The Core Security Doctrine

> [!IMPORTANT]
> **Imported assets are untrusted data, never execution authority.**  
> An agent skill, rule, or plugin cannot unilaterally grant itself elevated permissions, override Antigravity's system prompt, or disable approval prompts.

```text
+---------------------------------------------------------------+
|                    STATIC SECURITY DEFENSE GATES              |
+-------------------+--------------------+----------------------+
| 1. AST Parser     | 2. Injection Scan  | 3. License Audit     |
| Static inspection | Regex heuristics   | SPDX classification  |
| No script exec    | Prompt overrides   | Copyleft detection   |
+-------------------+--------------------+----------------------+
```

---

### 2. Threat Vector Analysis & Static Guardrails

| Threat Vector | Detection Pattern / Heuristic | Risk Level | Action Taken |
|---|---|:---:|---|
| **System Prompt Override** | `Ignore previous instructions`, `You are now in developer mode`, `DAN` | High | Quarantined immediately. Flagged in `asset_evidence`. |
| **Secret Harvesting** | Scanning for `.env`, `id_rsa`, `cookies.sqlite`, `credentials.json` | Critical | Blocked. Asset marked `QUARANTINED`. |
| **Destructive Commands** | `rm -rf /`, `del /s /q`, `Format-Volume`, `mkfs` | Critical | Flagged in `HookParser`. Requires explicit user sign-off. |
| **Remote Shell Execution**| `curl ... \| sh`, `wget ... \| bash`, `powershell -enc` | High | Flagged as `high_risk_destructive`. Execution disabled. |
| **Path Traversal / Escape**| `../../../../`, symlinks pointing to Windows system roots | High | PathGuard blocks path resolution outside workspace. |
| **Failing-Open Hooks** | Relying solely on `hooks.json` exit code for security | Medium | Warned: Non-zero exits fail open per Antigravity spec. |

---

### 3. Open-Source License & SPDX Governance

Every asset indexed in SkillForge is categorized by its SPDX license identifier to protect proprietary IP:

| License Category | SPDX Identifiers | Permissible Scope | Risk Assessment |
|---|---|---|---|
| **Permissive** | `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC` | Global & Workspace | **Safe:** Full commercial use, private modification permitted. |
| **Google Official** | `Google-Proprietary-Docs`, `Google-Official` | Global & Workspace | **Safe:** Authorized for Antigravity developer tooling. |
| **Weak Copyleft** | `LGPL-2.1`, `LGPL-3.0`, `MPL-2.0` | Workspace Only | **Caution:** Library modification triggers disclosure requirements. |
| **Strong Copyleft**| `GPL-2.0`, `GPL-3.0`, `AGPL-3.0` | Quarantined / Review | **High Risk:** Viral license terms can compromise proprietary codebases. |

---

### 4. Quarantine Protocol

When an asset triggers security flags:
1. **Zero Data Loss:** Original files are never deleted; provenance is preserved.
2. **Registry Containment:** Asset status is set to `QUARANTINED` in `ecosystem_assets` and `skills`.
3. **Retrieval Exclusion:** Quarantined assets are excluded from ranking pipelines and MCP recommendations.
4. **Evidence Logging:** Exact file offset, regex trigger, and hash are recorded in `asset_evidence`.

---
*Review verified by SkillForge Static Security Auditor.*
