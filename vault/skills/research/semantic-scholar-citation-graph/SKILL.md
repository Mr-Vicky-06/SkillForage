---
name: semantic-scholar-citation-graph
description: Maps paper citation trees, co-citations, highly influential citations, and author h-index trajectories using Semantic Scholar and Connected Papers protocols.
category: research
subcategory: scholarly-literature
tags: ["research", "academic", "citations", "semantic-scholar", "literature"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: false
required_permissions: ["READ_LOCAL_FILES", "ACCESS_NETWORK"]
---

# Semantic Scholar Citation Graph Explorer

## Overview
Maps paper citation trees, co-citations, highly influential citations, and author h-index trajectories using Semantic Scholar and Connected Papers protocols.

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Requires outbound network connection to https://api.semanticscholar.org/graph/v1.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`
- `ACCESS_NETWORK`

## Script Utilities
- `scripts/query_graph.py`: Local automated helper script for routine execution.
