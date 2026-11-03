---
name: architecture-spike-prototyper
description: Implements minimal, throwaway proof-of-concept spike prototypes to evaluate high-risk architectural assumptions before commitment.
category: research
subcategory: technical-architecture
tags: ["research", "architecture", "spike", "poc", "prototype"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: true
required_permissions: ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES", "EXECUTE_SCRIPT"]
---

# Architecture Spike Prototyper

## Overview
Implements minimal, throwaway proof-of-concept spike prototypes to evaluate high-risk architectural assumptions before commitment.

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
- `EXECUTE_SCRIPT`

## Script Utilities
- `scripts/run_spike.py`: Local automated helper script for routine execution.
