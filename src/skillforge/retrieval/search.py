"""Hybrid Candidate Search Engine combining FTS5, Technology Matching, and Triggers."""

from typing import Dict, List, Optional, Set, Tuple
from skillforge.database.models import ProjectProfile, SkillRecord
from skillforge.database.repository import SkillRepository
from skillforge.analyzer.task_classifier import TaskAnalysis


class CandidateSearchEngine:
    def __init__(self, repository: SkillRepository):
        self.repo = repository

    def find_candidates(
        self,
        task_analysis: TaskAnalysis,
        project_profile: Optional[ProjectProfile] = None,
        limit: int = 50
    ) -> List[SkillRecord]:
        """Gather skill candidates across FTS5, technologies, categories, and triggers."""
        candidate_map: Dict[str, SkillRecord] = {}

        # 1. FTS5 Search using task terms and domain keywords
        search_terms = task_analysis.extracted_terms + task_analysis.domains + task_analysis.intents
        if search_terms:
            fts_query = " ".join(search_terms[:12])
            fts_results = self.repo.search_fts(fts_query, limit=limit)
            for skill, _ in fts_results:
                candidate_map[skill.id] = skill

        # 2. Match project technologies
        if project_profile:
            project_techs = (
                project_profile.frameworks +
                project_profile.languages +
                project_profile.ai_ml +
                project_profile.databases +
                project_profile.testing_frameworks +
                project_profile.infrastructure
            )
            for tech in project_techs:
                tech_skills = self.repo.get_skills_by_technology(tech)
                for s in tech_skills:
                    if s.id not in candidate_map:
                        candidate_map[s.id] = s

        # 3. Category matching based on identified domains
        for domain in task_analysis.domains:
            domain_skills = self.repo.list_skills(category=domain, limit=20)
            for s in domain_skills:
                if s.id not in candidate_map:
                    candidate_map[s.id] = s

        return list(candidate_map.values())
