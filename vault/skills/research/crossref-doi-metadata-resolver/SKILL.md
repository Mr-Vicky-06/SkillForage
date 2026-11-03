---
name: crossref-doi-metadata-resolver
description: Resolves raw citations, unverified references, and DOIs into verified BibTeX entries and Crossref metadata.
category: research
subcategory: scholarly-literature
tags: ["research", "doi", "crossref", "bibtex", "citation-resolver"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: false
required_permissions: ["READ_LOCAL_FILES", "ACCESS_NETWORK"]
---

# CrossRef DOI Metadata Resolver

## Overview
Resolves raw citations, unverified references, and DOIs into verified BibTeX entries and Crossref metadata.

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Requires outbound network connection to https://api.crossref.org/works/.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`
- `ACCESS_NETWORK`

## Script Utilities
- `scripts/resolve_doi.py`: Local automated helper script for routine execution.
