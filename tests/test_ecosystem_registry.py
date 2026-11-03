"""Tests for SkillForge Antigravity Ecosystem Registry and Capability Management."""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from skillforge.database.migrations import init_database
from skillforge.database.models import (
    EcosystemAsset,
    EcosystemAssetType,
    MCPCapability,
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
)
from skillforge.ecosystem.recommender import EcosystemRecommender
from skillforge.ecosystem.scanner import EcosystemScanner
from skillforge.mcp_server.tools import SkillForgeTools


@pytest.fixture
def temp_repo():
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_ecosystem.db"
        repo = SkillRepository(db_path)
        yield repo
        repo.close()


def test_rule_parser(tmp_path):
    # Modular rule with frontmatter
    rule_file = tmp_path / "test-rule.md"
    rule_file.write_text("""---
trigger: model_decision
description: Enforce architecture boundaries
globs: src/**/*.py
---
# Architecture Rules
Do not import database layer in presentation layer.
""", encoding="utf-8")

    parsed = RuleParser.parse(rule_file)
    assert parsed["name"] == "test-rule"
    assert parsed["trigger"] == "model_decision"
    assert parsed["validation_state"] == "VERIFIED"
    assert "antigravity_ide" in parsed["compatibility_surfaces"]
    assert parsed["globs"] == ["src/**/*.py"]

    # Workspace always-on instruction
    instr_file = tmp_path / "AGENTS.md"
    instr_file.write_text("# Global Workspace Conventions\nAlways verify tests.", encoding="utf-8")
    parsed_instr = RuleParser.parse(instr_file)
    assert parsed_instr["asset_type"] == "workspace_instruction"
    assert parsed_instr["trigger"] == "always_on"
    assert parsed_instr["validation_state"] == "VERIFIED"


def test_agent_parser(tmp_path):
    agent_file = tmp_path / "security-reviewer.md"
    agent_file.write_text("""---
name: security-reviewer
description: Security auditor for prompt injection and permissions
tools:
  - read_file
  - run_command
model: pro
commandExecutionPolicy: ask
subagent: true
---
You are a senior security reviewer.
""", encoding="utf-8")

    parsed = AgentParser.parse(agent_file)
    assert parsed["name"] == "security-reviewer"
    assert parsed["tools"] == ["read_file", "run_command"]
    assert parsed["model"] == "pro"
    assert parsed["command_execution_policy"] == "ask"
    assert parsed["subagent"] is True
    assert parsed["validation_state"] == "VERIFIED"


def test_plugin_parser(tmp_path):
    plugin_dir = tmp_path / "test-plugin"
    plugin_dir.mkdir()
    manifest = plugin_dir / "plugin.json"
    manifest.write_text(json.dumps({
        "name": "test-plugin",
        "version": "1.2.0",
        "description": "Test plugin bundle",
        "license": "Apache-2.0"
    }), encoding="utf-8")

    # Add child skill
    skills_dir = plugin_dir / "skills" / "my-skill"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("---\ndescription: Child skill\n---\n# My Skill", encoding="utf-8")

    parsed = PluginParser.parse(plugin_dir)
    assert parsed["name"] == "test-plugin"
    assert parsed["version"] == "1.2.0"
    assert parsed["bundled_skills"] == ["my-skill"]
    assert parsed["validation_state"] == "VERIFIED"


def test_hook_parser(tmp_path):
    hooks_file = tmp_path / "hooks.json"
    hooks_file.write_text(json.dumps({
        "hooks": [
            {"event": "PostToolUse", "matcher": "edit_file", "command": "black --check .", "timeout": 3000},
            {"event": "Stop", "matcher": "*", "command": "pytest", "timeout": 10000}
        ]
    }), encoding="utf-8")

    parsed = HookParser.parse(hooks_file)
    assert parsed["asset_type"] == "lifecycle_hook"
    assert len(parsed["hooks"]) == 2
    assert parsed["risk_class"] == "automated_formatter"
    assert "fail open" in parsed["safety_note"].lower()


def test_mcp_config_parser(tmp_path):
    mcp_file = tmp_path / "mcp_config.json"
    mcp_file.write_text(json.dumps({
        "mcpServers": {
            "local-server": {"command": "python", "args": ["-m", "srv"], "env": {"SECRET_TOKEN": "12345"}},
            "remote-server": {"serverUrl": "https://mcp.internal/api"}
        }
    }), encoding="utf-8")

    parsed = MCPConfigParser.parse(mcp_file)
    assert len(parsed["servers"]) == 2
    local = next(s for s in parsed["servers"] if s["server_name"] == "local-server")
    assert local["transport"] == "stdio"
    assert local["configured_env_vars"] == ["SECRET_TOKEN"]  # Key preserved, secret value NEVER stored!
    remote = next(s for s in parsed["servers"] if s["server_name"] == "remote-server")
    assert remote["transport"] == "streamable_http"


def test_ecosystem_repository_crud(temp_repo):
    asset = EcosystemAsset(
        asset_id="rule_arch_boundaries",
        asset_type=EcosystemAssetType.AGENT_RULE.value,
        name="architecture-boundaries",
        display_name="Architecture Boundaries",
        description="Prevents layer violation",
        source_id="workspace-rule",
        compatibility_surfaces=["antigravity_ide", "antigravity_cli"],
        install_scope="workspace",
        enabled_state="enabled",
        metadata_json={"trigger": "model_decision"}
    )
    temp_repo.insert_ecosystem_asset(asset)

    retrieved = temp_repo.get_ecosystem_asset("rule_arch_boundaries")
    assert retrieved is not None
    assert retrieved["name"] == "architecture-boundaries"
    assert retrieved["install_scope"] == "workspace"
    assert "antigravity_ide" in retrieved["compatibility_surfaces"]

    # Test MCP capability insertion
    cap = MCPCapability(
        server_asset_id="rule_arch_boundaries",
        capability_type="tool",
        name="verify_architecture",
        description="Audit import AST",
        risk_class="read_only"
    )
    temp_repo.insert_mcp_capability(cap)
    caps = temp_repo.list_mcp_capabilities("rule_arch_boundaries")
    assert len(caps) == 1
    assert caps[0]["name"] == "verify_architecture"

    # Test component linking
    temp_repo.link_ecosystem_component("rule_arch_boundaries", "child_skill_1", rel_type="requires")
    components = temp_repo.get_ecosystem_components("rule_arch_boundaries")
    # Child asset child_skill_1 is not in ecosystem_assets, so get_ecosystem_components returns empty if inner join
    stats = temp_repo.get_ecosystem_stats()
    assert stats["total_assets"] == 1
    assert stats["total_mcp_capabilities"] == 1


def test_ecosystem_recommender(temp_repo, tmp_path):
    # Setup dummy project
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test-mcp-app'\ndependencies = ['mcp', 'pytest']\n", encoding="utf-8")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text("def test_dummy(): pass\n", encoding="utf-8")

    recommender = EcosystemRecommender(temp_repo)
    plan = recommender.recommend_setup(tmp_path)

    assert plan["project_name"] == tmp_path.name
    assert len(plan["recommended_rules"]) >= 2
    assert len(plan["recommended_agents"]) >= 2
    assert any(m["name"] == "skillforge" for m in plan["recommended_mcp_servers"])
    assert any(h["event"] == "Stop" for h in plan["recommended_hooks"])


def test_mcp_tools_ecosystem(temp_repo):
    asset = EcosystemAsset(
        asset_id="agent_code_reviewer",
        asset_type=EcosystemAssetType.CUSTOM_AGENT.value,
        name="code-reviewer",
        display_name="Code Reviewer",
        description="Senior code reviewer",
        source_id="global-agent",
        compatibility_surfaces=["antigravity_ide"],
        install_scope="global"
    )
    temp_repo.insert_ecosystem_asset(asset)

    tools = SkillForgeTools(temp_repo)
    assets = tools.list_ecosystem_assets(asset_type="custom_agent")
    assert len(assets) == 1
    assert assets[0]["name"] == "code-reviewer"

    validation = tools.validate_ecosystem_asset("agent_code_reviewer")
    assert validation["is_ide_compatible"] is True
    assert validation["asset_type"] == "custom_agent"

