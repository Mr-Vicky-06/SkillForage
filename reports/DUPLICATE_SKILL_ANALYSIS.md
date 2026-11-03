# SLIF Duplicate Skill Analysis & Reconciliation Matrix

**Audit Date:** 2026-11-03  
**Registry Scope:** 851 Skills  
**Format:** Pure Markdown (.md)  

---

### 1. Summary of Duplicates

- **Unique Skill Names:** 830
- **Duplicate Name Groups:** 13 groups (34 total instances)
- **Exact Content Hash Duplicates:** 12 groups (24 instances)

---

### 2. Duplicate Name Groups & Provenance

| Skill Name | Instances | Conflicting Source Scopes | Recommended Reconciliation |
|---|:---:|---|---|
| `agent-memory-systems` | 2 | installed_global, offline_book | Canonicalize to local vault; alias secondary scopes. |
| `banner-design` | 3 | installed_global, offline_book, installed_project | Canonicalize to local vault; alias secondary scopes. |
| `brand` | 3 | installed_global, offline_book, installed_project | Canonicalize to local vault; alias secondary scopes. |
| `conversation-memory` | 2 | installed_global, offline_book | Canonicalize to local vault; alias secondary scopes. |
| `design` | 3 | installed_global, offline_book, installed_project | Canonicalize to local vault; alias secondary scopes. |
| `design-system` | 3 | installed_global, offline_book, installed_project | Canonicalize to local vault; alias secondary scopes. |
| `memory-systems` | 2 | installed_global, offline_book | Canonicalize to local vault; alias secondary scopes. |
| `playwright-cli` | 2 | installed_global, installed_project | Canonicalize to local vault; alias secondary scopes. |
| `rag-implementation` | 2 | installed_global, offline_book | Canonicalize to local vault; alias secondary scopes. |
| `slides` | 3 | installed_global, offline_book, installed_project | Canonicalize to local vault; alias secondary scopes. |
| `test-driven-development` | 2 | installed_plugin, offline_book | Canonicalize to local vault; alias secondary scopes. |
| `ui-styling` | 3 | installed_global, offline_book, installed_project | Canonicalize to local vault; alias secondary scopes. |
| `ui-ux-pro-max` | 4 | installed_global, offline_book, offline_book, installed_project | Canonicalize to local vault; alias secondary scopes. |

---

### 3. Exact Content Duplicates (Identical SHA-256)

These skills share identical byte-for-byte `SKILL.md` contents across multiple paths:
- **SHA-256 `87fa830f0d822b85...`**:
  - `installed_global:global:agent-memory-systems`
  - `offline_book:ai:agent-memory-systems`
- **SHA-256 `913d9c4b2a3b405d...`**:
  - `installed_global:global:banner-design`
  - `installed_project:project:banner-design`
- **SHA-256 `6a450ee1a83a403d...`**:
  - `installed_global:global:brand`
  - `installed_project:project:brand`
- **SHA-256 `613cadf73d2209e4...`**:
  - `installed_global:global:conversation-memory`
  - `offline_book:core:conversation-memory`
- **SHA-256 `413f4ab913d07f7f...`**:
  - `installed_global:global:design`
  - `installed_project:project:design`
- **SHA-256 `655468bb723a6bc9...`**:
  - `installed_global:global:design-system`
  - `installed_project:project:design-system`
- **SHA-256 `205f520b9af51e85...`**:
  - `installed_global:global:memory-systems`
  - `offline_book:ai:memory-systems`
- **SHA-256 `b07a6cbe4e5b6380...`**:
  - `installed_global:global:playwright-cli`
  - `installed_project:project:playwright-cli`
- **SHA-256 `29eedf1f2f7e4125...`**:
  - `installed_global:global:rag-implementation`
  - `offline_book:ai:rag-implementation`
- **SHA-256 `2b90bdaf63f23191...`**:
  - `installed_global:global:slides`
  - `installed_project:project:slides`
- **SHA-256 `f8b6c3832d2af51f...`**:
  - `installed_global:global:ui-styling`
  - `installed_project:project:ui-styling`
- **SHA-256 `5905a2b470ca8607...`**:
  - `installed_global:global:ui-ux-pro-max`
  - `installed_project:project:ui-ux-pro-max`
