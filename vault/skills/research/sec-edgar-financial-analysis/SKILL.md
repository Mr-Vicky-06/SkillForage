---
name: sec-edgar-financial-analysis
description: Extracts revenue breakdowns, R&D expenditure, risk factors, and executive commentary directly from official SEC 10-K, 10-Q, and 8-K filings.
category: research
subcategory: market-intelligence
tags: ["research", "sec-edgar", "financial", "10-k", "due-diligence"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: false
required_permissions: ["READ_LOCAL_FILES", "ACCESS_NETWORK"]
---

# SEC EDGAR Financial Filing Analysis

## Overview
Extracts revenue breakdowns, R&D expenditure, risk factors, and executive commentary directly from official SEC 10-K, 10-Q, and 8-K filings.

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Requires outbound network connection to https://data.sec.gov.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`
- `ACCESS_NETWORK`

## Script Utilities
- `scripts/fetch_filings.py`: Local automated helper script for routine execution.
