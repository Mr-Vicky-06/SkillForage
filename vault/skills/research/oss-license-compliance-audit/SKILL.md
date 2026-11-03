---
name: oss-license-compliance-audit
description: Scans dependency trees using SPDX identifiers to detect viral copyleft licenses (GPL, AGPL) that risk proprietary source code.
category: research
subcategory: open-source
tags: ["research", "licensing", "spdx", "compliance", "gpl-check"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: true
required_permissions: ["READ_LOCAL_FILES", "WRITE_LOCAL_FILES"]
---

# Open-Source License Compliance & Copyleft Audit

## Overview
Scans dependency trees using SPDX identifiers to detect viral copyleft licenses (GPL, AGPL) that risk proprietary source code.

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
- `scripts/audit_licenses.py`: Local automated helper script for routine execution.
