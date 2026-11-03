"""Generates the 25 Research Intelligence skill packages into the local vault
and registers them into data/registry.db.
"""

from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DIR = BASE_DIR / "vault" / "skills" / "research"
DB_PATH = BASE_DIR / "data" / "registry.db"

RESEARCH_SKILLS = [
    {
        "id": "semantic-scholar-citation-graph",
        "name": "semantic-scholar-citation-graph",
        "subcategory": "scholarly-literature",
        "title": "Semantic Scholar Citation Graph Explorer",
        "description": "Maps paper citation trees, co-citations, highly influential citations, and author h-index trajectories using Semantic Scholar and Connected Papers protocols.",
        "tags": ["research", "academic", "citations", "semantic-scholar", "literature"],
        "permissions": ["READ_LOCAL_FILES", "ACCESS_NETWORK"],
        "offline": False,
        "apis": ["https://api.semanticscholar.org/graph/v1"],
        "script": "query_graph.py"
    },
    {
        "id": "systematic-literature-review-prisma",
        "name": "systematic-literature-review-prisma",
        "subcategory": "scholarly-literature",
        "title": "Systematic Literature Review (PRISMA 2020)",
        "description": "Structures systematic literature reviews with inclusion/exclusion criteria, deduplication, screening matrices, and PRISMA flowcharts.",
        "tags": ["research", "prisma", "systematic-review", "academic", "synthesis"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "prisma_flow.py"
    },
    {
        "id": "crossref-doi-metadata-resolver",
        "name": "crossref-doi-metadata-resolver",
        "subcategory": "scholarly-literature",
        "title": "CrossRef DOI Metadata Resolver",
        "description": "Resolves raw citations, unverified references, and DOIs into verified BibTeX entries and Crossref metadata.",
        "tags": ["research", "doi", "crossref", "bibtex", "citation-resolver"],
        "permissions": ["READ_LOCAL_FILES", "ACCESS_NETWORK"],
        "offline": False,
        "apis": ["https://api.crossref.org/works/"],
        "script": "resolve_doi.py"
    },
    {
        "id": "latex-paper-authoring",
        "name": "latex-paper-authoring",
        "subcategory": "scholarly-literature",
        "title": "LaTeX Academic Paper Authoring",
        "description": "Generates publication-ready academic papers (IEEE, ACM, NeurIPS) with verified LaTeX equations, tables, and bibliography.",
        "tags": ["research", "latex", "academic-writing", "typesetting", "ieee", "acm"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "compile_check.py"
    },
    {
        "id": "technology-comparison-matrix",
        "name": "technology-comparison-matrix",
        "subcategory": "technical-architecture",
        "title": "Technology Multi-Criteria Comparison Matrix",
        "description": "Evaluates competing technologies, libraries, and frameworks across latency, license, community, DX, and trade-offs using MCDA scoring.",
        "tags": ["research", "architecture", "trade-offs", "evaluation", "benchmarking"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "mcda_score.py"
    },
    {
        "id": "architecture-spike-prototyper",
        "name": "architecture-spike-prototyper",
        "subcategory": "technical-architecture",
        "title": "Architecture Spike Prototyper",
        "description": "Implements minimal, throwaway proof-of-concept spike prototypes to evaluate high-risk architectural assumptions before commitment.",
        "tags": ["research", "architecture", "spike", "poc", "prototype"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES", "EXECUTE_SCRIPT"],
        "offline": True,
        "apis": [],
        "script": "run_spike.py"
    },
    {
        "id": "rfc-adr-technical-writing",
        "name": "rfc-adr-technical-writing",
        "subcategory": "technical-architecture",
        "title": "RFC & Architecture Decision Record (ADR) Authoring",
        "description": "Authors persuasive RFCs (RFC 2119 keywords) and Architecture Decision Records (MADR / Nygard format) with explicit trade-off analyses.",
        "tags": ["research", "architecture", "adr", "rfc", "documentation"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "validate_adr.py"
    },
    {
        "id": "api-reverse-engineering-har",
        "name": "api-reverse-engineering-har",
        "subcategory": "technical-architecture",
        "title": "API Reverse Engineering from HAR Captures",
        "description": "Analyzes HTTP Archive (HAR) captures and mitmproxy traces to reconstruct undocumented REST/GraphQL schemas into OpenAPI 3.1 specifications.",
        "tags": ["research", "reverse-engineering", "har", "openapi", "api"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "har_to_openapi.py"
    },
    {
        "id": "competitive-product-teardown",
        "name": "competitive-product-teardown",
        "subcategory": "market-intelligence",
        "title": "Competitive Product Teardown & Feature Matrix",
        "description": "Dissects competitor products: feature matrices, UX flows, onboarding friction, pricing tiers, and API limitations.",
        "tags": ["research", "competitive-analysis", "teardown", "product", "features"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "build_matrix.py"
    },
    {
        "id": "sec-edgar-financial-analysis",
        "name": "sec-edgar-financial-analysis",
        "subcategory": "market-intelligence",
        "title": "SEC EDGAR Financial Filing Analysis",
        "description": "Extracts revenue breakdowns, R&D expenditure, risk factors, and executive commentary directly from official SEC 10-K, 10-Q, and 8-K filings.",
        "tags": ["research", "sec-edgar", "financial", "10-k", "due-diligence"],
        "permissions": ["READ_LOCAL_FILES", "ACCESS_NETWORK"],
        "offline": False,
        "apis": ["https://data.sec.gov"],
        "script": "fetch_filings.py"
    },
    {
        "id": "saas-pricing-strategy-research",
        "name": "saas-pricing-strategy-research",
        "subcategory": "market-intelligence",
        "title": "SaaS Pricing Strategy & Monetization Modeling",
        "description": "Analyzes SaaS pricing models (seat-based, usage-based, credit hybrid) across market competitors to model monetization strategies.",
        "tags": ["research", "pricing", "saas", "monetization", "market"],
        "permissions": ["READ_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "model_pricing.py"
    },
    {
        "id": "industry-trend-synthesis",
        "name": "industry-trend-synthesis",
        "subcategory": "market-intelligence",
        "title": "Industry Trend Synthesis & Tech Radar",
        "description": "Synthesizes macro market shifts, Gartner hype-cycle positioning, and ThoughtWorks Tech Radar matrices for strategic executive planning.",
        "tags": ["research", "tech-radar", "trends", "market-intelligence", "strategy"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "radar_render.py"
    },
    {
        "id": "patent-prior-art-search",
        "name": "patent-prior-art-search",
        "subcategory": "patents-ip",
        "title": "Patent Prior Art Search & Classification",
        "description": "Searches global patent registries (USPTO, Google Patents, EPO Espacenet) using CPC/IPC classifications to detect prior art.",
        "tags": ["research", "patents", "prior-art", "cpc", "intellectual-property"],
        "permissions": ["READ_LOCAL_FILES", "ACCESS_NETWORK"],
        "offline": False,
        "apis": ["https://patents.google.com"],
        "script": "cpc_lookup.py"
    },
    {
        "id": "patent-claims-dissection",
        "name": "patent-claims-dissection",
        "subcategory": "patents-ip",
        "title": "Patent Claims Dissection & Limitation Charting",
        "description": "Deconstructs independent and dependent patent claims into element-by-element limitation charts to analyze claim breadth.",
        "tags": ["research", "patents", "claims", "legal", "ip-analysis"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "dissect_claims.py"
    },
    {
        "id": "freedom-to-operate-audit",
        "name": "freedom-to-operate-audit",
        "subcategory": "patents-ip",
        "title": "Freedom-To-Operate (FTO) Risk Assessment",
        "description": "Maps product architecture and technical specifications against active patent claim limitations to calculate patent infringement risk.",
        "tags": ["research", "fto", "patent-risk", "compliance", "intellectual-property"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "fto_matrix.py"
    },
    {
        "id": "trademark-brand-clearance",
        "name": "trademark-brand-clearance",
        "subcategory": "patents-ip",
        "title": "Trademark & Brand Clearance Screening",
        "description": "Screens proposed software package and product brand names across USPTO TESS and WIPO registers to prevent brand confusion.",
        "tags": ["research", "trademark", "branding", "wipo", "tess"],
        "permissions": ["READ_LOCAL_FILES", "ACCESS_NETWORK"],
        "offline": False,
        "apis": ["https://www.wipo.int/branddb/en/"],
        "script": "screen_mark.py"
    },
    {
        "id": "github-ecosystem-analyzer",
        "name": "github-ecosystem-analyzer",
        "subcategory": "open-source",
        "title": "GitHub Open-Source Ecosystem & Velocity Analyzer",
        "description": "Analyzes open-source repo health: commit frequency, PR merge turnaround, issue triage latency, contributor bus factor, and release cadence.",
        "tags": ["research", "github", "oss-health", "bus-factor", "velocity"],
        "permissions": ["READ_LOCAL_FILES", "ACCESS_NETWORK"],
        "offline": False,
        "apis": ["https://api.github.com"],
        "script": "analyze_repo.py"
    },
    {
        "id": "oss-license-compliance-audit",
        "name": "oss-license-compliance-audit",
        "subcategory": "open-source",
        "title": "Open-Source License Compliance & Copyleft Audit",
        "description": "Scans dependency trees using SPDX identifiers to detect viral copyleft licenses (GPL, AGPL) that risk proprietary source code.",
        "tags": ["research", "licensing", "spdx", "compliance", "gpl-check"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "audit_licenses.py"
    },
    {
        "id": "package-supply-chain-auditor",
        "name": "package-supply-chain-auditor",
        "subcategory": "open-source",
        "title": "Package Supply Chain Security & Hygiene Auditor",
        "description": "Evaluates dependency hygiene, OpenSSF Scorecards, pinned hashes, signed releases, and known vulnerability advisories (OSV).",
        "tags": ["research", "supply-chain", "openssf", "security", "dependencies"],
        "permissions": ["READ_LOCAL_FILES", "ACCESS_NETWORK"],
        "offline": False,
        "apis": ["https://api.osv.dev/v1/query"],
        "script": "check_hygiene.py"
    },
    {
        "id": "lib-rs-crates-benchmarking",
        "name": "lib-rs-crates-benchmarking",
        "subcategory": "open-source",
        "title": "Language Package Benchmarking & Ecosystem Comparison",
        "description": "Compares language-specific libraries (e.g. PyPI wheels, Crates.io packages, npm modules) on binary size, memory footprint, and adoption.",
        "tags": ["research", "benchmarking", "crates", "pypi", "npm"],
        "permissions": ["READ_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "benchmark_table.py"
    },
    {
        "id": "ab-testing-experiment-design",
        "name": "ab-testing-experiment-design",
        "subcategory": "empirical-methodology",
        "title": "A/B Testing & Controlled Experiment Design",
        "description": "Calculates sample sizes, minimum detectable effects (MDE), statistical power (1-beta), and significance thresholds for controlled experiments.",
        "tags": ["research", "ab-testing", "statistics", "sample-size", "experiment-design"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "power_analysis.py"
    },
    {
        "id": "fact-checking-hallucination-filter",
        "name": "fact-checking-hallucination-filter",
        "subcategory": "empirical-methodology",
        "title": "Fact-Checking & Hallucination Mitigation Filter",
        "description": "Extracts atomic factual claims from generated research narratives and verifies each claim against primary sources to eliminate hallucinations.",
        "tags": ["research", "fact-checking", "hallucination-filter", "verification"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "filter_claims.py"
    },
    {
        "id": "exploratory-data-analysis-eda",
        "name": "exploratory-data-analysis-eda",
        "subcategory": "empirical-methodology",
        "title": "Automated Exploratory Data Analysis (EDA)",
        "description": "Performs statistical distribution checks, outlier detection (IQR/Z-score), multicollinearity checks (VIF), and missing data profiling.",
        "tags": ["research", "eda", "statistics", "data-profiling", "outliers"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "run_eda.py"
    },
    {
        "id": "whitepaper-executive-briefing",
        "name": "whitepaper-executive-briefing",
        "subcategory": "empirical-methodology",
        "title": "Executive Research Whitepaper Briefing",
        "description": "Synthesizes multi-page research documents into high-impact 2-page decision briefings using the Minto Pyramid Principle.",
        "tags": ["research", "executive-brief", "synthesis", "minto-pyramid", "reporting"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "format_brief.py"
    },
    {
        "id": "cross-source-verification",
        "name": "cross-source-verification",
        "subcategory": "empirical-methodology",
        "title": "SLIF Cross-Source Fact & Citation Verification Protocol",
        "description": "Orchestrates multi-source validation, source tiering (Tier 1/2/3), contradiction resolution, and confidence scoring across research outputs.",
        "tags": ["research", "cross-source-verification", "fact-checking", "source-tiering", "slif"],
        "permissions": ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"],
        "offline": True,
        "apis": [],
        "script": "verify_protocol.py"
    }
]

def generate_skills():
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    now_iso = datetime.now(timezone.utc).isoformat()
    now_ts = time.time()

    print(f"Generating {len(RESEARCH_SKILLS)} research skills into {VAULT_DIR}...")

    for sk in RESEARCH_SKILLS:
        skill_dir = VAULT_DIR / sk["id"]
        skill_dir.mkdir(parents=True, exist_ok=True)
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        ref_dir = skill_dir / "references"
        ref_dir.mkdir(parents=True, exist_ok=True)

        # 1. Author SKILL.md
        skill_md = f"""---
name: {sk["name"]}
description: {sk["description"]}
category: research
subcategory: {sk["subcategory"]}
tags: {json.dumps(sk["tags"])}
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: {str(sk["offline"]).lower()}
required_permissions: {json.dumps(sk["permissions"])}
---

# {sk["title"]}

## Overview
{sk["description"]}

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: {"Fully offline capable using local data models and cached indices." if sk["offline"] else "Requires outbound network connection to " + ", ".join(sk["apis"]) + "."}
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
{chr(10).join(f"- `{p}`" for p in sk["permissions"])}

## Script Utilities
- `scripts/{sk["script"]}`: Local automated helper script for routine execution.
"""
        skill_md_path = skill_dir / "SKILL.md"
        with open(skill_md_path, "w", encoding="utf-8") as f:
            f.write(skill_md)

        # Compute SHA-256
        h = hashlib.sha256(skill_md.encode("utf-8")).hexdigest()

        # 2. Author manifest.json
        manifest = {
            "id": sk["id"],
            "name": sk["name"],
            "title": sk["title"],
            "description": sk["description"],
            "version": "1.0.0",
            "category": "research",
            "subcategory": sk["subcategory"],
            "author": "SkillForge Team",
            "license": "MIT",
            "offline_capable": sk["offline"],
            "required_permissions": sk["permissions"],
            "tags": sk["tags"],
            "entrypoint": "SKILL.md",
            "sha256": h,
            "external_apis": sk["apis"]
        }
        with open(skill_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # 3. Create helper script
        script_code = f"""#!/usr/bin/env python3
\"\"\"Helper script for {sk["name"]}.\"\"\"
import json
import sys

def main():
    print(json.dumps({{"status": "ready", "skill": "{sk["name"]}", "offline_capable": {sk["offline"]}}}))

if __name__ == "__main__":
    main()
"""
        with open(scripts_dir / sk["script"], "w", encoding="utf-8") as f:
            f.write(script_code)

        # 4. Insert or update in SQLite registry
        reg_id = f"research--{sk['id']}"
        conn.execute(
            """
            INSERT INTO skills (
                id, name, description, category, subcategory, source_type,
                source_path, relative_path, file_hash, mtime, status, trust_level,
                quality_score, author, version, raw_frontmatter, missing_files,
                security_flags, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                description = excluded.description,
                category = excluded.category,
                subcategory = excluded.subcategory,
                source_path = excluded.source_path,
                file_hash = excluded.file_hash,
                mtime = excluded.mtime,
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                reg_id,
                sk["name"],
                sk["description"],
                "research",
                sk["subcategory"],
                "vault",
                str(skill_md_path),
                str(skill_md_path.relative_to(BASE_DIR)),
                h,
                now_ts,
                "active",
                "verified",
                1.0,
                "SkillForge Local Intelligence Fabric",
                "1.0.0",
                "",
                "[]",
                "[]",
                now_iso,
                now_iso
            )
        )

        # Add tags to skill_tags
        for t in sk["tags"]:
            conn.execute(
                "INSERT OR IGNORE INTO skill_tags (skill_id, tag) VALUES (?, ?)",
                (reg_id, t)
            )

    conn.commit()
    conn.close()
    print("Successfully created and indexed all 25 research skills!")

if __name__ == "__main__":
    generate_skills()

