# SkillForge Research Intelligence Blueprint
## Advanced Research Skills: Comprehensive Gap Analysis & Target Capabilities

**Report Date:** 2026-11-03  
**Target Platform:** Google Antigravity & SkillForge Local Knowledge Fabric  
**Scope:** Academic, Technical, Market, Competitive, Patent, and Empirical Research  
**Format:** Pure Markdown (.md)  

---

### 1. Current State of Research Skills in SkillForge

A targeted audit of `data/registry.db` reveals **10 active research-related skills** out of 851:

```text
CURRENT RESEARCH SKILL INVENTORY (10 Skills):
Academic Preprints / Literature:  5 skills (arXiv, bioRxiv, Europe PMC, OpenAlex, PubMed)
General / Conversational AI:     4 skills (deep-research, context7-auto-research, research-engineer, wiki-researcher)
Knowledge Graph Extraction:      1 skill  (graphify)
```

#### What We Have Today:
- **Strengths:** Excellent biomedical and life sciences preprint search (PubMed, bioRxiv, Europe PMC) and broad bibliographic search via OpenAlex.
- **The Blind Spot:** In modern engineering and AI organizations, research is far broader than pulling PubMed abstracts. We currently lack skills for **competitive market teardowns, patent prior art discovery, technology benchmark spikes (ADR/RFC), open-source ecosystem health analysis, and statistical experiment design**.

---

### 2. The 6 Critical Research Domains & 24 Target Skills

To turn SkillForge into an **autonomous Research Intelligence engine**, we define 6 core research domains and 24 specialized target skills:

```text
┌────────────────────────────────────────────────────────┐
│            THE 6 RESEARCH INTELLIGENCE DOMAINS         │
├──────────────────────────┬─────────────────────────────┤
│ 1. Scholarly Literature  │ 2. Tech Architecture Spikes │
│ 3. Market & Competitive  │ 4. Patents & Intellectual P.│
│ 5. Open-Source Ecosystem │ 6. Empirical & Synthesis    │
└──────────────────────────┴─────────────────────────────┘
```

---

#### 📚 DOMAIN 1: Scholarly Literature & Deep Academic Discovery
*Moving beyond raw keyword searches into citation graphs, systematic reviews, and publication drafting.*

| Priority | Target Skill Name | Primary APIs / Tools | Target Research Capability |
| :---: | :--- | :--- | :--- |
| **P0** | `semantic-scholar-citation-graph` | Semantic Scholar API, S2AG, Connected Papers | Maps paper citation trees, co-citations, highly influential citations, and author h-index trajectories. |
| **P0** | `systematic-literature-review-prisma` | PRISMA 2020 Protocol, Screening Matrix | Structures systematic literature reviews: inclusion/exclusion criteria, deduplication, and quality assessment. |
| **P1** | `crossref-doi-metadata-resolver` | CrossRef REST API, DOI Org | Resolves raw citations and unverified references into verified BibTeX entries and metadata. |
| **P1** | `latex-paper-authoring` | LaTeX, BibTeX, Overleaf API, KaTeX | Generates publication-ready academic papers (IEEE, ACM, NeurIPS formats) with verified equations and bibliography. |

---

#### 🏗️ DOMAIN 2: Technical Architecture Evaluation & Spike Prototyping
*Evaluating rival technologies, running feasibility spikes, and authoring authoritative decision records.*

| Priority | Target Skill Name | Primary APIs / Tools | Target Research Capability |
| :---: | :--- | :--- | :--- |
| **P0** | `technology-comparison-matrix` | Multi-criteria Decision Analysis (MCDA) | Evaluates competing technologies (e.g. 5 vector databases or 4 message brokers) across latency, licensing, community, and DX. |
| **P0** | `architecture-spike-prototyper` | Rapid Prototyping, Throwaway Spikes | Implements minimal, high-risk hypothesis testing code to validate third-party library claims before architectural commitment. |
| **P1** | `rfc-adr-technical-writing` | RFC 2119, ADR Templates (MADR, Nygard) | Authors persuasive Requests for Comments (RFC) and Architecture Decision Records with explicit trade-off analyses. |
| **P1** | `api-reverse-engineering-har` | HAR analyzers, mitmproxy, OpenAPI diff | Reverse engineers undocumented REST/GraphQL endpoints from network captures to produce OpenAPI 3.1 specs. |

---

#### 📊 DOMAIN 3: Market Intelligence, Competitive Teardowns & SEC Filings
*Empowering agents to analyze competitors, business models, and public financial disclosures.*

| Priority | Target Skill Name | Primary APIs / Tools | Target Research Capability |
| :---: | :--- | :--- | :--- |
| **P0** | `competitive-product-teardown` | Product Hunt, G2, Capterra, Playwright | Dissects competitor products: feature matrices, UX flows, onboarding frictions, pricing tiers, and API limitations. |
| **P0** | `sec-edgar-financial-analysis` | SEC EDGAR API, 10-K, 10-Q, 8-K filings | Extracts revenue breakdowns, risk factors, R&D spend, and executive commentary directly from official SEC filings. |
| **P1** | `saas-pricing-strategy-research` | Scraping, Tier Modeling, Value Metrics | Analyzes SaaS pricing structures (seat-based, usage-based, hybrid credits) to recommend optimal monetization. |
| **P1** | `industry-trend-synthesis` | Gartner/Forrester frameworks, Tech Radar | Maps emerging tech trends, adoption curves, and hype cycle positioning for executive decision makers. |

---

#### ⚖️ DOMAIN 4: Patents, Intellectual Property & Prior Art
*Analyzing the patent landscape to ensure freedom to operate and uncover prior art.*

| Priority | Target Skill Name | Primary APIs / Tools | Target Research Capability |
| :---: | :--- | :--- | :--- |
| **P0** | `patent-prior-art-search` | Google Patents API, USPTO, EPO Espacenet | Searches global patent databases using CPC/IPC classifications to detect prior art and evaluate novelty. |
| **P1** | `patent-claims-dissection` | Legal claim parsers, Independent Claims | Breaks down independent and dependent patent claims into element-by-element limitation charts. |
| **P1** | `freedom-to-operate-audit` | FTO Frameworks, Infringement Matrix | Maps a product's technical architecture against existing patent claims to identify infringement risks. |
| **P2** | `trademark-brand-clearance` | USPTO TESS, WIPO Global Brand Database | Screens software project names, trademarks, and logos across trademark registers before public branding. |

---

#### 🔍 DOMAIN 5: Open-Source Ecosystem Surveying & Supply-Chain Health
*Evaluating open-source dependencies before introducing them into production.*

| Priority | Target Skill Name | Primary APIs / Tools | Target Research Capability |
| :---: | :--- | :--- | :--- |
| **P0** | `github-ecosystem-analyzer` | GitHub GraphQL API, Git velocity | Analyzes repo health: commit frequency, PR merge turnaround, issue triage latency, and maintainer bus factor. |
| **P0** | `oss-license-compliance-audit` | SPDX, FOSSA, Licensee | Scans dependency trees for viral copyleft licenses (GPL/AGPL) that could compromise proprietary IP. |
| **P1** | `package-supply-chain-auditor` | OpenSSF Scorecard, Deps.dev, PyPI/npm | Evaluates dependency hygiene: binary artifacts, pinned dependencies, branch protection, and vulnerability history. |
| **P1** | `lib-rs-crates-benchmarking` | Lib.rs, Crates.io, npm trends | Compares language-specific libraries (e.g. serde vs postcard, tokio vs smol) on performance and adoption. |

---

#### 🧪 DOMAIN 6: Empirical Methodology, Experiment Design & Fact-Checking
*Ensuring that research conclusions are statistically sound, reproducible, and free from hallucinations.*

| Priority | Target Skill Name | Primary APIs / Tools | Target Research Capability |
| :---: | :--- | :--- | :--- |
| **P0** | `ab-testing-experiment-design` | Sample size calculators, Power analysis | Designs statistically sound A/B tests: minimum detectable effect (MDE), sample sizing, and multi-armed bandits. |
| **P0** | `fact-checking-hallucination-filter` | Claim extraction, Cross-verification | Breaks text into atomic factual claims, cross-references each claim against primary sources, and flags discrepancies. |
| **P1** | `exploratory-data-analysis-eda` | SciPy, Statsmodels, DuckDB, Polars | Automatically identifies outliers, distribution skewness, multicollinearity, and statistically significant correlations. |
| **P1** | `whitepaper-executive-briefing` | Pyramid Principle (Minto), Synthesis | Synthesizes 50+ pages of dense findings into a 2-page decision brief using the Situation-Complication-Resolution framework. |

---

### 3. Quantitative Impact on Research Capabilities

Integrating these 24 research skills into SkillForge expands your research intelligence dramatically:

```text
RESEARCH CAPABILITY PROJECTION:
Current System:  [████░░░░░░░░░░░░░░░░] 20% (Academic literature lookups only)
With Domain 1-3: [████████████░░░░░░░░] 60% (Academic + Architecture + Market)
With All 6:      [████████████████████] 98% (Complete end-to-end research powerhouse)
```

---

### 4. Implementation Priority: The Immediate "Top 6" Research Pack

If you want to start acquiring research skills right away, these are the **6 most impactful skills** to add first:

1. **`technology-comparison-matrix`**: Instantly evaluate competing libraries, frameworks, or databases with clear scoring rubrics.
2. **`semantic-scholar-citation-graph`**: Trace which papers cite each other to find the real seminal breakthroughs.
3. **`fact-checking-hallucination-filter`**: Protect agent reasoning by cross-verifying generated claims against primary sources.
4. **`github-ecosystem-analyzer`**: Inspect any open-source repo's velocity, maintainer activity, and risk factors before adopting it.
5. **`competitive-product-teardown`**: Map competitor products, feature gaps, and pricing models automatically.
6. **`systematic-literature-review-prisma`**: Turn chaotic web searching into a rigorous, academic-grade review process.

---
*Report saved to `reports/RESEARCH_SKILLS_EXPANSION_REPORT.md`.*
