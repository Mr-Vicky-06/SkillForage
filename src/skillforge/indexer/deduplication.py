"""Deduplication and Canonical Skill Selection Engine."""

import re
from typing import Dict, List, Set, Tuple
from skillforge.database.models import SkillRecord, SkillRelationship, SourceType


SOURCE_PRIORITY = {
    SourceType.INSTALLED_GLOBAL: 100,
    SourceType.INSTALLED_PLUGIN: 80,
    SourceType.INSTALLED_PROJECT: 70,
    SourceType.INSTALLED_BUILTIN: 60,
    SourceType.OFFLINE_BOOK: 40,
}


def normalize_skill_name(name: str) -> str:
    """Normalize skill name for duplicate grouping (e.g. ui-ux-pro-max-skill -> ui-ux-pro-max)."""
    norm = name.lower().replace("_", "-")
    norm = re.sub(r"-skill$", "", norm)
    norm = re.sub(r"-database$", "", norm)
    norm = re.sub(r"[^a-z0-9\-]", "", norm)
    return norm


class DeduplicationEngine:
    def group_duplicates(self, skills: List[SkillRecord]) -> Dict[str, List[SkillRecord]]:
        """Group skills by normalized name and hash to detect exact and near duplicates."""
        groups: Dict[str, List[SkillRecord]] = {}

        for skill in skills:
            norm_name = normalize_skill_name(skill.name)
            key = norm_name
            if key not in groups:
                groups[key] = []
            groups[key].append(skill)

        # Filter to only groups with more than 1 item
        return {k: v for k, v in groups.items() if len(v) > 1}

    def select_canonical_skill(self, duplicate_group: List[SkillRecord]) -> Tuple[SkillRecord, List[SkillRecord]]:
        """Select the strongest canonical skill from a duplicate group.
        
        Selection criteria:
        1. Source provenance (Installed global > Installed plugin > Project > Offline book)
        2. Description completeness (no truncation penalty)
        3. Quality score (fewer missing files)
        4. Freshness (mtime)
        """
        def score_skill(s: SkillRecord) -> float:
            score = SOURCE_PRIORITY.get(s.source_type, 0)
            score += s.quality_score * 30
            # Penalty for missing files
            score -= len(s.missing_files) * 5
            # Small bonus for recent mtime
            score += min(5.0, s.mtime / 1e9)
            return score

        sorted_skills = sorted(duplicate_group, key=score_skill, reverse=True)
        canonical = sorted_skills[0]
        duplicates = sorted_skills[1:]
        return canonical, duplicates

    def assign_relationships(self, skills: List[SkillRecord]) -> List[SkillRecord]:
        """Detect duplicate groups and attach duplicate_of relationships to non-canonical copies."""
        dup_groups = self.group_duplicates(skills)

        for norm_name, group in dup_groups.items():
            canonical, dups = self.select_canonical_skill(group)
            for d in dups:
                # Add relationship if not already present
                exists = any(r.target_skill_id == canonical.id and r.relationship_type == "duplicate_of" for r in d.relationships)
                if not exists:
                    d.relationships.append(SkillRelationship(
                        target_skill_id=canonical.id,
                        relationship_type="duplicate_of",
                        reason=f"Near-duplicate of canonical skill '{canonical.name}' ({canonical.source_type.value})"
                    ))

        return skills

