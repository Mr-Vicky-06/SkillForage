---
name: lib-rs-crates-benchmarking
description: Compares language-specific libraries (e.g. PyPI wheels, Crates.io packages, npm modules) on binary size, memory footprint, and adoption.
category: research
subcategory: open-source
tags: ["research", "benchmarking", "crates", "pypi", "npm"]
author: SkillForge Local Intelligence Fabric
version: 1.0.0
offline_capable: true
required_permissions: ["READ_LOCAL_FILES"]
---

# Language Package Benchmarking & Ecosystem Comparison

## Overview
Compares language-specific libraries (e.g. PyPI wheels, Crates.io packages, npm modules) on binary size, memory footprint, and adoption.

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
- `scripts/benchmark_table.py`: Local automated helper script for routine execution.
