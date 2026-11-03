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
