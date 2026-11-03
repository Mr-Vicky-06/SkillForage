"""SkillForge Data Models and Schemas."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SkillStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    BROKEN = "broken"
    UNVERIFIED = "unverified"
    QUARANTINED = "quarantined"


class TrustLevel(str, Enum):
    TRUSTED = "trusted"         # Verified official or thoroughly audited
    REVIEWED = "reviewed"       # Static inspection passed without flags
    UNVERIFIED = "unverified"   # Third-party, basic frontmatter only
    QUARANTINED = "quarantined" # Security risk, prompt override, etc.
    BROKEN = "broken"           # Malformed frontmatter, missing files


class SourceType(str, Enum):
    OFFLINE_BOOK = "offline_book"
    INSTALLED_GLOBAL = "installed_global"
    INSTALLED_PLUGIN = "installed_plugin"
    INSTALLED_PROJECT = "installed_project"
    INSTALLED_BUILTIN = "installed_builtin"


@dataclass
class SkillDependency:
    dependency_type: str  # binary, python_pkg, node_pkg, mcp, tool, env_var
    name: str
    is_satisfied: bool = True
    details: str = ""


@dataclass
class SkillRelationship:
    target_skill_id: str
    relationship_type: str  # duplicate_of, conflicts_with, complements, requires, enhances
    reason: str = ""


@dataclass
class SkillRecord:
    id: str
    name: str
    description: str
    category: str
    subcategory: str = ""
    source_type: SourceType = SourceType.OFFLINE_BOOK
    source_path: str = ""
    relative_path: str = ""
    file_hash: str = ""
    mtime: float = 0.0
    status: SkillStatus = SkillStatus.ACTIVE
    trust_level: TrustLevel = TrustLevel.REVIEWED
    quality_score: float = 1.0
    author: str = ""
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    dependencies: List[SkillDependency] = field(default_factory=list)
    relationships: List[SkillRelationship] = field(default_factory=list)
    referenced_files: List[str] = field(default_factory=list)
    missing_files: List[str] = field(default_factory=list)
    security_flags: List[str] = field(default_factory=list)
    raw_frontmatter: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ProjectProfile:
    project_path: str
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    package_managers: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    ai_ml: List[str] = field(default_factory=list)
    infrastructure: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    testing_frameworks: List[str] = field(default_factory=list)
    deployment: List[str] = field(default_factory=list)
    detected_files: List[str] = field(default_factory=list)
    conventions: List[str] = field(default_factory=list)
    last_analyzed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RecommendationScore:
    skill_id: str
    skill_name: str
    total_score: float
    task_relevance: float
    tech_relevance: float
    specificity: float
    prerequisite_score: float
    quality_score: float
    historical_feedback_score: float
    confidence: float
    source_type: SourceType
    source_path: str
    trust_level: TrustLevel
    reasoning: str
    warnings: List[str] = field(default_factory=list)
    suggested_role: str = "primary"  # primary, complementary


class NodeType(str, Enum):
    SKILL = "skill"
    TECHNOLOGY = "technology"
    CATEGORY = "category"
    DOMAIN = "domain"
    CONCEPT = "concept"
    TOOL = "tool"


class EdgeType(str, Enum):
    PREREQUISITE_FOR = "PREREQUISITE_FOR"
    COMPLEMENTS = "COMPLEMENTS"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    SUPERSEDES = "SUPERSEDES"
    USES_TECH = "USES_TECH"
    BELONGS_TO_CATEGORY = "BELONGS_TO_CATEGORY"
    ASSOCIATED_WITH_CONCEPT = "ASSOCIATED_WITH_CONCEPT"


@dataclass
class GraphNode:
    id: str
    node_type: NodeType
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relationship_type: str
    weight: float = 1.0
    confidence: float = 1.0
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None


@dataclass
class EntityAlias:
    alias: str
    canonical_node_id: str
    alias_type: str = "synonym"
    id: Optional[int] = None



class EcosystemAssetType(str, Enum):
    AGENT_SKILL = "agent_skill"
    AGENT_RULE = "agent_rule"
    WORKSPACE_INSTRUCTION = "workspace_instruction"
    CUSTOM_AGENT = "custom_agent"
    PLUGIN_BUNDLE = "plugin_bundle"
    LIFECYCLE_HOOK = "lifecycle_hook"
    MCP_SERVER = "mcp_server"
    MCP_TOOL = "mcp_tool"
    MCP_RESOURCE = "mcp_resource"
    MCP_PROMPT = "mcp_prompt"
    DISCOVERY_MANIFEST = "discovery_manifest"
    SIDECAR = "sidecar"
    LEGACY_WORKFLOW = "legacy_workflow"
    IDE_EXTENSION = "ide_extension"
    OFFICIAL_BUNDLE = "official_bundle"
    REFERENCE_PACK = "reference_pack"
    EVALUATION_PACK = "evaluation_pack"


@dataclass
class EcosystemAsset:
    asset_id: str
    asset_type: str
    name: str
    display_name: str
    description: str
    source_id: str
    source_url: str = ""
    source_path: str = ""
    version: str = "1.0.0"
    license_spdx: str = "MIT"
    license_notes: str = ""
    content_hash: str = ""
    trust_state: str = "reviewed"
    validation_state: str = "unverified"
    compatibility_surfaces: List[str] = field(default_factory=lambda: ["antigravity_ide"])
    install_scope: str = "workspace"
    enabled_state: str = "discovered"
    metadata_json: Dict[str, Any] = field(default_factory=dict)
    last_verified_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class EcosystemComponent:
    parent_asset_id: str
    child_asset_id: str
    relationship_type: str  # 'contains', 'bundles', 'depends_on', 'provides'
    metadata_json: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None


@dataclass
class MCPCapability:
    server_asset_id: str
    capability_type: str  # 'tool', 'resource', 'prompt'
    name: str
    description: str = ""
    schema_json: Dict[str, Any] = field(default_factory=dict)
    risk_class: str = "read_only"  # 'read_only', 'state_mutating', 'destructive'
    permission_mode: str = "ask"  # 'ask', 'allow', 'deny'
    auth_required: bool = False
    id: Optional[int] = None


@dataclass
class AssetEvidence:
    asset_id: str
    evidence_source: str
    content_hash: str = ""
    extraction_method: str = "static_ast"
    validation_result: str = "VERIFIED"  # 'VERIFIED', 'PARTIALLY VERIFIED', 'FAILED', 'NOT TESTED'
    notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: Optional[int] = None


@dataclass
class AssetInstallation:
    asset_id: str
    target_scope: str  # 'workspace', 'global'
    target_path: str
    installed_version: str = "1.0.0"
    installed_hash: str = ""
    install_status: str = "active"  # 'active', 'disabled', 'orphaned'
    verification_result: str = "VERIFIED"
    installed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: Optional[int] = None


@dataclass
class AssetRelationship:
    source_asset_id: str
    target_asset_id: str
    relationship_type: str
    confidence: float = 1.0
    notes: str = ""
    id: Optional[int] = None
