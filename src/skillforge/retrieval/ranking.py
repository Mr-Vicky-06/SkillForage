"""Hybrid Ranking and Scoring Engine for Skill Candidates."""

import re
from typing import Dict, List, Optional
from skillforge.database.models import (
    ProjectProfile,
    RecommendationScore,
    SkillRecord,
    SkillStatus,
    SourceType,
    TrustLevel,
)
from skillforge.database.repository import SkillRepository
from skillforge.analyzer.task_classifier import TaskAnalysis


# Configurable weights from Section 5
DEFAULT_WEIGHTS = {
    "task": 0.35,
    "tech": 0.25,
    "specificity": 0.15,
    "prereq": 0.10,
    "quality": 0.10,
    "feedback": 0.05,
}


class RankingEngine:
    def __init__(self, repository: SkillRepository, weights: Optional[Dict[str, float]] = None):
        self.repo = repository
        self.weights = weights or DEFAULT_WEIGHTS

    def rank_candidates(
        self,
        candidates: List[SkillRecord],
        task_analysis: TaskAnalysis,
        project_profile: Optional[ProjectProfile] = None
    ) -> List[RecommendationScore]:
        """Rank candidates using hybrid multi-factor scoring."""
        scored: List[RecommendationScore] = []

        task_text = task_analysis.raw_task.lower()
        project_techs = set()
        if project_profile:
            for t in (
                project_profile.frameworks +
                project_profile.languages +
                project_profile.ai_ml +
                project_profile.databases +
                project_profile.testing_frameworks +
                project_profile.infrastructure
            ):
                project_techs.add(t.lower())

        for skill in candidates:
            # Skip quarantined skills from general recommendations
            if skill.status == SkillStatus.QUARANTINED:
                continue

            # 1. Task relevance (0.0 to 1.0)
            task_score = 0.0
            signals: List[str] = []

            # Exact skill name mentioned in task
            norm_skill_name = skill.name.lower().replace("-", " ")
            if norm_skill_name in task_text or skill.name.lower() in task_text:
                task_score += 0.6
                signals.append(f"Direct mention of skill name '{skill.name}' in task")
            else:
                # Core keyword matching within skill name (e.g. "fastapi", "dbt", "android", "rag", "docker", "pytorch")
                skill_words = [w for w in skill.name.lower().split("-") if len(w) > 2 and w not in ("dev", "app", "py", "ts", "js", "expert", "patterns", "guide", "templates", "frameworks", "transformation")]
                name_word_matches = [w for w in skill_words if w in task_text or any(w == term.lower() for term in task_analysis.extracted_terms)]
                if name_word_matches:
                    task_score += 0.5
                    signals.append(f"Core skill keyword match: {', '.join(name_word_matches)}")

            # Check trigger phrases
            for tr in skill.triggers:
                if tr in task_text or task_text in tr:
                    task_score += 0.35
                    signals.append(f"Trigger phrase match: '{tr}'")
                    break

            # Term overlap in description
            desc_words = set(re.findall(r"[a-z]{3,}", skill.description.lower()))
            overlap = desc_words.intersection(set(task_analysis.extracted_terms))
            if overlap:
                task_score += min(0.3, len(overlap) * 0.08)
                signals.append(f"Keyword overlap in description ({len(overlap)} terms)")

            task_score = min(1.0, task_score)

            # 2. Tech relevance (0.0 to 1.0)
            tech_score = 0.0
            matched_techs = []
            if project_techs and skill.technologies:
                skill_techs = set(t.lower() for t in skill.technologies)
                matched = skill_techs.intersection(project_techs)
                if matched:
                    matched_techs = sorted(list(matched))
                    tech_score = min(1.0, len(matched) * 0.35 + 0.2)
                    signals.append(f"Matched project technologies: {', '.join(matched_techs)}")
            elif not project_techs:
                # Neutral if no project context provided
                tech_score = 0.5

            # 3. Specificity & Domain relevance (0.0 to 1.0)
            spec_score = 0.0
            if skill.category.lower() in [d.lower() for d in task_analysis.domains]:
                spec_score += 0.6
                signals.append(f"Category '{skill.category}' aligns with task domain")
            if any(intent in skill.description.lower() for intent in task_analysis.intents):
                spec_score += 0.4

            spec_score = min(1.0, spec_score)

            # 4. Prerequisites (0.0 to 1.0)
            prereq_score = 1.0
            warnings: List[str] = []
            for dep in skill.dependencies:
                if not dep.is_satisfied:
                    prereq_score -= 0.3
                    warnings.append(f"Prerequisite '{dep.name}' not detected on system")
            prereq_score = max(0.0, prereq_score)

            # 5. Quality (0.0 to 1.0)
            quality_score = skill.quality_score
            if skill.status == SkillStatus.BROKEN:
                quality_score = 0.2
                warnings.append("Skill has broken or missing metadata")
            elif skill.missing_files:
                warnings.append(f"Referenced files missing ({len(skill.missing_files)})")

            # 6. Historical feedback (0.0 to 1.0)
            fb_multiplier = self.repo.get_skill_feedback_multiplier(skill.id)
            fb_score = min(1.0, fb_multiplier / 1.25)

            # Total weighted score
            total = (
                self.weights["task"] * task_score +
                self.weights["tech"] * tech_score +
                self.weights["specificity"] * spec_score +
                self.weights["prereq"] * prereq_score +
                self.weights["quality"] * quality_score +
                self.weights["feedback"] * fb_score
            ) * fb_multiplier

            # Bonus for installed global or plugin skills to prefer active tools
            if skill.source_type in (SourceType.INSTALLED_GLOBAL, SourceType.INSTALLED_PLUGIN):
                total *= 1.1

            total = round(min(1.0, total), 4)
            confidence = round(total, 2)

            # Construct human-readable reasoning
            source_desc = "actively installed in Antigravity" if skill.source_type in (SourceType.INSTALLED_GLOBAL, SourceType.INSTALLED_PLUGIN) else "available offline in Universal Skill Book"
            reasoning_parts = [
                f"Selected '{skill.name}' ({source_desc}).",
                f"Signals: {'; '.join(signals) if signals else 'General domain match'}.",
            ]
            if matched_techs:
                reasoning_parts.append(f"Project stack compatibility: {', '.join(matched_techs)}.")

            scored.append(RecommendationScore(
                skill_id=skill.id,
                skill_name=skill.name,
                total_score=total,
                task_relevance=round(task_score, 2),
                tech_relevance=round(tech_score, 2),
                specificity=round(spec_score, 2),
                prerequisite_score=round(prereq_score, 2),
                quality_score=round(quality_score, 2),
                historical_feedback_score=round(fb_score, 2),
                confidence=confidence,
                source_type=skill.source_type,
                source_path=skill.source_path,
                trust_level=skill.trust_level,
                reasoning=" ".join(reasoning_parts),
                warnings=warnings
            ))

        # Sort by total score descending
        return sorted(scored, key=lambda s: s.total_score, reverse=True)
