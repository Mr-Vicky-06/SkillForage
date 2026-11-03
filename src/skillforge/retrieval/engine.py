"""Hybrid Retrieval Engine orchestrating FTS5, Knowledge Graph, and RRF."""

from __future__ import annotations
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skillforge.analyzer.project_detector import ProjectDetector
from skillforge.analyzer.task_classifier import TaskClassifier
from skillforge.database.models import ProjectProfile, SkillRecord, SkillStatus, SourceType
from skillforge.database.repository import SkillRepository
from skillforge.graph.traversal import GraphTraverser
from skillforge.retrieval.cache import QueryCache
from skillforge.retrieval.fusion import ReciprocalRankFusion


class RetrievalMode(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    DEEP = "deep"
    DISCOVERY = "discovery"
    BOOTSTRAP = "bootstrap"


FOUNDATIONAL_SKILL_ROLES = [
    ("architecture", ["clean-code", "software-architect", "architecture"]),
    ("testing", ["test-driven-development", "qa-engineer", "playwright-cli", "pytest"]),
    ("security", ["security-and-hardening", "security-reviewer", "security-auditor"]),
    ("optimization", ["performance-optimization", "python-performance-optimization"]),
    ("agentic", ["google-antigravity-sdk", "autonomous-agent-patterns", "agent-memory-systems"])
]


class HybridRetrievalEngine:
    """Next-generation multi-channel hybrid retrieval engine for SkillForge."""

    def __init__(self, repository: SkillRepository, cache: Optional[QueryCache] = None):
        self.repo = repository
        self.cache = cache or QueryCache(max_size=1000, ttl_seconds=300.0)
        self.classifier = TaskClassifier()
        self.detector = ProjectDetector()
        self.traverser = GraphTraverser(repository)
        self.rrf = ReciprocalRankFusion(k=60.0)

    def retrieve(
        self,
        query: str,
        project_path: Optional[str] = None,
        mode: RetrievalMode = RetrievalMode.BALANCED,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Perform multi-channel context-aware skill retrieval."""
        t0 = time.perf_counter()
        
        # 1. Project Profile Inspection
        project_profile: Optional[ProjectProfile] = None
        project_key = ""
        if project_path:
            p = Path(project_path).resolve()
            if p.is_dir():
                project_profile = self.detector.analyze_workspace(p)
                project_key = f"{p}:{','.join(sorted(project_profile.frameworks + project_profile.languages))}"

        # 2. Check Query Cache
        cached = self.cache.get(query=query, context=project_key, mode=mode.value, limit=limit)
        if cached:
            cached["cache_hit"] = True
            cached["duration_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return cached

        # 3. Handle Special Retrieval Modes
        if mode == RetrievalMode.BOOTSTRAP:
            result = self._bootstrap_project(project_profile, limit)
            result["duration_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            self.cache.put(query=query, value=result, context=project_key, mode=mode.value, limit=limit)
            return result

        # 4. Task Classification
        task_analysis = self.classifier.classify(query)

        # 5. Channel 1: Lexical Search (FTS5)
        fts_terms = task_analysis.extracted_terms + task_analysis.domains
        fts_query = " ".join(fts_terms[:10]) if fts_terms else query
        lexical_candidates = self.repo.search_fts(fts_query, limit=limit * 4)
        
        lexical_list: List[Tuple[str, float]] = []
        candidate_skills: Dict[str, SkillRecord] = {}
        for skill, score in lexical_candidates:
            if skill.status == SkillStatus.QUARANTINED:
                continue
            lexical_list.append((skill.id, score))
            candidate_skills[skill.id] = skill

        # 6. Channel 2: Graph Neighborhood & Cluster Expansion
        graph_list: List[Tuple[str, float]] = []
        if mode in (RetrievalMode.BALANCED, RetrievalMode.DEEP):
            max_hops = 2 if mode == RetrievalMode.DEEP else 1
            # Expand top 3 lexical candidates via graph CTE
            seed_ids = [s_id for s_id, _ in lexical_list[:3]]
            seen_graph = set()
            for seed in seed_ids:
                neighbors = self.traverser.get_neighbors(seed, max_hops=max_hops)
                for n in neighbors:
                    if n["node_type"] == "skill":
                        clean_id = n["id"].replace("skill:", "")
                        if clean_id not in seen_graph:
                            weight = n["weight"] / (n["depth"] * 1.0)
                            graph_list.append((clean_id, weight))
                            seen_graph.add(clean_id)
                            if clean_id not in candidate_skills:
                                s_record = self.repo.get_skill_by_id(clean_id)
                                if s_record and s_record.status != SkillStatus.QUARANTINED:
                                    candidate_skills[clean_id] = s_record

        # 7. Channel 3: Project Technology Alignment
        tech_list: List[Tuple[str, float]] = []
        if project_profile:
            techs = set(t.lower() for t in (
                project_profile.frameworks +
                project_profile.languages +
                project_profile.databases +
                project_profile.testing_frameworks
            ))
            for skill_id, skill in candidate_skills.items():
                s_techs = set(t.lower() for t in skill.technologies)
                matched = techs.intersection(s_techs)
                if matched:
                    tech_list.append((skill_id, len(matched) * 0.5))
            tech_list.sort(key=lambda x: x[1], reverse=True)

        # 8. Channel 4: Feedback & Quality
        quality_list: List[Tuple[str, float]] = []
        for skill_id, skill in candidate_skills.items():
            multiplier = self.repo.get_skill_feedback_multiplier(skill_id)
            final_q = skill.quality_score * multiplier
            # Active local/global tools priority boost
            if skill.source_type in (SourceType.INSTALLED_GLOBAL, SourceType.INSTALLED_PROJECT):
                final_q *= 1.25
            quality_list.append((skill_id, final_q))
        quality_list.sort(key=lambda x: x[1], reverse=True)

        # 9. Fuse Channels via Reciprocal Rank Fusion (RRF)
        channels = {
            "lexical": lexical_list,
            "quality": quality_list
        }
        if graph_list:
            channels["graph"] = graph_list
        if tech_list:
            channels["technology"] = tech_list

        fused = self.rrf.fuse(channels)

        # 10. Format and Enrich Final Selections
        results = []
        for item in fused[:limit]:
            skill_id = item["skill_id"]
            skill = candidate_skills.get(skill_id) or self.repo.get_skill_by_id(skill_id)
            if not skill:
                continue

            # Check prerequisites
            prereqs = self.traverser.find_skill_prerequisites(skill_id)
            missing_prereqs = [p["name"] for p in prereqs if not p.get("metadata", {}).get("satisfied", True)]

            results.append({
                "skill_id": skill.id,
                "name": skill.name,
                "description": skill.description[:200] + ("..." if len(skill.description) > 200 else ""),
                "category": skill.category,
                "source_type": skill.source_type.value,
                "source_path": skill.source_path,
                "rrf_score": item["rrf_score"],
                "normalized_confidence": item["normalized_score"],
                "signals": item["signals"],
                "channel_ranks": item["channel_ranks"],
                "missing_prerequisites": missing_prereqs,
                "quality_score": skill.quality_score
            })

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        response = {
            "query": query,
            "mode": mode.value,
            "count": len(results),
            "duration_ms": duration_ms,
            "cache_hit": False,
            "results": results
        }

        # Cache response
        self.cache.put(query=query, value=response, context=project_key, mode=mode.value, limit=limit)
        return response

    def _bootstrap_project(self, profile: Optional[ProjectProfile], limit: int) -> Dict[str, Any]:
        """Bootstrap a project with foundational engineering skills."""
        results = []
        selected_ids = set()

        for role, skill_candidates in FOUNDATIONAL_SKILL_ROLES:
            for s_name in skill_candidates:
                skill = self.repo.get_skill_by_name(s_name)
                if skill and skill.id not in selected_ids and skill.status != SkillStatus.QUARANTINED:
                    selected_ids.add(skill.id)
                    results.append({
                        "skill_id": skill.id,
                        "name": skill.name,
                        "description": skill.description[:180] + "...",
                        "category": skill.category,
                        "source_type": skill.source_type.value,
                        "source_path": skill.source_path,
                        "role": role,
                        "signals": [f"Foundational role: {role}"],
                        "normalized_confidence": 0.95
                    })
                    break
            if len(results) >= limit:
                break

        return {
            "mode": "bootstrap",
            "count": len(results),
            "results": results
        }
