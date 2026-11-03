"""Implementation of SkillForge MCP Tool Handlers."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillforge.database.models import SkillRecord, SkillStatus, SourceType
from skillforge.database.repository import SkillRepository
from skillforge.indexer.validator import SkillValidator
from skillforge.retrieval.context_matcher import ContextMatcher
from skillforge.security.path_guard import PathTraversalError, validate_safe_relative_path


class SkillForgeTools:
    def __init__(self, repository: SkillRepository):
        self.repo = repository
        self.matcher = ContextMatcher(repository)
        self.validator = SkillValidator()

    def status(self) -> Dict[str, Any]:
        """Returns database health, skill counts, sources, and index time."""
        stats = self.repo.get_stats()
        return {
            "status": "online",
            "server": "SkillForge MCP Server v0.1.0",
            "database_path": str(self.repo.db_path),
            "stats": stats
        }

    def search_skills(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Search skills by keyword, domain, technology, or task description (returns compact metadata)."""
        results = self.repo.search_fts(query, limit=limit)
        items = []
        for skill, score in results:
            items.append({
                "id": skill.id,
                "name": skill.name,
                "description": skill.description[:180] + ("..." if len(skill.description) > 180 else ""),
                "category": skill.category,
                "source_type": skill.source_type.value,
                "score": round(score, 3),
                "quality_score": skill.quality_score,
                "technologies": skill.technologies[:5]
            })
        return items

    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze a project workspace and return detected languages, frameworks, and architecture signals."""
        profile = self.matcher.detector.analyze_workspace(project_path)
        self.repo.save_project_profile(profile)
        return {
            "project_path": profile.project_path,
            "languages": profile.languages,
            "frameworks": profile.frameworks,
            "package_managers": profile.package_managers,
            "databases": profile.databases,
            "ai_ml": profile.ai_ml,
            "infrastructure": profile.infrastructure,
            "testing_frameworks": profile.testing_frameworks,
            "build_tools": profile.build_tools,
            "detected_manifests": profile.detected_files
        }

    def recommend_skills(
        self,
        task: str,
        project_path: Optional[str] = None,
        max_skills: int = 3
    ) -> Dict[str, Any]:
        """Recommend ranked skills matching user task and project context with full explanations."""
        selected, explanation, profile = self.matcher.match(
            task=task,
            project_path=project_path,
            max_skills=max_skills
        )
        recommendations = []
        for s in selected:
            recommendations.append({
                "skill_name": s.skill_name,
                "skill_id": s.skill_id,
                "role": s.suggested_role,
                "confidence": s.confidence,
                "source_type": s.source_type.value,
                "source_path": s.source_path,
                "reasoning": s.reasoning,
                "warnings": s.warnings
            })
        return {
            "task": task,
            "selected_count": len(recommendations),
            "explanation": explanation,
            "recommendations": recommendations,
            "project_summary": {
                "languages": profile.languages if profile else [],
                "frameworks": profile.frameworks if profile else []
            } if profile else None
        }

    def load_skill(self, skill_name_or_id: str) -> Dict[str, Any]:
        """Loads a skill's full SKILL.md instructions into the agent context."""
        skill = self.repo.get_skill_by_id(skill_name_or_id)
        if not skill:
            skill = self.repo.get_skill_by_name(skill_name_or_id)

        if not skill:
            return {
                "error": f"Skill '{skill_name_or_id}' not found in SkillForge registry."
            }

        path = Path(skill.source_path)
        if not path.is_file():
            return {
                "error": f"Skill file does not exist on disk: {skill.source_path}"
            }

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {
                "error": f"Failed to read skill file: {str(e)}"
            }

        return {
            "skill_name": skill.name,
            "skill_id": skill.id,
            "category": skill.category,
            "source_type": skill.source_type.value,
            "source_path": skill.source_path,
            "file_hash": skill.file_hash,
            "quality_score": skill.quality_score,
            "warnings": skill.security_flags + ([f"Missing {f}" for f in skill.missing_files]),
            "referenced_resources": skill.referenced_files,
            "content": content
        }

    def read_skill_resource(self, skill_name_or_id: str, relative_path: str) -> Dict[str, Any]:
        """Reads a referenced resource or document file belonging to a skill with path traversal prevention."""
        skill = self.repo.get_skill_by_id(skill_name_or_id)
        if not skill:
            skill = self.repo.get_skill_by_name(skill_name_or_id)

        if not skill:
            return {"error": f"Skill '{skill_name_or_id}' not found."}

        skill_dir = Path(skill.source_path).parent

        try:
            target_path = validate_safe_relative_path(skill_dir, relative_path)
        except PathTraversalError as e:
            return {"error": f"Security Violation: {str(e)}"}

        if not target_path.is_file():
            return {"error": f"Resource file not found: {relative_path} in {skill.name}"}

        try:
            content = target_path.read_text(encoding="utf-8", errors="replace")
            return {
                "skill_name": skill.name,
                "resource_path": relative_path,
                "absolute_path": str(target_path),
                "content": content
            }
        except Exception as e:
            return {"error": f"Failed to read resource file: {str(e)}"}

    def list_skills(
        self,
        category: Optional[str] = None,
        source_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List skills in registry with category, source, and status filters."""
        skills = self.repo.list_skills(
            category=category,
            source_type=source_type,
            status=status,
            limit=limit,
            offset=offset
        )
        return {
            "total_returned": len(skills),
            "skills": [
                {
                    "id": s.id,
                    "name": s.name,
                    "category": s.category,
                    "source_type": s.source_type.value,
                    "quality_score": s.quality_score,
                    "trust_level": s.trust_level.value,
                    "status": s.status.value
                }
                for s in skills
            ]
        }

    def validate_skill(self, skill_name_or_id: str) -> Dict[str, Any]:
        """Validates a skill's structure, frontmatter, and prerequisites."""
        skill = self.repo.get_skill_by_id(skill_name_or_id)
        if not skill:
            skill = self.repo.get_skill_by_name(skill_name_or_id)

        if not skill:
            return {"error": f"Skill '{skill_name_or_id}' not found."}

        is_valid, messages = self.validator.validate_skill(skill)
        return {
            "skill_name": skill.name,
            "is_valid": is_valid,
            "status": skill.status.value,
            "trust_level": skill.trust_level.value,
            "quality_score": skill.quality_score,
            "dependencies": [
                {"name": d.name, "type": d.dependency_type, "satisfied": d.is_satisfied}
                for d in skill.dependencies
            ],
            "messages": messages
        }

    def record_skill_feedback(
        self,
        skill_name_or_id: str,
        rating: int,
        feedback_type: str,
        comment: str = "",
        task_context: str = ""
    ) -> Dict[str, Any]:
        """Record user/agent feedback on whether a loaded skill was helpful, irrelevant, etc."""
        skill = self.repo.get_skill_by_id(skill_name_or_id)
        if not skill:
            skill = self.repo.get_skill_by_name(skill_name_or_id)

        skill_id = skill.id if skill else skill_name_or_id
        # Clamp rating to [-1, 0, 1]
        clamped_rating = max(-1, min(1, rating))

        self.repo.record_feedback(
            skill_id=skill_id,
            rating=clamped_rating,
            feedback_type=feedback_type,
            comment=comment,
            task_context=task_context
        )
        return {
            "status": "success",
            "skill_id": skill_id,
            "recorded_rating": clamped_rating,
            "feedback_type": feedback_type
        }

