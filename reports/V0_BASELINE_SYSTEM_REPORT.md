# SkillForge V0 Baseline System & Performance Report

**Document Version:** 1.0.0 (Immutable V0 Reference)  
**Date:** 2026-11-03T05:58:17Z  
**Environment:** Windows 11 x64, Python 3.12.10, uv 0.13.6  
**Database:** SQLite 3 WAL mode with FTS5 virtual table  

---

## 1. Registry Inventory & Source Distribution

- **Total Indexed Distinct Skills:** 851
- **Database File Size:** 2.34 MB (2,449,408 bytes)
- **Total Categories:** 23

| Source Layer | Skill Count | Description |
|---|---:|---|
| `offline_book` | 724 | Offline universal library (`D:\setup\vignesh-universal-skill-book`) |
| `installed_plugin` | 66 | Plugins in `%USERPROFILE%\.gemini\config\plugins` |
| `installed_global` | 44 | Canonical global skills in `%USERPROFILE%\.gemini\config\skills` |
| `installed_builtin` | 9 | Antigravity runtime builtin skills |
| `installed_project` | 8 | Project-scoped skills in `.agents\skills` |

---

## 2. Trust and Security Distribution

| Trust Level | Count | Assessment |
|---|---:|---|
| `REVIEWED` | 372 | 0 security flags, clean structure and frontmatter |
| `UNVERIFIED` | 455 | Minor formatting issues, truncated descriptions, or phantom references |
| `QUARANTINED` | 24 | High risk flags (destructive disk commands, prompt injection) - excluded |

---

## 3. Latency & Performance Percentiles (Cold vs. Warm)

| Operation | Cold (First) | p50 (Median) | p95 (Tail) | Mean | Min | Max | Sample Size |
|---|---:|---:|---:|---:|---:|---:|---:|
| **FTS5 Search Query** | 4.66 ms | 1.65 ms | 2.87 ms | 1.47 ms | 0.31 ms | 3.62 ms | 50 queries |
| **Context-Aware Recommendation** | N/A | 31.6 ms | 42.68 ms | 32.39 ms | 25.13 ms | 42.68 ms | 20 tasks |
| **Skill Content Loading** | N/A | 0.56 ms | 1.72 ms | 0.72 ms | 0.3 ms | 1.72 ms | 20 skills |
| **Workspace Context Detection** | 7.7 ms | - | - | 7.7 ms | - | - | 1 scan |
| **Incremental Registry Scan** | 6189.85 ms | - | - | 6189.85 ms | - | - | 868 items |

---

## 4. Initial Accuracy & Test Suite Baselines

- **Contextual Benchmark Accuracy:** Top-1: 90.0%, Top-3: 100.0% (across 10 project contexts)
- **PyTest Unit & Integration Tests:** 21 / 21 passing in 3.74s
- **Path Traversal Security:** 100% blocked with `PathTraversalError`
- **Secret Exposure:** 0 leaks (strictly ignores `.env`, `.git`, `node_modules`, `.venv`)

---

## 5. Identified Architectural Limitations of V0 Baseline

1. **No Typed Knowledge Graph:** Relationships between technologies, frameworks, and tasks are implicit; multi-hop reasoning is absent.
2. **Lexical-Dominant Retrieval:** Lacks Reciprocal Rank Fusion (RRF) and semantic vector search.
3. **Simple Project Boundaries:** Previous sandbox defaulted to `D:\setup` rather than the exact workspace root (`D:\setup\antigravity-skillforge`).
4. **No Self-Evolution Loop:** No mechanism for the system to detect missing knowledge, formulate learning goals, acquire skills, and test improvements autonomously.