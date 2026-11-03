"""Final Context-Aware Skill Selection and Deduplication Filtering."""

import re
from typing import Dict, List, Optional, Tuple
from skillforge.database.models import RecommendationScore
from skillforge.database.repository import SkillRepository
from skillforge.indexer.deduplication import normalize_skill_name


CONFIDENCE_THRESHOLD = 0.22


class SkillSelector:
    def __init__(self, repository: SkillRepository, min_threshold: float = CONFIDENCE_THRESHOLD):
        self.repo = repository
        self.min_threshold = min_threshold

    def select(
        self,
        ranked_scores: List[RecommendationScore],
        task: str,
        project_path: str = "",
        max_skills: int = 3
    ) -> Tuple[List[RecommendationScore], str]:
        """Select top candidates while eliminating duplicates and checking threshold.
        
        Returns:
            (selected_scores, explanation_summary)
        """
        if not ranked_scores:
            return [], "NO MATCH: No matching skills found for the current query or project."

        # Filter out scores below threshold
        valid = [s for s in ranked_scores if s.total_score >= self.min_threshold]
        if not valid:
            top_score = ranked_scores[0].total_score if ranked_scores else 0.0
            return [], f"NO MATCH: Best matching skill scored {top_score:.2f}, below confidence threshold {self.min_threshold:.2f}."

        # Deduplication filtering: keep only the highest scoring skill per normalized name
        selected: List[RecommendationScore] = []
        seen_names = set()

        for score in valid:
            norm_name = normalize_skill_name(score.skill_name)
            if norm_name in seen_names:
                continue
            seen_names.add(norm_name)

            if not selected:
                score.suggested_role = "primary"
            else:
                score.suggested_role = "complementary"

            selected.append(score)
            if len(selected) >= max_skills:
                break

        # Generate summary explanation
        summary_lines = [
            f"SkillForge Context-Aware Selection ({len(selected)} skill{'s' if len(selected) != 1 else ''} selected):"
        ]
        for idx, s in enumerate(selected, 1):
            role_label = f"[{s.suggested_role.upper()}]"
            source_badge = "[INSTALLED]" if "installed" in s.source_type.value else "[OFFLINE-BOOK]"
            summary_lines.append(
                f"{idx}. {role_label} {source_badge} **{s.skill_name}** (Confidence: {int(s.confidence * 100)}%)\n"
                f"   Why: {s.reasoning}"
            )
            if s.warnings:
                summary_lines.append(f"   Notice: {'; '.join(s.warnings)}")

        explanation = "\n".join(summary_lines)

        # Record routing decision for auditing
        self.repo.record_routing(
            task=task,
            project_path=project_path,
            selected_skills=[s.skill_name for s in selected],
            confidence=selected[0].confidence if selected else 0.0,
            reasoning=explanation
        )

        return selected, explanation

