# SkillForge Security & Static Content Audit Report

## 1. Audit Policy and Boundaries

SkillForge enforces defense-in-depth static content auditing for every indexed skill:
1. **Prompt Injection / Rule Override Prevention:** Checks for instructions attempting to override platform safety rules (`ignore all previous instructions`, `system prompt override`, `bypass safety`).
2. **Credential & Secret Protection:** Strictly flags patterns attempting to inspect `.env`, extract tokens/passwords, or read browser session profiles.
3. **Destructive Command Detection:** Detects destructive disk wipe commands (`rm -rf /`, `del /s /q c:\`, `format c:`, `drop database`).
4. **Path Traversal Protection:** All resource access via `read_skill_resource` is guarded by canonical path verification preventing directory traversal.
5. **Execution Isolation:** SkillForge retrieves instructions for LLM context ONLY. It never automatically executes shell scripts or binaries from imported skills.

---

## 2. Trust Level Classification Summary

- **Total Reviewed Skills (Clean):** 372
- **Total Unverified Skills (Minor formatting/missing files):** 455
- **Total Quarantined Skills:** 24

## 3. Quarantined Skills Register

| Skill Name | Category | Reason / Security Flags |
|---|---|---|
| `agy-customizations` | `builtin` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/; Referenced files not found on disk: 1 file(s) |
| `android-cli` | `plugin:android-cli-plugin` | Destructive shell command pattern detected: curl[^\n]+\|\s*(ba)?sh |
| `android-device-hub` | `plugin:android-cli-plugin` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/; Suspicious raw IP / tunneling pattern: https?://(?:[0-9]{1,3}\.){3}[0-9]{1,3} |
| `automation` | `builtin` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/ |
| `aws-secrets-rotation` | `cloud` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/ |
| `browser-testing-with-devtools` | `plugin:agent-skills` | Prompt injection / rule override pattern detected: ignore\s+(all\s+)?(previous|prior)\s+instructions |
| `bun-development` | `development` | Destructive shell command pattern detected: curl[^\n]+\|\s*(ba)?sh; Truncated or incomplete description detected |
| `cloud-penetration-testing` | `cloud` | Destructive shell command pattern detected: curl[^\n]+\|\s*(ba)?sh; Suspicious raw IP / tunneling pattern: https?://(?:[0-9]{1,3}\.){3}[0-9]{1,3}; Truncated or incomplete description detected |
| `compose-preview` | `plugin:android-cli-plugin` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/; Suspicious raw IP / tunneling pattern: https?://(?:[0-9]{1,3}\.){3}[0-9]{1,3} |
| `ethical-hacking-methodology` | `security` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/; Truncated or incomplete description detected |
| `file-path-traversal` | `security` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/; Truncated or incomplete description detected |
| `last30days` | `core` | Credential access pattern detected: (read|cat|type|open)\s+([^\n]+\.env) |
| `linkerd-patterns` | `devops` | Destructive shell command pattern detected: curl[^\n]+\|\s*(ba)?sh; Truncated or incomplete description detected; Referenced files not found on disk: 1 file(s) |
| `linux-privilege-escalation` | `security` | Destructive shell command pattern detected: curl[^\n]+\|\s*(ba)?sh; Truncated or incomplete description detected; Referenced files not found on disk: 1 file(s) |
| `metasploit-framework` | `security` | Prompt injection / rule override pattern detected: bypass\s+(safety|security|policy|restrictions); Credential access pattern detected: (extract|dump|steal|export)\s+(passwords?|tokens?|cookies|keys); Truncated or incomplete description detected; Referenced files not found on disk: 1 file(s) |
| `migrate-workflows` | `builtin` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/ |
| `plugin` | `builtin` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/ |
| `privilege-escalation-methods` | `security` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/; Truncated or incomplete description detected |
| `sharp-edges` | `core` | Prompt injection / rule override pattern detected: bypass\s+(safety|security|policy|restrictions) |
| `source-driven-development` | `plugin:agent-skills` | Prompt injection / rule override pattern detected: ignore\s+(all\s+)?(previous|prior)\s+instructions |
| `ssh-penetration-testing` | `security` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/; Truncated or incomplete description detected |
| `ui-plugin-navigation` | `builtin` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/ |
| `uv` | `plugin:science` | Destructive shell command pattern detected: curl[^\n]+\|\s*(ba)?sh |
| `workflow-skill-creator` | `plugin:science` | Credential access pattern detected: (\.gemini|\.aws|\.ssh|\.gnupg)/ |

---

## 4. Path Traversal & Sandboxing Verification

- `PathTraversalError` unit tests executed: Traversal attempts targeting `../../Windows/System32` or root directories are immediately blocked with `PathTraversalError`.
- Workspace exclusion: `.env`, `.git`, `node_modules`, `.venv`, and private keys are strictly excluded from project workspace scans.