# SkillForge Master Inventory Report

**Generated:** 2026-11-03T05:11:13.366042+00:00
**Total Distinct Skills Indexed:** 851
**Database Registry:** `data/registry.db` (SQLite with FTS5 BM25 search)

---

## 1. Inventory by Source Distribution

| Source Type | Count | Description |
|---|---:|---|
| `offline_book` | 724 | Stored offline in `D:\setup\vignesh-universal-skill-book` |
| `installed_plugin` | 66 | Provided by active plugins in `%USERPROFILE%\.gemini\config\plugins` |
| `installed_global` | 44 | Canonical global skills in `%USERPROFILE%\.gemini\config\skills` |
| `installed_builtin` | 9 | Shipped with Antigravity runtime builtin |
| `installed_project` | 8 | Scoped to active project in `.agents\skills` |

---

## 2. Inventory by Trust & Verification Level

| Trust Level | Count | Definition |
|---|---:|---|
| `REVIEWED` | 372 | Passed static inspection with 0 security or formatting flags |
| `UNVERIFIED` | 455 | Valid skills with minor formatting notes (e.g. truncated descriptions or missing auxiliary references) |
| `QUARANTINED` | 24 | Flagged for security risks (prompt injection, credential harvesting, or destructive patterns) - excluded from recommendations |

---

## 3. Inventory by Major Domain Categories

| Category | Count | Focus Area |
|---|---:|---|
| `core` | 100 | Skills covering core domain |
| `development` | 98 | Skills covering development domain |
| `ai` | 80 | Skills covering ai domain |
| `web` | 56 | Skills covering web domain |
| `security` | 52 | Skills covering security domain |
| `data` | 49 | Skills covering data domain |
| `global` | 44 | Skills covering global domain |
| `workflow` | 44 | Skills covering workflow domain |
| `devops` | 43 | Skills covering devops domain |
| `cloud` | 39 | Skills covering cloud domain |
| `plugin:science` | 38 | Skills covering plugin:science domain |
| `backend` | 37 | Skills covering backend domain |
| `testing` | 35 | Skills covering testing domain |
| `product` | 34 | Skills covering product domain |
| `documentation` | 25 | Skills covering documentation domain |
| `plugin:agent-skills` | 25 | Skills covering plugin:agent-skills domain |
| `architecture` | 13 | Skills covering architecture domain |
| `builtin` | 9 | Skills covering builtin domain |
| `project` | 8 | Skills covering project domain |
| `custom` | 7 | Skills covering custom domain |
| `ui-ux-pro-max-skill` | 7 | Skills covering ui-ux-pro-max-skill domain |
| `3d` | 5 | Skills covering 3d domain |
| `plugin:android-cli-plugin` | 3 | Skills covering plugin:android-cli-plugin domain |

---

## 4. Reconciled Differences from Initial Catalog Snapshot

- **Initial Catalog Snapshot (`ALL_SKILLS_CATALOG.md`):** Recorded 828 skills (117 installed, 711 available).
- **Filesystem Discovery:** Scanned 868 total skill directories across offline, global, plugin, project, and builtin paths.
- **Indexed Active Records in Registry:** **851** distinct skills indexed with full FTS5 search indexes.
- **Preservation Status:** All source skill books and existing installed Antigravity directories remain strictly **READ-ONLY** and completely untouched.