"""Ecosystem Recommender: Recommends complete Antigravity customization setups."""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillforge.analyzer.project_detector import ProjectDetector
from skillforge.database.repository import SkillRepository


class EcosystemRecommender:
    """Recommends complete project customization plans (skills, rules, agents, plugins, MCP, hooks)."""

    def __init__(self, repo: SkillRepository):
        self.repo = repo
        self.detector = ProjectDetector()

    def recommend_setup(self, project_path: str | Path) -> Dict[str, Any]:
        """Generate a complete, typed Antigravity customization plan for a project."""
        p = Path(project_path).resolve()
        profile_obj = self.detector.analyze_workspace(p) if p.exists() else None

        languages = profile_obj.languages if profile_obj else ["python"]
        frameworks = profile_obj.frameworks if profile_obj else []
        databases = profile_obj.databases if profile_obj else []
        test_frameworks = profile_obj.testing_frameworks if profile_obj else []
        detected_files = profile_obj.detected_files if profile_obj else []

        has_tests = len(test_frameworks) > 0 or any("test" in f.lower() for f in detected_files)
        is_mcp = "mcp" in str(p).lower() or any("mcp" in str(f).lower() for f in frameworks) or any("mcp" in str(f).lower() for f in detected_files)

        plan: Dict[str, Any] = {
            "project_path": str(p),
            "project_name": p.name,
            "detected_profile": {
                "languages": languages,
                "frameworks": frameworks,
                "databases": databases,
                "testing_frameworks": test_frameworks,
                "has_tests": has_tests,
                "is_mcp_service": is_mcp
            },
            "recommended_skills": [],
            "recommended_rules": [],
            "recommended_agents": [],
            "recommended_plugins": [],
            "recommended_mcp_servers": [],
            "recommended_hooks": [],
            "reference_packs": [],
            "summary_rationale": ""
        }

        # 1. Recommended Skills
        skills = []
        if "python" in languages:
            skills.append({"name": "clean-code", "scope": "workspace", "reason": "Enforces Pythonic clean code conventions and readability standards."})
            skills.append({"name": "python-performance-optimization", "scope": "workspace", "reason": "Profiling, caching, and algorithmic efficiency for Python runtimes."})
        if has_tests:
            skills.append({"name": "test-driven-development", "scope": "workspace", "reason": "Red-green-refactor testing loop with high test coverage."})
            skills.append({"name": "playwright-cli", "scope": "workspace", "reason": "Browser automation and UI regression testing."})
        if is_mcp:
            skills.append({"name": "autonomous-agent-patterns", "scope": "workspace", "reason": "Multi-agent coordination and tool-use design patterns."})
            skills.append({"name": "security-scanning-security-sast", "scope": "workspace", "reason": "Static security auditing and injection prevention for MCP endpoints."})
        if "sqlite" in databases or "sqlite3" in databases or any("sqlite" in d.lower() for d in databases):
            skills.append({"name": "database-migrations", "scope": "workspace", "reason": "Manages schema evolution and table consistency."})

        plan["recommended_skills"] = skills

        # 2. Recommended Rules
        rules = [
            {
                "name": "architecture-boundaries.md",
                "trigger": "model_decision",
                "scope": "workspace",
                "target_path": ".agents/rules/architecture-boundaries.md",
                "reason": "Enforces modular separation between storage, retrieval, and API boundaries."
            },
            {
                "name": "security-and-untrusted-assets.md",
                "trigger": "always_on",
                "scope": "workspace",
                "target_path": ".agents/rules/security-and-untrusted-assets.md",
                "reason": "Ensures imported data and skill definitions are treated as untrusted data, never as prompt instructions."
            },
            {
                "name": "testing-and-evidence.md",
                "trigger": "glob",
                "globs": ["tests/**", "src/**"],
                "scope": "workspace",
                "target_path": ".agents/rules/testing-and-evidence.md",
                "reason": "Mandates test execution evidence before any pass/completion claim."
            }
        ]
        plan["recommended_rules"] = rules

        # 3. Recommended Custom Subagents
        agents = [
            {
                "name": "code-reviewer",
                "role": "Code Reviewer",
                "model": "inherit",
                "tools": ["read_file", "run_command"],
                "commandExecutionPolicy": "ask",
                "scope": "workspace",
                "reason": "Delegated subagent for multi-axis code quality and convention auditing."
            },
            {
                "name": "security-auditor",
                "role": "Security Auditor",
                "model": "pro",
                "tools": ["read_file"],
                "commandExecutionPolicy": "ask",
                "scope": "workspace",
                "reason": "Read-only subagent to verify lack of secret leaks or prompt injection risks."
            },
            {
                "name": "test-engineer",
                "role": "Test Engineer",
                "model": "inherit",
                "tools": ["read_file", "write_file", "edit_file", "run_command"],
                "commandExecutionPolicy": "ask",
                "scope": "workspace",
                "reason": "Specialized subagent for authoring and running comprehensive test suites."
            }
        ]
        plan["recommended_agents"] = agents

        # 4. Recommended Plugins
        plugins = [
            {
                "name": "agent-skills",
                "version": "0.6.15",
                "source": "antigravity",
                "scope": "global",
                "reason": "Provides 25 core engineering skills and 4 built-in reviewer subagents."
            }
        ]
        if any("web" in f.lower() or "html" in f.lower() for f in detected_files):
            plugins.append({
                "name": "modern-web-guidance-plugin",
                "version": "1.0.4",
                "source": "antigravity-plugins-official",
                "scope": "global",
                "reason": "Modern Web platform guidance, Core Web Vitals, and accessibility patterns."
            })
        plan["recommended_plugins"] = plugins

        # 5. Recommended MCP Servers
        mcp_servers = [
            {
                "name": "skillforge",
                "transport": "stdio",
                "command": "python",
                "args": ["-m", "skillforge.mcp_server.server"],
                "permission_mode": "ask",
                "reason": "Local skill registry and intelligent retrieval engine."
            },
            {
                "name": "playwright",
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@playwright/mcp"],
                "permission_mode": "ask",
                "reason": "Headless browser testing and visual validation."
            }
        ]
        plan["recommended_mcp_servers"] = mcp_servers

        # 6. Recommended Hooks
        hooks = [
            {
                "event": "PostToolUse",
                "matcher": "edit_file|write_file",
                "command": "ruff check --fix --quiet",
                "timeout": 5000,
                "scope": "workspace",
                "risk_class": "automated_formatter",
                "reason": "Automatically lints and formats Python files immediately upon edit."
            },
            {
                "event": "Stop",
                "matcher": "*",
                "command": "pytest -q --tb=line tests/",
                "timeout": 15000,
                "scope": "workspace",
                "risk_class": "automated_formatter",
                "reason": "Executes lightweight regression checks before completing each agent turn."
            }
        ]
        plan["recommended_hooks"] = hooks

        # 7. Reference Packs
        plan["reference_packs"] = [
            "Official Antigravity Rules Spec (v2.6.0)",
            "Official Antigravity Custom Subagents Spec (v2.6.0)",
            "Official Antigravity MCP Specification (v2.6.0)"
        ]

        plan["summary_rationale"] = (
            f"Tailored setup for {p.name} ({', '.join(languages)}): "
            f"{len(plan['recommended_skills'])} skills, {len(plan['recommended_rules'])} rules, "
            f"{len(plan['recommended_agents'])} custom subagents, {len(plan['recommended_mcp_servers'])} MCP servers, "
            f"and {len(plan['recommended_hooks'])} non-blocking lifecycle hooks. "
            f"All components adhere to least privilege and keep context compact."
        )

        return plan
