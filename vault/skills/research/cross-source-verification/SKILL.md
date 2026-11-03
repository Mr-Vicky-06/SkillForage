---
name: cross-source-verification
description: Orchestrates multi-source validation, source tiering (Tier 1/2/3), contradiction resolution, and confidence scoring across research outputs.
category: research
subcategory: empirical-methodology
tags: ["research", "cross-source-verification", "fact-checking", "source-tiering", "slif"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: true
required_permissions: ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"]
---

# SLIF Cross-Source Fact & Citation Verification Protocol

## Overview
Orchestrates multi-source validation, source tiering (Tier 1/2/3), contradiction resolution, and confidence scoring across research outputs.

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
- `scripts/verify_protocol.py`: Local automated helper script for routine execution.
