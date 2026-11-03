# SLIF Local Storage & Vault Architecture

**Document Version:** 1.0.0  
**Status:** Approved Specification  
**Format:** Pure Markdown (.md)  

---

### 1. Unified Directory Hierarchy

All SkillForge assets reside in the local project root (`D:\setup\antigravity-skillforge`):

```text
antigravity-skillforge/
├── config/                     # SLIF policies, runtime settings, source registries
│   ├── skillforge.yaml
│   └── policies.yaml
├── vault/                      # Canonical local storage of specialist skills
│   └── skills/
│       ├── python/             # Python engineering skills
│       ├── web-development/    # React, Next.js, Web standards
│       ├── testing/            # Playwright, TDD, mutation testing
│       ├── data-engineering/   # BigQuery, dbt, Spark, SQL tuning
│       ├── cloud/              # GCP, AWS, Terraform, Cloud Run
│       ├── machine-learning/   # RAG, fine-tuning, embeddings, eval
│       ├── security/           # SAST, DAST, REA, reverse engineering
│       └── research/           # 25 Research Intelligence skills
├── data/                       # Local SQLite databases, WAL logs, backups
│   ├── registry.db             # Primary SQLite registry with FTS5
│   └── registry.db.slif_backup # Verified baseline backup
├── cache/                      # Offline snapshots of research papers, patents, APIs
│   ├── papers/
│   ├── patents/
│   └── docs/
├── runtime/                    # Controlled execution environments & sandboxes
│   └── .venv/
├── logs/                       # Comprehensive local audit and performance logs
│   ├── routing.jsonl
│   ├── approval.jsonl
│   └── execution.jsonl
└── reports/                    # Verified Markdown audit and benchmark reports
```

---

### 2. Skill Package Standard Specification

Every skill package in `vault/skills/<category>/<skill-name>/` is self-contained:

```text
<skill-name>/
├── SKILL.md                    # Primary instructions (YAML frontmatter + Markdown body)
├── manifest.json               # Typed metadata, version, license, execution class
├── requirements.txt            # Python dependencies (if needed)
├── scripts/                    # Local helper scripts (read-only until approved)
├── references/                 # Supporting documentation, schemas, templates
└── tests/                      # Local verification test cases
```

---

### 3. Checksum & Immutability Protection

- Every `SKILL.md` file has its SHA-256 hash recorded in the registry upon ingestion.
- Prior to loading or execution, the controlled loader recalculates the SHA-256 hash. If any tampering or unintended modification is detected, loading is blocked and an audit alert is logged.
