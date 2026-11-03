"""Parsers for native Antigravity ecosystem primitives."""

from __future__ import annotations
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml


def compute_file_hash(path: str | Path) -> str:
    """Compute SHA-256 hash of a file."""
    p = Path(path)
    if not p.is_file():
        return ""
    hasher = hashlib.sha256()
    try:
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


class RuleParser:
    """Parses Antigravity rules and persistent workspace instructions."""

    VALID_TRIGGERS = {"always_on", "model_decision", "glob", "manual"}

    @classmethod
    def parse(cls, file_path: str | Path) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.is_file():
            return {"error": "File not found", "path": str(p)}

        content = p.read_text(encoding="utf-8", errors="replace")
        sha256 = compute_file_hash(p)
        name = p.stem

        # Check for YAML frontmatter
        trigger = "always_on"
        description = ""
        globs: List[str] = []
        is_instruction = False

        if p.name.upper() in ["AGENTS.MD", "GEMINI.MD"]:
            is_instruction = True
            description = f"Persistent workspace instruction ({p.name})"
            trigger = "always_on"
        elif content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                    trigger = fm.get("trigger", "model_decision")
                    description = fm.get("description", "")
                    raw_globs = fm.get("globs", "")
                    if isinstance(raw_globs, str) and raw_globs:
                        globs = [g.strip() for g in raw_globs.split(",") if g.strip()]
                    elif isinstance(raw_globs, list):
                        globs = [str(g).strip() for g in raw_globs]
                except Exception as e:
                    trigger = "broken_frontmatter"
                    description = f"YAML parse error: {e}"

        validation_state = "VERIFIED" if trigger in cls.VALID_TRIGGERS else "INVALID_TRIGGER"

        return {
            "name": name,
            "display_name": f"Rule: {name}",
            "description": description or f"Rule defined in {p.name}",
            "asset_type": "workspace_instruction" if is_instruction else "agent_rule",
            "trigger": trigger,
            "globs": globs,
            "content_hash": sha256,
            "source_path": str(p),
            "validation_state": validation_state,
            "compatibility_surfaces": ["antigravity_ide", "antigravity_app", "antigravity_cli"]
        }


class AgentParser:
    """Parses Antigravity custom agents and subagent profiles."""

    @classmethod
    def parse(cls, file_path: str | Path) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.is_file():
            return {"error": "File not found", "path": str(p)}

        content = p.read_text(encoding="utf-8", errors="replace")
        sha256 = compute_file_hash(p)
        name = p.stem if p.name != "agent.md" else p.parent.name

        description = ""
        tools: List[str] = []
        model = "inherit"
        main_agent = False
        subagent = True
        command_policy = "ask"
        skills: List[str] = []
        mcp_servers: List[str] = []

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                    name = fm.get("name", name)
                    description = fm.get("description", "")
                    tools = fm.get("tools", []) or []
                    model = fm.get("model", "inherit")
                    main_agent = fm.get("mainAgent", False)
                    subagent = fm.get("subagent", True)
                    command_policy = fm.get("commandExecutionPolicy", "ask")
                    skills = fm.get("skills", []) or []
                    mcp_servers = fm.get("mcpServers", []) or []
                except Exception as e:
                    description = f"Parse error: {e}"

        validation_state = "VERIFIED" if description else "UNVERIFIED"

        return {
            "name": name,
            "display_name": f"Agent: {name}",
            "description": description or f"Custom subagent profile for {name}",
            "asset_type": "custom_agent",
            "tools": tools,
            "model": model,
            "main_agent": main_agent,
            "subagent": subagent,
            "command_execution_policy": command_policy,
            "skills": skills,
            "mcp_servers": mcp_servers,
            "content_hash": sha256,
            "source_path": str(p),
            "validation_state": validation_state,
            "compatibility_surfaces": ["antigravity_ide", "antigravity_app"]
        }


class PluginParser:
    """Parses Antigravity plugin packages and component manifests."""

    @classmethod
    def parse(cls, plugin_dir: str | Path) -> Dict[str, Any]:
        d = Path(plugin_dir)
        if not d.is_dir():
            return {"error": "Plugin directory not found", "path": str(d)}

        manifest_path = d / "plugin.json"
        if not manifest_path.is_file():
            alt = d / ".antigravity-plugin" / "plugin.json"
            if alt.is_file():
                manifest_path = alt

        meta: Dict[str, Any] = {}
        if manifest_path.is_file():
            try:
                meta = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
            except Exception as e:
                meta = {"name": d.name, "description": f"Malformed plugin.json: {e}"}
        else:
            meta = {"name": d.name, "description": f"Unmanifested plugin directory {d.name}"}

        name = meta.get("name", d.name)
        version = meta.get("version", "1.0.0")
        description = meta.get("description", f"Antigravity plugin bundle {name}")
        license_spdx = meta.get("license", "Unknown")

        # Discover child components
        bundled_skills: List[str] = []
        skills_dir = d / "skills"
        if skills_dir.is_dir():
            for item in skills_dir.iterdir():
                if item.is_dir() and (item / "SKILL.md").is_file():
                    bundled_skills.append(item.name)

        bundled_agents: List[str] = []
        agents_dir = d / "agents"
        if agents_dir.is_dir():
            for item in agents_dir.iterdir():
                if item.is_file() and item.suffix == ".md":
                    bundled_agents.append(item.stem)
                elif item.is_dir() and (item / "agent.md").is_file():
                    bundled_agents.append(item.name)

        has_mcp = (d / "mcp_config.json").is_file()
        has_hooks = (d / "hooks.json").is_file()

        sha256 = compute_file_hash(manifest_path) if manifest_path.is_file() else ""

        return {
            "name": name,
            "display_name": f"Plugin: {name} (v{version})",
            "description": description,
            "asset_type": "plugin_bundle",
            "version": version,
            "license_spdx": license_spdx,
            "bundled_skills": bundled_skills,
            "bundled_agents": bundled_agents,
            "has_mcp": has_mcp,
            "has_hooks": has_hooks,
            "source_path": str(d),
            "manifest_path": str(manifest_path) if manifest_path.is_file() else "",
            "content_hash": sha256,
            "validation_state": "VERIFIED" if manifest_path.is_file() else "PARTIALLY_VERIFIED",
            "compatibility_surfaces": ["antigravity_ide", "antigravity_app", "antigravity_cli"]
        }


class HookParser:
    """Parses Antigravity lifecycle hooks configuration statically."""

    VALID_EVENTS = {"SessionStart", "PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"}
    HIGH_RISK_PATTERNS = [r"\brm\s+-rf\b", r"\bdel\s+/[sfq]\b", r"curl\s+.*\|\s*sh", r"powershell\s+.*-enc", r"Invoke-Expression", r"wget\s+.*\|\s*sh"]

    @classmethod
    def parse(cls, file_path: str | Path) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.is_file():
            return {"error": "Hooks config not found", "path": str(p)}

        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            return {"error": f"JSON parse error: {e}", "path": str(p)}

        sha256 = compute_file_hash(p)
        hooks_list = data.get("hooks", []) if isinstance(data, dict) else []
        parsed_hooks = []
        highest_risk = "safe_read"

        for h in hooks_list:
            event = h.get("event", "")
            matcher = h.get("matcher", "*")
            cmd = h.get("command", "")
            timeout = h.get("timeout", 10000)

            # Static risk analysis
            risk = "safe_read"
            for pat in cls.HIGH_RISK_PATTERNS:
                if re.search(pat, cmd, re.IGNORECASE):
                    risk = "high_risk_destructive"
                    highest_risk = "high_risk_destructive"
                    break

            if risk == "safe_read" and any(w in cmd.lower() for w in ["format", "lint", "prettier", "black", "ruff"]):
                risk = "automated_formatter"
                if highest_risk != "high_risk_destructive":
                    highest_risk = "automated_formatter"

            parsed_hooks.append({
                "event": event,
                "matcher": matcher,
                "command": cmd,
                "timeout": timeout,
                "risk_class": risk,
                "is_valid_event": event in cls.VALID_EVENTS
            })

        return {
            "name": p.parent.name + "_hooks",
            "display_name": f"Lifecycle Hooks ({p.parent.name})",
            "description": f"Antigravity lifecycle hooks bundle containing {len(parsed_hooks)} handlers",
            "asset_type": "lifecycle_hook",
            "hooks": parsed_hooks,
            "risk_class": highest_risk,
            "content_hash": sha256,
            "source_path": str(p),
            "safety_note": "Non-zero hook exit codes fail open per Antigravity specification. Do not rely on hooks as sole security control.",
            "validation_state": "VERIFIED" if all(h["is_valid_event"] for h in parsed_hooks) else "PARTIALLY_VERIFIED",
            "compatibility_surfaces": ["antigravity_ide", "antigravity_app", "antigravity_cli"]
        }


class MCPConfigParser:
    """Parses MCP server configuration files without exposing credentials."""

    @classmethod
    def parse(cls, file_path: str | Path) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.is_file():
            return {"error": "MCP config not found", "path": str(p)}

        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            return {"error": f"JSON parse error: {e}", "path": str(p)}

        sha256 = compute_file_hash(p)
        servers = data.get("mcpServers", {})
        parsed_servers = []

        for server_name, cfg in servers.items():
            transport = "stdio"
            server_url = cfg.get("serverUrl", "")
            if server_url:
                transport = "streamable_http"
            elif "httpUrl" in cfg:
                transport = "deprecated_httpUrl"

            command = cfg.get("command", "")
            args = cfg.get("args", [])
            env_keys = list(cfg.get("env", {}).keys())  # capture ONLY variable names, never values!

            parsed_servers.append({
                "server_name": server_name,
                "transport": transport,
                "command": command,
                "args_count": len(args),
                "configured_env_vars": env_keys,
                "is_remote": bool(server_url),
                "is_deprecated_transport": transport == "deprecated_httpUrl"
            })

        return {
            "name": p.parent.name + "_mcp_config",
            "display_name": f"MCP Config ({p.parent.name})",
            "description": f"MCP configuration exposing {len(parsed_servers)} servers",
            "asset_type": "mcp_server",
            "servers": parsed_servers,
            "content_hash": sha256,
            "source_path": str(p),
            "validation_state": "VERIFIED",
            "compatibility_surfaces": ["antigravity_ide", "antigravity_app", "antigravity_cli"]
        }


class ManifestParser:
    """Parses discovery manifests (skills.json, rules.json, agents.json, plugins.json)."""

    @classmethod
    def parse(cls, file_path: str | Path) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.is_file():
            return {"error": "Manifest not found", "path": str(p)}

        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            return {"error": f"JSON parse error: {e}", "path": str(p)}

        sha256 = compute_file_hash(p)
        paths = data.get("paths", [])
        return {
            "name": p.name,
            "display_name": f"Discovery Manifest: {p.name}",
            "description": f"Antigravity discovery manifest referencing {len(paths)} additional scan paths",
            "asset_type": "discovery_manifest",
            "paths": paths,
            "content_hash": sha256,
            "source_path": str(p),
            "validation_state": "VERIFIED",
            "compatibility_surfaces": ["antigravity_ide", "antigravity_app"]
        }


class WorkflowParser:
    """Parses legacy workflow files and flags retirement/migration status."""

    @classmethod
    def parse(cls, file_path: str | Path) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.is_file():
            return {"error": "Workflow file not found", "path": str(p)}

        sha256 = compute_file_hash(p)
        return {
            "name": p.stem,
            "display_name": f"Legacy Workflow: {p.stem}",
            "description": f"Deprecated single-file workflow. Retired on 19 October 2026. Needs migration to Agent Skill.",
            "asset_type": "legacy_workflow",
            "content_hash": sha256,
            "source_path": str(p),
            "status": "deprecated",
            "retirement_date": "2026-10-19",
            "migration_recommended": True,
            "validation_state": "RETIRED",
            "compatibility_surfaces": []
        }
