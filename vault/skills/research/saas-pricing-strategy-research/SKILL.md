---
name: saas-pricing-strategy-research
description: Analyzes SaaS pricing models (seat-based, usage-based, credit hybrid) across market competitors to model monetization strategies.
category: research
subcategory: market-intelligence
tags: ["research", "pricing", "saas", "monetization", "market"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: true
required_permissions: ["READ_LOCAL_FILES"]
---

# SaaS Pricing Strategy & Monetization Modeling

## Overview
Analyzes SaaS pricing models (seat-based, usage-based, credit hybrid) across market competitors to model monetization strategies.

## Execution Protocol
1. **Activation Verification:** Confirm explicit human approval (Token `SF-XXXX`) before loading instructions into working context.
2. **Context Intake:** Validate research query parameters and identify target primary sources.
3. **Execution Mode:**
   - Offline Capability: Fully offline capable using local data models and cached indices.
4. **Output Artifact:** Produce structured, citation-backed findings in pure Markdown (`.md`).
5. **Quality Gate:** Cross-reference extracted claims with `cross-source-verification` before concluding.

## Permissible Permissions
- `READ_LOCAL_FILES`

## Script Utilities
- `scripts/model_pricing.py`: Local automated helper script for routine execution.
