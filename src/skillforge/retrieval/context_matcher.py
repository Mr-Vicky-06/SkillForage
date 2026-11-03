"""Unified Context Matcher Pipeline for SkillForge."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from skillforge.analyzer.project_detector import ProjectDetector
from skillforge.analyzer.task_classifier import TaskClassifier
from skillforge.database.models import ProjectProfile, RecommendationScore, SkillRecord
from skillforge.database.repository import SkillRepository
from skillforge.retrieval.ranking import RankingEngine
from skillforge.retrieval.search import CandidateSearchEngine
from skillforge.retrieval.selector import SkillSelector


class ContextMatcher:
    def __init__(self, repository: SkillRepository):
        self.repo = repository
        self.detector = ProjectDetector()
        self.classifier = TaskClassifier()
        self.searcher = CandidateSearchEngine(repository)
        self.ranker = RankingEngine(repository)
        self.selector = SkillSelector(repository)

    def match(
        self,
        task: str,
        project_path: Optional[str] = None,
        max_skills: int = 3,
        force_refresh_profile: bool = False
    ) -> Tuple[List[RecommendationScore], str, Optional[ProjectProfile]]:
        """End-to-end context-aware skill recommendation pipeline."""
        # 1. Project Context Analysis
        profile: Optional[ProjectProfile] = None
        if project_path:
            p_path = str(Path(project_path).resolve())
            if not force_refresh_profile:
                profile = self.repo.get_project_profile(p_path)
            if not profile:
                profile = self.detector.analyze_workspace(p_path)
                self.repo.save_project_profile(profile)

        # 2. Task Intent Classification
        task_analysis = self.classifier.classify(task)

        # 3. Candidate Search
        candidates = self.searcher.find_candidates(task_analysis, profile, limit=60)

        # 4. Hybrid Ranking
        ranked = self.ranker.rank_candidates(candidates, task_analysis, profile)

        # 5. Selection and Deduplication
        selected, explanation = self.selector.select(
            ranked_scores=ranked,
            task=task,
            project_path=project_path or "",
            max_skills=max_skills
        )

        return selected, explanation, profile

