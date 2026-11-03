---
name: github-ecosystem-analyzer
description: Analyzes open-source repo health: commit frequency, PR merge turnaround, issue triage latency, contributor bus factor, and release cadence.
category: research
subcategory: open-source
tags: ["research", "github", "oss-health", "bus-factor", "velocity"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: false
required_permissions: ["READ_LOCAL_FILES", "ACCESS_NETWORK"]
---

# GitHub Open-Source Ecosystem & Velocity Analyzer

## Overview
Analyzes open-source repo health: commit frequency, PR merge turnaround, issue triage latency, contributor bus factor, and release cadence.

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Requires outbound network connection to https://api.github.com.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`
- `ACCESS_NETWORK`

## Script Utilities
- `scripts/analyze_repo.py`: Local automated helper script for routine execution.
