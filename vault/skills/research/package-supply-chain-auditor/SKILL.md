---
name: package-supply-chain-auditor
description: Evaluates dependency hygiene, OpenSSF Scorecards, pinned hashes, signed releases, and known vulnerability advisories (OSV).
category: research
subcategory: open-source
tags: ["research", "supply-chain", "openssf", "security", "dependencies"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: false
required_permissions: ["READ_LOCAL_FILES", "ACCESS_NETWORK"]
---

# Package Supply Chain Security & Hygiene Auditor

## Overview
Evaluates dependency hygiene, OpenSSF Scorecards, pinned hashes, signed releases, and known vulnerability advisories (OSV).

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Requires outbound network connection to https://api.osv.dev/v1/query.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`
- `ACCESS_NETWORK`

## Script Utilities
- `scripts/check_hygiene.py`: Local automated helper script for routine execution.
