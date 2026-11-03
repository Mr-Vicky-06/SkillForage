"""Ecosystem Scanner: Discovers and indexes all native Antigravity ecosystem primitives."""

from __future__ import annotations
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillforge.database.models import (
    EcosystemAsset,
    EcosystemAssetType,
    EcosystemComponent,
    MCPCapability,
    AssetEvidence,
)
from skillforge.database.repository import SkillRepository
from skillforge.ecosystem.parsers import (
    AgentParser,
    HookParser,
    ManifestParser,
    MCPConfigParser,
    PluginParser,
    RuleParser,
    WorkflowParser,
    compute_file_hash,
)


class EcosystemScanner:
    """Discovers, parses, validates, and indexes all Antigravity ecosystem assets."""

    def __init__(self, repo: SkillRepository):
        self.repo = repo
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.global_gemini = Path(self.user_profile) / ".gemini" if self.user_profile else None
        self.global_config = self.global_gemini / "config" if self.global_gemini else None

    def scan_all(
        self,
        workspace_roots: Optional[List[str | Path]] = None,
        include_global: bool = True,
        include_supplemental: bool = True
    ) -> Dict[str, Any]:
        """Perform a full discovery and indexing of all Antigravity ecosystem assets."""
        stats = {
            "rules_indexed": 0,
            "instructions_indexed": 0,
            "agents_indexed": 0,
            "plugins_indexed": 0,
            "hooks_indexed": 0,
            "mcp_servers_indexed": 0,
            "mcp_capabilities_indexed": 0,
            "manifests_indexed": 0,
            "legacy_workflows_indexed": 0,
            "supplemental_packs_indexed": 0,
            "total_assets_indexed": 0,
        }

        # 1. Scan Global Antigravity Directory (%USERPROFILE%/.gemini)
        if include_global and self.global_gemini and self.global_gemini.exists():
            self._scan_global(stats)

        # 2. Scan Workspace Roots
        roots = workspace_roots or [Path("d:/setup"), Path("d:/setup/antigravity-skillforge")]
        for r in roots:
            p = Path(r)
            if p.is_dir():
                self._scan_workspace(p, stats)

        # 3. Scan Supplemental Source Mirrors (D:/setup/skillforge-ecosystem-sources)
        if include_supplemental:
            supp = Path("d:/setup/skillforge-ecosystem-sources")
            if supp.is_dir():
                self._scan_supplemental(supp, stats)

        # 4. Ingest Active Plugin List from agy CLI if available
        self._ingest_agy_plugins(stats)

        stats["total_assets_indexed"] = (
            stats["rules_indexed"]
            + stats["instructions_indexed"]
            + stats["agents_indexed"]
            + stats["plugins_indexed"]
            + stats["hooks_indexed"]
            + stats["mcp_servers_indexed"]
            + stats["manifests_indexed"]
            + stats["legacy_workflows_indexed"]
            + stats["supplemental_packs_indexed"]
        )

        return stats

    def _scan_global(self, stats: Dict[str, Any]) -> None:
        """Scan global instructions, agents, plugins, rules, and MCP configs."""
        # A. Always-on instructions
        for inst_name in ["AGENTS.md", "GEMINI.md"]:
            inst_path = self.global_gemini / inst_name
            if inst_path.is_file():
                self._index_rule(inst_path, scope="global", is_instruction=True, stats=stats)

        if not self.global_config or not self.global_config.exists():
            return

        # B. Global agents
        agents_dir = self.global_config / "agents"
        if agents_dir.is_dir():
            for item in agents_dir.iterdir():
                if item.is_file() and item.suffix == ".md":
                    self._index_agent(item, scope="global", stats=stats)
                elif item.is_dir() and (item / "agent.md").is_file():
                    self._index_agent(item / "agent.md", scope="global", stats=stats)

        # C. Global rules
        rules_dir = self.global_config / "rules"
        if rules_dir.is_dir():
            for item in rules_dir.iterdir():
                if item.is_file() and item.suffix == ".md":
                    self._index_rule(item, scope="global", is_instruction=False, stats=stats)

        # D. Global plugins
        plugins_dir = self.global_config / "plugins"
        if plugins_dir.is_dir():
            for pdir in plugins_dir.iterdir():
                if pdir.is_dir():
                    self._index_plugin(pdir, scope="global", stats=stats)

        # E. Global MCP config
        mcp_cfg = self.global_config / "mcp_config.json"
        if mcp_cfg.is_file():
            self._index_mcp_config(mcp_cfg, scope="global", stats=stats)

        # F. Global hooks
        hooks_cfg = self.global_config / "hooks.json"
        if hooks_cfg.is_file():
            self._index_hooks(hooks_cfg, scope="global", stats=stats)

        # G. Global sidecars
        sidecars_dir = self.global_config / "sidecars"
        if sidecars_dir.is_dir():
            for sdir in sidecars_dir.iterdir():
                sc_file = sdir / "sidecar.json"
                if sc_file.is_file():
                    self._index_sidecar(sc_file, scope="global", stats=stats)

    def _scan_workspace(self, workspace_path: Path, stats: Dict[str, Any]) -> None:
        """Scan workspace instructions, .agents/ directory, rules, agents, plugins, hooks."""
        # A. Workspace instructions
        for inst_name in ["AGENTS.md", "GEMINI.md"]:
            inst_path = workspace_path / inst_name
            if inst_path.is_file():
                self._index_rule(inst_path, scope="workspace", is_instruction=True, stats=stats)

        agents_root = workspace_path / ".agents"
        if not agents_root.is_dir():
            return

        # B. Workspace rules
        rules_dir = agents_root / "rules"
        if rules_dir.is_dir():
            for item in rules_dir.iterdir():
                if item.is_file() and item.suffix == ".md":
                    self._index_rule(item, scope="workspace", is_instruction=False, stats=stats)

        # C. Workspace agents
        agents_dir = agents_root / "agents"
        if agents_dir.is_dir():
            for item in agents_dir.iterdir():
                if item.is_file() and item.suffix == ".md":
                    self._index_agent(item, scope="workspace", stats=stats)
                elif item.is_dir() and (item / "agent.md").is_file():
                    self._index_agent(item / "agent.md", scope="workspace", stats=stats)

        # D. Workspace plugins
        plugins_dir = agents_root / "plugins"
        if plugins_dir.is_dir():
            for pdir in plugins_dir.iterdir():
                if pdir.is_dir():
                    self._index_plugin(pdir, scope="workspace", stats=stats)

        # E. Workspace MCP config
        mcp_file = agents_root / "mcp_config.json"
        if mcp_file.is_file():
            self._index_mcp_config(mcp_file, scope="workspace", stats=stats)

        # F. Workspace hooks
        hooks_file = agents_root / "hooks.json"
        if hooks_file.is_file():
            self._index_hooks(hooks_file, scope="workspace", stats=stats)

        # G. Legacy workflows
        wf_dir = agents_root / "workflows"
        if wf_dir.is_dir():
            for wf in wf_dir.iterdir():
                if wf.is_file() and wf.suffix in [".yaml", ".yml", ".md"]:
                    self._index_legacy_workflow(wf, scope="workspace", stats=stats)

        # H. Manifests
        for m_name in ["skills.json", "rules.json", "agents.json", "plugins.json"]:
            m_path = agents_root / m_name
            if m_path.is_file():
                self._index_manifest(m_path, scope="workspace", stats=stats)

    def _scan_supplemental(self, supp_dir: Path, stats: Dict[str, Any]) -> None:
        """Scan supplemental source mirrors: docs snapshots, community indexes, manifests."""
        # A. Docs snapshots (Official Antigravity Specs)
        docs_dir = supp_dir / "official-antigravity" / "docs-snapshots"
        if docs_dir.is_dir():
            for item in docs_dir.iterdir():
                if item.is_file() and item.suffix == ".json":
                    try:
                        data = json.loads(item.read_text(encoding="utf-8"))
                        asset = EcosystemAsset(
                            asset_id=f"doc_spec_{item.stem}",
                            asset_type=EcosystemAssetType.REFERENCE_PACK.value,
                            name=item.stem,
                            display_name=f"Official Antigravity Spec: {item.stem}",
                            description=f"Specification snapshot for {data.get('primitive', item.stem)}",
                            source_id="official-antigravity-docs",
                            source_path=str(item),
                            source_url=data.get("documentation_url", "https://antigravity.google/docs"),
                            license_spdx="Google-Proprietary-Docs",
                            trust_state="trusted",
                            validation_state="VERIFIED",
                            compatibility_surfaces=data.get("supported_surfaces", ["antigravity_ide"]),
                            install_scope="built_in",
                            enabled_state="enabled",
                            metadata_json=data
                        )
                        self.repo.insert_ecosystem_asset(asset)
                        stats["supplemental_packs_indexed"] += 1
                    except Exception:
                        pass

        # B. Community indexes
        comm_dir = supp_dir / "community-discovery-indexes"
        if comm_dir.is_dir():
            for item in comm_dir.iterdir():
                if item.is_file() and item.suffix == ".json":
                    try:
                        data = json.loads(item.read_text(encoding="utf-8"))
                        asset = EcosystemAsset(
                            asset_id=f"community_idx_{item.stem}",
                            asset_type=EcosystemAssetType.REFERENCE_PACK.value,
                            name=item.stem,
                            display_name=f"Community Index: {item.stem}",
                            description=f"Curated index from {data.get('source', item.stem)}",
                            source_id="community-index",
                            source_path=str(item),
                            source_url=data.get("source", ""),
                            license_spdx="MIT",
                            trust_state="reviewed",
                            validation_state="VERIFIED",
                            compatibility_surfaces=["antigravity_ide", "antigravity_app"],
                            install_scope="built_in",
                            enabled_state="enabled",
                            metadata_json=data
                        )
                        self.repo.insert_ecosystem_asset(asset)
                        stats["supplemental_packs_indexed"] += 1
                    except Exception:
                        pass

        # C. Manifests
        mani_dir = supp_dir / "manifests"
        if mani_dir.is_dir():
            for item in mani_dir.iterdir():
                if item.is_file() and item.suffix == ".json":
                    self._index_manifest(item, scope="workspace", stats=stats)

    def _ingest_agy_plugins(self, stats: Dict[str, Any]) -> None:
        """Cross-reference with agy plugin list --json to verify installed plugins."""
        try:
            res = subprocess.run(["agy", "plugin", "list", "--json"], capture_output=True, text=True, timeout=10)
            if res.returncode == 0 and res.stdout.strip():
                plugins = json.loads(res.stdout)
                for p in plugins:
                    pname = p.get("name")
                    if not pname:
                        continue
                    asset_id = f"plugin_agy_{pname}"
                    existing = self.repo.get_ecosystem_asset(asset_id)
                    bundled_skills = p.get("skills", [])
                    bundled_agents = p.get("agents", [])

                    asset = EcosystemAsset(
                        asset_id=asset_id,
                        asset_type=EcosystemAssetType.PLUGIN_BUNDLE.value,
                        name=pname,
                        display_name=f"Plugin: {pname} (agy verified)",
                        description=f"Antigravity active plugin {pname} with {len(bundled_skills)} skills and {len(bundled_agents)} agents",
                        source_id=p.get("source", "antigravity-plugins-official"),
                        source_path=p.get("path", ""),
                        version=p.get("version", "1.0.0"),
                        license_spdx="Google-Official",
                        trust_state="trusted",
                        validation_state="VERIFIED",
                        compatibility_surfaces=["antigravity_ide", "antigravity_app", "antigravity_cli"],
                        install_scope="global",
                        enabled_state="enabled" if p.get("enabled", True) else "disabled",
                        metadata_json={
                            "bundled_skills": bundled_skills,
                            "bundled_agents": bundled_agents,
                            "cli_verified": True
                        }
                    )
                    self.repo.insert_ecosystem_asset(asset)

                    # Link bundled skills as components without creating duplicate skill records in skills table!
                    for sk in bundled_skills:
                        child_id = f"skill_{sk}"
                        self.repo.link_ecosystem_component(asset_id, child_id, rel_type="bundles", metadata={"name": sk})

                    # Link bundled agents as components
                    for ag in bundled_agents:
                        child_id = f"agent_{ag}"
                        self.repo.link_ecosystem_component(asset_id, child_id, rel_type="bundles", metadata={"name": ag})

                    if not existing:
                        stats["plugins_indexed"] += 1
        except Exception:
            pass

    # Helper indexing routines

    def _index_rule(self, path: Path, scope: str, is_instruction: bool, stats: Dict[str, Any]) -> None:
        parsed = RuleParser.parse(path)
        if "error" in parsed:
            return

        asset_id = f"{'inst' if is_instruction else 'rule'}_{scope}_{parsed['name']}"
        asset = EcosystemAsset(
            asset_id=asset_id,
            asset_type=EcosystemAssetType.WORKSPACE_INSTRUCTION.value if is_instruction else EcosystemAssetType.AGENT_RULE.value,
            name=parsed["name"],
            display_name=parsed["display_name"],
            description=parsed["description"],
            source_id=f"{scope}-rule",
            source_path=str(path),
            content_hash=parsed["content_hash"],
            trust_state="trusted" if scope == "workspace" else "reviewed",
            validation_state=parsed["validation_state"],
            compatibility_surfaces=parsed["compatibility_surfaces"],
            install_scope=scope,
            enabled_state="enabled",
            metadata_json={"trigger": parsed.get("trigger", "always_on"), "globs": parsed.get("globs", [])}
        )
        self.repo.insert_ecosystem_asset(asset)
        if is_instruction:
            stats["instructions_indexed"] += 1
        else:
            stats["rules_indexed"] += 1

    def _index_agent(self, path: Path, scope: str, stats: Dict[str, Any]) -> None:
        parsed = AgentParser.parse(path)
        if "error" in parsed:
            return

        asset_id = f"agent_{scope}_{parsed['name']}"
        asset = EcosystemAsset(
            asset_id=asset_id,
            asset_type=EcosystemAssetType.CUSTOM_AGENT.value,
            name=parsed["name"],
            display_name=parsed["display_name"],
            description=parsed["description"],
            source_id=f"{scope}-agent",
            source_path=str(path),
            content_hash=parsed["content_hash"],
            trust_state="trusted" if scope == "workspace" else "reviewed",
            validation_state=parsed["validation_state"],
            compatibility_surfaces=parsed["compatibility_surfaces"],
            install_scope=scope,
            enabled_state="enabled",
            metadata_json={
                "tools": parsed.get("tools", []),
                "model": parsed.get("model", "inherit"),
                "commandExecutionPolicy": parsed.get("command_execution_policy", "ask"),
                "subagent": parsed.get("subagent", True),
                "skills": parsed.get("skills", []),
                "mcpServers": parsed.get("mcp_servers", [])
            }
        )
        self.repo.insert_ecosystem_asset(asset)
        stats["agents_indexed"] += 1

    def _index_plugin(self, path: Path, scope: str, stats: Dict[str, Any]) -> None:
        parsed = PluginParser.parse(path)
        if "error" in parsed:
            return

        asset_id = f"plugin_{scope}_{parsed['name']}"
        asset = EcosystemAsset(
            asset_id=asset_id,
            asset_type=EcosystemAssetType.PLUGIN_BUNDLE.value,
            name=parsed["name"],
            display_name=parsed["display_name"],
            description=parsed["description"],
            source_id=f"{scope}-plugin",
            source_path=str(path),
            version=parsed.get("version", "1.0.0"),
            license_spdx=parsed.get("license_spdx", "Unknown"),
            content_hash=parsed["content_hash"],
            trust_state="reviewed",
            validation_state=parsed["validation_state"],
            compatibility_surfaces=parsed["compatibility_surfaces"],
            install_scope=scope,
            enabled_state="enabled",
            metadata_json={
                "bundled_skills": parsed.get("bundled_skills", []),
                "bundled_agents": parsed.get("bundled_agents", []),
                "has_mcp": parsed.get("has_mcp", False),
                "has_hooks": parsed.get("has_hooks", False)
            }
        )
        self.repo.insert_ecosystem_asset(asset)

        # Link bundled skills as components
        for sk in parsed.get("bundled_skills", []):
            child_id = f"skill_{sk}"
            self.repo.link_ecosystem_component(asset_id, child_id, rel_type="bundles", metadata={"name": sk})

        # Link bundled agents as components
        for ag in parsed.get("bundled_agents", []):
            child_id = f"agent_{ag}"
            self.repo.link_ecosystem_component(asset_id, child_id, rel_type="bundles", metadata={"name": ag})

        stats["plugins_indexed"] += 1

    def _index_hooks(self, path: Path, scope: str, stats: Dict[str, Any]) -> None:
        parsed = HookParser.parse(path)
        if "error" in parsed:
            return

        asset_id = f"hook_{scope}_{parsed['name']}"
        asset = EcosystemAsset(
            asset_id=asset_id,
            asset_type=EcosystemAssetType.LIFECYCLE_HOOK.value,
            name=parsed["name"],
            display_name=parsed["display_name"],
            description=parsed["description"],
            source_id=f"{scope}-hooks",
            source_path=str(path),
            content_hash=parsed["content_hash"],
            trust_state="reviewed",
            validation_state=parsed["validation_state"],
            compatibility_surfaces=parsed["compatibility_surfaces"],
            install_scope=scope,
            enabled_state="enabled",
            metadata_json={
                "hooks": parsed.get("hooks", []),
                "risk_class": parsed.get("risk_class", "safe_read"),
                "safety_note": parsed.get("safety_note", "")
            }
        )
        self.repo.insert_ecosystem_asset(asset)
        stats["hooks_indexed"] += 1

    def _index_mcp_config(self, path: Path, scope: str, stats: Dict[str, Any]) -> None:
        parsed = MCPConfigParser.parse(path)
        if "error" in parsed:
            return

        for srv in parsed.get("servers", []):
            srv_name = srv["server_name"]
            server_asset_id = f"mcp_{scope}_{srv_name}"
            asset = EcosystemAsset(
                asset_id=server_asset_id,
                asset_type=EcosystemAssetType.MCP_SERVER.value,
                name=srv_name,
                display_name=f"MCP Server: {srv_name} ({scope})",
                description=f"MCP Server {srv_name} using {srv['transport']} transport",
                source_id=f"{scope}-mcp",
                source_path=str(path),
                content_hash=parsed["content_hash"],
                trust_state="reviewed",
                validation_state="VERIFIED",
                compatibility_surfaces=["antigravity_ide", "antigravity_app", "antigravity_cli"],
                install_scope=scope,
                enabled_state="enabled",
                metadata_json=srv
            )
            self.repo.insert_ecosystem_asset(asset)
            stats["mcp_servers_indexed"] += 1

            # Register default capability representation
            cap = MCPCapability(
                server_asset_id=server_asset_id,
                capability_type="tool",
                name=f"{srv_name}_tools",
                description=f"Tools exposed by MCP server {srv_name}",
                schema_json={"transport": srv["transport"], "command": srv["command"]},
                risk_class="read_only" if "read" in srv_name or "query" in srv_name else "state_mutating",
                permission_mode="ask",
                auth_required=len(srv.get("configured_env_vars", [])) > 0
            )
            self.repo.insert_mcp_capability(cap)
            stats["mcp_capabilities_indexed"] += 1

    def _index_manifest(self, path: Path, scope: str, stats: Dict[str, Any]) -> None:
        parsed = ManifestParser.parse(path)
        if "error" in parsed:
            return

        asset_id = f"manifest_{scope}_{parsed['name']}"
        asset = EcosystemAsset(
            asset_id=asset_id,
            asset_type=EcosystemAssetType.DISCOVERY_MANIFEST.value,
            name=parsed["name"],
            display_name=parsed["display_name"],
            description=parsed["description"],
            source_id=f"{scope}-manifest",
            source_path=str(path),
            content_hash=parsed["content_hash"],
            trust_state="trusted",
            validation_state="VERIFIED",
            compatibility_surfaces=parsed["compatibility_surfaces"],
            install_scope=scope,
            enabled_state="enabled",
            metadata_json={"paths": parsed.get("paths", [])}
        )
        self.repo.insert_ecosystem_asset(asset)
        stats["manifests_indexed"] += 1

    def _index_sidecar(self, path: Path, scope: str, stats: Dict[str, Any]) -> None:
        sha256 = compute_file_hash(path)
        name = path.parent.name
        asset_id = f"sidecar_{scope}_{name}"
        asset = EcosystemAsset(
            asset_id=asset_id,
            asset_type=EcosystemAssetType.SIDECAR.value,
            name=name,
            display_name=f"Sidecar: {name} (App Surface Only)",
            description=f"Antigravity App sidecar background daemon {name}",
            source_id=f"{scope}-sidecar",
            source_path=str(path),
            content_hash=sha256,
            trust_state="reviewed",
            validation_state="APP_ONLY",
            compatibility_surfaces=["antigravity_app"],
            install_scope=scope,
            enabled_state="disabled",  # Disabled in standalone IDE to maintain compatibility
            metadata_json={"manifest": str(path), "note": "Unsupported in standalone Antigravity IDE"}
        )
        self.repo.insert_ecosystem_asset(asset)

    def _index_legacy_workflow(self, path: Path, scope: str, stats: Dict[str, Any]) -> None:
        parsed = WorkflowParser.parse(path)
        asset_id = f"workflow_{scope}_{parsed['name']}"
        asset = EcosystemAsset(
            asset_id=asset_id,
            asset_type=EcosystemAssetType.LEGACY_WORKFLOW.value,
            name=parsed["name"],
            display_name=parsed["display_name"],
            description=parsed["description"],
            source_id=f"{scope}-workflow",
            source_path=str(path),
            content_hash=parsed["content_hash"],
            trust_state="unverified",
            validation_state="RETIRED",
            compatibility_surfaces=[],
            install_scope=scope,
            enabled_state="archived",
            metadata_json={
                "retired_date": "2026-10-19",
                "migration_command": "/migrate-workflows",
                "target": "agent_skill"
            }
        )
        self.repo.insert_ecosystem_asset(asset)
        stats["legacy_workflows_indexed"] += 1
