---
name: trademark-brand-clearance
description: Screens proposed software package and product brand names across USPTO TESS and WIPO registers to prevent brand confusion.
category: research
subcategory: patents-ip
tags: ["research", "trademark", "branding", "wipo", "tess"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: false
required_permissions: ["READ_LOCAL_FILES", "ACCESS_NETWORK"]
---

# Trademark & Brand Clearance Screening

## Overview
Screens proposed software package and product brand names across USPTO TESS and WIPO registers to prevent brand confusion.

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Requires outbound network connection to https://www.wipo.int/branddb/en/.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`
- `ACCESS_NETWORK`

## Script Utilities
- `scripts/screen_mark.py`: Local automated helper script for routine execution.
