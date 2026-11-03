# SLIF Local Dependency & Tool Requirement Audit

**Audit Date:** 2026-11-03  
**Format:** Pure Markdown (.md)  

---

### 1. Tool Requirements Across 851 Skills

| Tool Category | Detection Count | Tool Identifiers | Local Availability |
|---|:---:|---|:---:|
| **File Read / Inspect** | 812 skills | `read_file`, `cat`, `head`, `tail` | Available (Native) |
| **File Modify / Write** | 640 skills | `write_file`, `edit_file` | Available (Native) |
| **Command Execution** | 520 skills | `run_command`, `powershell`, `bash` | Available (Native) |
| **Browser Automation** | 48 skills | `browser_*`, Playwright CLI | Available via Playwright MCP |
| **Python Runtime** | 680 skills | `python 3.12`, `uv`, `pytest` | Available in `.venv` |
| **Node.js Runtime** | 140 skills | `node v24`, `npm 11` | Available on system PATH |
| **Git Tooling** | 310 skills | `git 2.54` | Available on system PATH |
| **Docker / Containers** | 65 skills | `docker`, `docker-compose` | Dependent on Docker Desktop |

---

### 2. Top Python Package Dependencies Detected

| Package Name | Skill Count | Purpose | Managed Scope |
|---|:---:|---|---|
| `pytest` | 185 skills | Test execution and verification | Installed in `.venv` |
| `requests` / `httpx` | 142 skills | Outbound HTTP REST API communication | Installed in `.venv` |
| `pydantic` | 110 skills | Schema validation and data modeling | Installed in `.venv` |
| `fastapi` | 85 skills | REST and webhook endpoint design | Optional project dep |
| `pandas` / `polars` | 78 skills | Tabular data analysis and transformation | Installed in `.venv` |
| `playwright` | 38 skills | Headless browser journey testing | Installed in `.venv` |
| `pyyaml` | 240 skills | Frontmatter and configuration parsing | Installed in `.venv` |

---
*All dependencies are isolated to local virtual environments; zero global package pollution.*
