---
name: patent-prior-art-search
description: Searches global patent registries (USPTO, Google Patents, EPO Espacenet) using CPC/IPC classifications to detect prior art.
category: research
subcategory: patents-ip
tags: ["research", "patents", "prior-art", "cpc", "intellectual-property"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: false
required_permissions: ["READ_LOCAL_FILES", "ACCESS_NETWORK"]
---

# Patent Prior Art Search & Classification

## Overview
Searches global patent registries (USPTO, Google Patents, EPO Espacenet) using CPC/IPC classifications to detect prior art.

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Requires outbound network connection to https://patents.google.com.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`
- `ACCESS_NETWORK`

## Script Utilities
- `scripts/cpc_lookup.py`: Local automated helper script for routine execution.
