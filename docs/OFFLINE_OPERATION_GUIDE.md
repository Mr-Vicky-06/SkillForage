# SkillForge — Strict-Offline Operation Guide

**Feature:** 100% Air-Gapped and Offline Execution  
**Format:** Pure Markdown (.md)

---

## 1. Offline Architectural Foundation

SLIF is designed from the ground up to operate without external servers:
- **Registry & Graph:** Embedded SQLite database (`data/registry.db`) with Write-Ahead Logging (WAL).
- **Search Engine:** Built-in SQLite FTS5 extension.
- **Skill Instructions:** Stored directly on local SSD (`vault/skills/` and local source folders).
- **Execution Sandboxing:** Subprocess execution running local Python, Node, Shell scripts.
- **Research Cache:** Local SQLite content-addressable cache with SHA-256 keys.

---

## 2. Enabling Strict-Offline Mode

To enforce strict-offline execution where no outbound network connections are permitted:

### Method 1: Environment Variable
```bash
set SKILLFORGE_OFFLINE_MODE=1
```

### Method 2: Executor Parameter
When invoking `LocalSkillExecutor(repo, strict_offline=True)`:
- Strips external API tokens (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`) from child process environments.
- Blocks execution of any skill requesting `ACCESS_NETWORK` permission.
- Rejects external HTTP requests at runtime.

---

## 3. Offline Research & Documentation Snapshots

- All previously queried research papers, SEC filings, and patent classification matrices are cached in `research_cache`.
- Cache lookups use content-addressable SHA-256 keys. If offline, the research engine serves cached responses without querying remote APIs.

