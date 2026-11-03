# SkillForge Local Intelligence Fabric (SLIF) — User Guide

**Target Audience:** Antigravity AI Assistant & Engineering Operators  
**Platform:** Google Antigravity IDE & CLI  
**Format:** Pure Markdown (.md)

---

## 1. How SLIF Works

SkillForge acts as an on-demand, local intelligent skill registry hosting 876+ specialized Agent Skills. Rather than cluttering your context window with all skills (which costs ~85,000 tokens), SkillForge keeps skills in an offline vault and provides dynamic retrieval.

### The Human Approval Gate
Specialist skill instructions and scripts are **never** loaded into memory or executed without your explicit conversational approval.

---

## 2. Day-to-Day Antigravity Workflow

```text
┌────────────────┐     Task Context     ┌────────────────────────┐
│ Human Operator │ ───────────────────> │ Antigravity Assistant  │
└────────────────┘                      └───────────┬────────────┘
        ▲                                           │ 1. Evaluates task
        │                                           ▼
        │ 3. Asks Approval             ┌────────────────────────┐
        │    Token: SF-XXXX            │ skillforge_recommend_   │
        ├───────────────────────────── │ skills                 │
        │                              └────────────────────────┘
        │
   User Replies:
   - "YES"            ───> 4. skillforge_load_approved_skills
   - "SELECT <id>"    ───>    (Loads full instructions into context)
   - "NO"             ───> 4. skillforge_decline_skills
                              (Proceeds with standard capabilities)
```

---

## 3. Human Response Commands

When Antigravity presents candidate skills:

1. **`YES` (or `Approve`):**
   Approves all recommended skills. Antigravity calls `skillforge_load_approved_skills` with the token.
2. **`SELECT <skill-name-or-id>`:**
   Approves only the named skill. Antigravity loads only that specific skill instructions.
3. **`NO` (or `Decline`):**
   Declines the recommendation. Antigravity records the decision and continues using built-in knowledge without loading specialist instructions.

---

## 4. Research Intelligence Protocol

When conducting technical, academic, or market research:
1. Antigravity identifies candidate research skills (e.g., `systematic-literature-review-prisma`, `sec-edgar-financial-analysis`, `patent-prior-art-search`).
2. After approval, the instructions guide data extraction.
3. For factual verification, Antigravity calls `skillforge_cross_source_verify`:
   - Classifies sources into Tier 1 (peer-reviewed, official government filings), Tier 2 (preprints, tech blogs), or Tier 3 (unverified).
   - Detects contradictions across sources.
   - Outputs a verified confidence matrix.

---

## 5. Local Script Execution

If a loaded skill contains an automated script (e.g. `scripts/verify.py`):
1. Antigravity requests execution permission.
2. The script runs locally via `skillforge_execute_script`.
3. Execution enforces a default 30-second timeout and redacts secrets from parameters and output logs.

