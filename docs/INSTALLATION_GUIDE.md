# SkillForge Local Intelligence Fabric (SLIF) — Installation & Setup Guide

**Target Environment:** Local Machine (Windows 11 / Linux / macOS)  
**Antigravity Compatibility:** Google Antigravity 2.6.0+  
**Format:** Pure Markdown (.md)

---

## 1. System Requirements

- **Operating System:** Windows 10/11 (x64), Linux (Ubuntu 22.04+), or macOS (Sonoma+)
- **Python Runtime:** Python 3.12+ (64-bit)
- **Virtual Environment Tool:** `venv` or `uv`
- **Database Engine:** SQLite 3.38+ with FTS5 support (bundled with standard Python distribution)
- **Network Requirement:** Zero external servers or cloud services. 100% local operation.

---

## 2. Directory Layout Setup

Clone or place SkillForge in a dedicated local directory:

```text
D:\setup\antigravity-skillforge\
├── config/             # Runtime policies and settings
├── data/               # SQLite database (registry.db) and backups
├── vault/skills/       # Canonical storage of specialist skills
│   └── research/       # 25 Research Intelligence skills
├── src/skillforge/     # Core SLIF engine modules
├── tests/              # 54 automated pytest verification tests
├── reports/            # Formal audit and benchmark reports
└── docs/               # System documentation and manuals
```

---

## 3. Python Virtual Environment & Dependencies

Initialize a local virtual environment and install core packages:

```bash
cd D:\setup\antigravity-skillforge
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Install runtime dependencies:
pip install mcp pytest anyio pyyaml
```

---

## 4. SQLite Registry Database Initialization

Initialize the database schema with migrations:

```bash
.\.venv\Scripts\python -c "from skillforge.database.migrations import init_database; init_database('data/registry.db')"
```

This creates the canonical SLIF tables:
- `skills`, `skill_tags`, `skill_triggers`, `skill_technologies`, `skill_dependencies`
- `skill_fts` (FTS5 full-text search)
- `pending_approvals` (Cryptographic single-use token tracking)
- `approval_audit_log` (Audit records of human decisions)
- `execution_audit_log` (Sandboxed local execution logs with redacted parameters)
- `research_cache` (Content-addressable SHA-256 cache)
- `cross_verification_records` (Fact-checking and citation validation history)

---

## 5. Antigravity FastMCP Server Registration

Configure the local stdio MCP server in `%USERPROFILE%\.gemini\antigravity\mcp_config.json` or workspace settings:

```json
{
  "mcpServers": {
    "skillforge": {
      "command": "D:\\setup\\antigravity-skillforge\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "skillforge.mcp_server.server"
      ],
      "env": {
        "SKILLFORGE_DB_PATH": "D:\\setup\\antigravity-skillforge\\data\\registry.db"
      }
    }
  }
}
```

---

## 6. Verification of Installation

Run the full automated test suite to confirm complete operational readiness:

```bash
.\.venv\Scripts\pytest -q
```
*Expected Output:* `54 passed in <5s`.

