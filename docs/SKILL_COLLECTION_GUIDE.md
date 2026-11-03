# SkillForge — Skill Collection & Ingestion Guide

**Purpose:** Managing, Deduplicating, and Indexing Multi-Source Skill Libraries  
**Format:** Pure Markdown (.md)

---

## 1. Supported Skill Sources

SLIF aggregates skills across 5 distinct source types without moving or corrupting original files:

1. **`vault` (`vault/skills/`):** Canonical, versioned local skill packages authored directly for SLIF.
2. **`offline_book` (`D:\setup\vignesh-universal-skill-book`):** Curated static collection of 724 offline engineering skills.
3. **`installed_global` (`%USERPROFILE%\.gemini\config\skills\`):** Global Antigravity skills.
4. **`installed_plugin` (`%USERPROFILE%\.gemini\config\plugins\`):** Plugin-scoped specialist skills (e.g., science plugins, Android CLI).
5. **`installed_project` (`.agents\skills\`):** Project-specific local skills.

---

## 2. Ingestion & Normalization Pipeline

When scanning a new source directory, the SLIF indexer:
1. **Validates Frontmatter:** Checks YAML syntax, required fields, and UTF-8 encoding.
2. **Computes Checksum:** Calculates SHA-256 hash (CRLF/LF normalized).
3. **Detects Duplicates:**
   - Exact hash matches: Identical duplicate content across scopes.
   - Name collisions: Scoped precedence resolution (Project > Global > Vault > Book).
4. **Extracts Technologies & Triggers:** Parses referenced tools, languages, and triggers for semantic graph indexing.
5. **Updates SQLite Registry:** Writes records to `skills`, `skill_tags`, `skill_technologies`.
6. **Rebuilds FTS5 Index:** Updates `skill_fts` with BM25 weights.

---

## 3. Deduplication Policy

- If a skill exists in both `installed_project` and `offline_book`, the project-scoped version takes precedence during routing.
- The registry maintains records of all copies with their source paths, avoiding destructive overwrites.

