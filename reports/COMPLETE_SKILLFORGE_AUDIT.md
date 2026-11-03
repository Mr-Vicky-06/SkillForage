# SkillForge Local Intelligence Fabric (SLIF) - Complete Baseline Audit

**Audit Date:** 2026-11-03  
**Audited Runtime:** Windows 11 x64, Google Antigravity IDE v2.6.0, AGY CLI v1.4.12, Python 3.12.10  
**Registry Database:** `data/registry.db` (Backed up to `data/registry.db.slif_backup`)  
**Format:** Pure Markdown (.md)  

---

### 1. Executive Summary & Core Metric Breakdown

| Audit Metric | Audited Count | Percentage | Verification Status |
|---|:---:|:---:|---|
| **Total Cataloged Skills** | **851** | 100.0% | VERIFIED in `data/registry.db` |
| **Files Existing on Disk** | **851** | 100.0% | VERIFIED (0 missing files) |
| **Unique Skill Names** | **830** | 97.5% | 830 unique functional skill names |
| **Duplicate Name Instances** | **34** | 4.0% | Across 13 distinct duplicate groups |
| **Exact Content Hash Duplicates** | **24** | 2.8% | Across 12 SHA-256 duplicate groups |
| **Fully Offline Capable** | **458** | 53.8% | Zero network/API calls required |
| **Requires Internet (Direct HTTPS)**| **252** | 29.6% | Calls public APIs/web endpoints |
| **Requires API Credentials / Tokens**| **141** | 16.6% | Requires API keys (OpenAI, GitHub, SEC) |
| **Incomplete / Stub Skills** | **26** | 3.1% | < 100 chars or missing description |
| **Invalid YAML Frontmatter** | **0** | 0.0% | 100% compliant frontmatter syntax |

---

### 2. Source Distribution

```text
+-------------------------------------------------------------------------------+
|                        SKILL INVENTORY SOURCE DISTRIBUTION                    |
+-------------------------------------------------------+-----------------------+
| Offline Universal Skill Book (D:\setup\vignesh...)    | 724 skills (85.1%)    |
| Installed Plugins (agent-skills, science, android)    |  66 skills ( 7.8%)    |
| Global Config (%USERPROFILE%\.gemini\config\skills)   |  44 skills ( 5.2%)    |
| Native Antigravity Built-ins                          |   9 skills ( 1.1%)    |
| Project Scoped (.agents\skills)                       |   8 skills ( 0.9%)    |
+-------------------------------------------------------+-----------------------+
| TOTAL INDEXED SKILLS                                  | 851 skills (100.0%)   |
+-------------------------------------------------------+-----------------------+
```

---

### 3. Critical Architectural Discoveries

1. **Zero Missing Files:** Every one of the 851 recorded skills exists as a physical `SKILL.md` file on the local filesystem.
2. **Duplicate Source Patterns:** The 34 duplicate instances occur primarily because skills were mirrored between global scope (`%USERPROFILE%\.gemini\config\skills`) and workspace scope (`.agents\skills`).
3. **53.8% Pure Offline Operation:** 458 skills require zero network connectivity and execute entirely against local files, AST parsers, regex tokenizers, and local SQLite tables.
4. **Controlled Remote Access:** 252 skills request external web resources directly from the local machine (e.g. arXiv, PubMed, GitHub GraphQL). No external SkillForge backend or proxy exists.
