# SkillForge — Troubleshooting & Diagnostic Guide

**Platform:** Google Antigravity & SkillForge SLIF  
**Format:** Pure Markdown (.md)

---

## 1. Common Issues & Quick Resolutions

### 1.1 Approval Token Expired (`SF-XXXX`)
- **Symptom:** `ACCESS DENIED: Approval token 'SF-XXXX' has expired.`
- **Cause:** Tokens enforce a strict 15-minute TTL to prevent stale unauthorized activations.
- **Resolution:** Ask Antigravity to re-recommend skills for the task. A fresh token will be generated immediately.

### 1.2 Checksum Mismatch / Integrity Violation
- **Symptom:** `INTEGRITY VIOLATION: Skill 'xxx' hash mismatch. Expected aaa, got bbb. File may have been altered.`
- **Cause:** The `SKILL.md` file was edited on disk without re-indexing, or was modified by an unauthorized script.
- **Resolution:** If the edit was intentional, re-compute the hash and update `skills.file_hash` in `data/registry.db`, then run `scripts/sync_fts.py`.

### 1.3 Path Traversal Alert
- **Symptom:** `PathTraversalError: Path traversal attempt detected: ...`
- **Cause:** A skill or resource request attempted to access files outside the allowable project or vault root.
- **Resolution:** Check that the relative path does not contain `../` or absolute drive roots (`C:\`, `D:\`).

### 1.4 SQLite Database Locked (`busy` / `locked`)
- **Symptom:** `sqlite3.OperationalError: database is locked`
- **Cause:** Multiple concurrent processes writing to SQLite without WAL mode.
- **Resolution:** SLIF enables WAL mode by default. Check `PRAGMA journal_mode = WAL;`. Ensure background tasks close connections cleanly.

---

## 2. Diagnostic Commands

### Comprehensive System Health Check
```bash
.\.venv\Scripts\python -c "from skillforge.database.repository import SkillRepository; from skillforge.mcp_server.tools import SkillForgeTools; t = SkillForgeTools(SkillRepository('data/registry.db')); print(t.skillforge_health())"
```

### Run All Test Suites
```bash
.\.venv\Scripts\pytest -v
```

