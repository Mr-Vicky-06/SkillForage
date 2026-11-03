# SLIF Skill Execution & Progressive Disclosure Runtime Architecture

**Document Version:** 1.0.0  
**Status:** Approved Specification  
**Format:** Pure Markdown (.md)  

---

### 1. Progressive Disclosure Architecture

To protect the model context window, information is partitioned into 5 discrete tiers:

```text
TIER 1: Skill Metadata (Loaded at routing time)
└── Name, ID, Domain, Summary, Priority, Dependencies, Network Requirement (~150 tokens)

TIER 2: Core Instructions (Loaded upon user approval)
└── SKILL.md standard methodology, parameters, and constraints (1,000 - 4,000 tokens)

TIER 3: Supporting References (Loaded on demand via read_skill_resource)
└── Detailed schemas, cheat sheets, benchmark tables (only when referenced)

TIER 4: Executable Scripts (Executed locally through run_command)
└── Python/Bash helper scripts run in subprocess sandboxes; outputs captured to stdout

TIER 5: Generated Outputs & Artifacts
└── Output reports, modified project files, test evidence logs
```

---

### 2. Execution Classification Matrix

| Execution Class | Description | Network Policy | Credential Policy |
|---|---|---|---|
| `FULL_LOCAL` | Executes 100% locally using local AST, SQLite, or files. | Zero network access | Zero credentials needed |
| `LOCAL_WITH_OPTIONAL_INTERNET`| Operates offline, but can fetch fresh data if connected. | Optional outbound HTTPS | Optional |
| `LOCAL_WITH_REQUIRED_INTERNET`| Requires live outbound data (e.g. arXiv, OpenAlex, GitHub). | Direct outbound HTTPS | Public endpoints (No API key) |
| `LOCAL_WITH_API_CREDENTIALS` | Requires developer API key (e.g. SEC EDGAR, EPO OPS, OpenAI). | Direct outbound HTTPS | Stored in env vars only |
| `EXTERNAL_APPLICATION_REQUIRED`| Requires local desktop app (e.g. Docker Desktop, PyMOL). | Local IPC / stdio | N/A |
| `UNSUPPORTED_OR_INCOMPLETE` | Stub or incomplete skill. Quarantined from routing. | Blocked | Blocked |

---

### 3. Local Script Sandboxing

- Helper scripts execute via `subprocess.run` with explicit timeouts (default: 30s).
- Working directory is scoped strictly to the current workspace root.
- Environment variables containing system secrets are never exposed in subprocess logs.
