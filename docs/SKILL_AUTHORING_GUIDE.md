# SkillForge — Skill Authoring & Packaging Guide

**Specification:** SLIF Skill Package v1.0  
**Format:** Pure Markdown (.md)

---

## 1. Skill Package Standard Structure

Every skill residing in the canonical local vault (`vault/skills/<category>/<skill-name>/`) must adhere to this folder layout:

```text
<skill-name>/
├── SKILL.md             # Primary instructions (YAML frontmatter + Markdown body)
├── manifest.json        # Typed machine-readable metadata & permissions
├── scripts/             # Local automation and validation scripts
│   └── helper.py
├── references/          # Supporting specs, diagrams, templates
│   └── playbook.md
└── tests/               # Local test cases
    └── test_skill.py
```

---

## 2. Frontmatter Standard (`SKILL.md`)

The top of `SKILL.md` must begin with valid YAML frontmatter:

```yaml
---
name: my-specialist-skill
description: Concise 1-2 sentence description explaining when and why to use this skill.
category: research
subcategory: empirical-methodology
tags: ["testing", "validation", "automation"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: true
required_permissions:
  - READ_LOCAL_FILES
  - WRITE_LOCAL_FILES
---
```

### Frontmatter Fields:
- `name` (required): Lowercase, kebab-cased unique name matching directory name.
- `description` (required): Informative summary indexed by FTS5 for BM25 retrieval.
- `category` (required): One of `core`, `development`, `ai`, `web`, `security`, `data`, `cloud`, `research`, `testing`, `backend`.
- `offline_capable` (required): Boolean indicating whether the skill can operate with zero internet connection.
- `required_permissions` (required): Declared permissions (`READ_LOCAL_FILES`, `WRITE_LOCAL_FILES`, `EXECUTE_SCRIPT`, `ACCESS_NETWORK`).

---

## 3. Package Manifest (`manifest.json`)

```json
{
  "id": "research--my-specialist-skill",
  "name": "my-specialist-skill",
  "title": "My Specialist Skill Title",
  "description": "Comprehensive explanation of capabilities.",
  "version": "1.0.0",
  "category": "research",
  "subcategory": "empirical-methodology",
  "author": "SkillForge Team",
  "license": "MIT",
  "offline_capable": true,
  "required_permissions": [
    "READ_LOCAL_FILES",
    "WRITE_LOCAL_FILES"
  ],
  "tags": ["testing", "validation"],
  "entrypoint": "SKILL.md",
  "sha256": "computed_sha256_of_skill_md",
  "external_apis": []
}
```

---

## 4. Registering & Indexing

To index new skills into the local database and rebuild FTS5:

```bash
.\.venv\Scripts\python scripts/sync_fts.py
```

Run test suite to verify checksums and integrity:
```bash
.\.venv\Scripts\pytest -q
```

