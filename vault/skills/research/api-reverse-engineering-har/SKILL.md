---
name: api-reverse-engineering-har
description: Analyzes HTTP Archive (HAR) captures and mitmproxy traces to reconstruct undocumented REST/GraphQL schemas into OpenAPI 3.1 specifications.
category: research
subcategory: technical-architecture
tags: ["research", "reverse-engineering", "har", "openapi", "api"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: true
required_permissions: ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"]
---

# API Reverse Engineering from HAR Captures

## Overview
Analyzes HTTP Archive (HAR) captures and mitmproxy traces to reconstruct undocumented REST/GraphQL schemas into OpenAPI 3.1 specifications.

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Fully offline capable using local data models and cached indices.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`
- `WRITE_LOCAL_FILES`

## Script Utilities
- `scripts/har_to_openapi.py`: Local automated helper script for routine execution.
