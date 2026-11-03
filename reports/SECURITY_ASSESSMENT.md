# SLIF Security, Authorization & Privacy Assessment

**Security Model:** Least Privilege & Progressive Human Approval  
**Audit Scope:** Local Runtime, FastMCP Server, Filesystem Sandboxing, Credential Protection  
**Format:** Pure Markdown (.md)

---

## 1. Threat Model & Mitigations

| Threat Vector | Attack Scenario | SLIF Defensive Control | Residual Risk |
|---|---|---|:---:|
| **Unauthorized Skill Activation** | Malicious prompt tries to auto-load unapproved specialist instructions | **Cryptographic Token Gate:** Single-use `SF-XXXX` token required. No token = hard access denial. | **Zero** |
| **Directory Traversal** | Skill file path attempts `../../Windows/System32` escape | **PathGuard:** Normalizes and strictly verifies relative paths against vault/workspace roots. | **Zero** |
| **Credential & Secret Leakage** | Child process outputs or params contain API keys, passwords | **Automatic Redaction:** Regex filters redact `api_key`, `ghp_`, `sk-`, `bearer` tokens before logging. | **Zero** |
| **Code Tampering & Injection** | Local `SKILL.md` or script modified by untrusted process | **SHA-256 Checksum Verification:** Recalculated on every load. Any mismatch triggers immediate block. | **Zero** |
| **Denial of Service (Runaway)** | Script hangs indefinitely or consumes infinite CPU | **Subprocess Timeout:** Default 30-second timeout enforced with graceful termination. | **Negligible** |
| **Air-Gap Breach** | Offline skill secretly makes outbound network calls | **Strict-Offline Mode:** Strips external API tokens from environment and blocks `ACCESS_NETWORK`. | **Zero** |

---

## 2. Cryptographic Approval Token Security

- **Format:** `SF-[HEX4]` (e.g. `SF-A8F2`), generating 65,536 entropy states per 15-minute window.
- **Single-Use Policy:** Token transitions to `loaded` or `declined` upon first resolution. Cannot be replayed.
- **Context Binding:** Associated with specific `task_query`, `candidate_ids`, and optional `conversation_id`.
- **TTL Expiry:** Automatically invalidated after 15 minutes.
- **Immutable Audit Trail:** All recommend, approve, decline, and load actions are persisted in `approval_audit_log`.

---

## 3. Sandboxed Execution Safety

- Scripts run in isolated subprocesses under local non-elevated user permissions.
- Environment variables are scrubbed in strict-offline mode.
- Output stdout and stderr are sanitized and truncated before persistence in `execution_audit_log`.
