---
name: rfc-adr-technical-writing
description: Authors persuasive RFCs (RFC 2119 keywords) and Architecture Decision Records (MADR / Nygard format) with explicit trade-off analyses.
category: research
subcategory: technical-architecture
tags: ["research", "architecture", "adr", "rfc", "documentation"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: true
required_permissions: ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"]
---

# RFC & Architecture Decision Record (ADR) Authoring

## Overview
Authors persuasive RFCs (RFC 2119 keywords) and Architecture Decision Records (MADR / Nygard format) with explicit trade-off analyses.

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
- `scripts/validate_adr.py`: Local automated helper script for routine execution.
