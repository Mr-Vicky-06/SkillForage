"""Implementation of SkillForge MCP Tool Handlers."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillforge.database.models import SkillRecord, SkillStatus, SourceType
from skillforge.database.repository import SkillRepository
from skillforge.graph.traversal import GraphTraverser
from skillforge.indexer.validator import SkillValidator
from skillforge.retrieval.context_matcher import ContextMatcher
from skillforge.retrieval.engine import HybridRetrievalEngine, RetrievalMode
from skillforge.security.path_guard import PathTraversalError, validate_safe_relative_path


class SkillForgeTools:
    def __init__(self, repository: SkillRepository):
        self.repo = repository
        self.matcher = ContextMatcher(repository)
        self.engine = HybridRetrievalEngine(repository)
        self.traverser = GraphTraverser(repository)
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
            skill_rec = self.repo.get_skill_by_id(s.skill_id)
            cat = skill_rec.category if skill_rec else "general"
            recommendations.append({
                "skill_name": s.skill_name,
                "skill_id": s.skill_id,
                "name": s.skill_name,
                "id": s.skill_id,
                "category": cat,
                "role": s.suggested_role,
                "confidence": s.confidence,
                "source_type": s.source_type.value,
                "source_path": s.source_path,
                "reasoning": s.reasoning,
                "warnings": s.warnings,
                "offline_capable": True
            })
        return {
            "task": task,
            "selected_count": len(recommendations),
            "explanation": explanation,
            "recommendations": recommendations,
            "recommended_skills": recommendations,
            "project_summary": {
                "languages": profile.languages if profile else [],
                "frameworks": profile.frameworks if profile else []
            } if profile else None
        }

    def load_skill(self, skill_name_or_id: str, approval_token: str = "", conversation_id: str = "") -> Dict[str, Any]:
        """Loads a skill's full SKILL.md instructions strictly requiring an APPROVED authorization token."""
        if not approval_token:
            return {
                "error": "ACCESS DENIED: Direct skill loading without user approval is prohibited. You must query 'skillforge_recommend_skills', obtain explicit human approval ('YES' or 'SELECT <id>'), and provide the valid approval token."
            }
        from skillforge.runtime.loader import ControlledSkillLoader
        loader = ControlledSkillLoader(self.repo)
        return loader.load_approved_skill(
            skill_identifier=skill_name_or_id,
            approval_token=approval_token,
            conversation_id=conversation_id
        )

    def read_skill_resource(self, skill_name_or_id: str, relative_path: str, approval_token: str = "", conversation_id: str = "") -> Dict[str, Any]:
        """Reads a referenced resource file strictly requiring an approved authorization token and path traversal prevention."""
        if not approval_token:
            return {
                "error": "ACCESS DENIED: Direct resource access without approval token is prohibited. Provide the approval token issued for this skill."
            }
        from skillforge.approval.token_manager import ApprovalTokenManager
        token_mgr = ApprovalTokenManager(self.repo.db_path)
        status_rec = token_mgr.get_status(approval_token)
        if not status_rec:
            return {"error": f"ACCESS DENIED: Approval token '{approval_token}' not found."}
        if status_rec.get("status") not in ["approved", "consumed"]:
            return {"error": f"ACCESS DENIED: Token '{approval_token}' is not in an authorized state (status: {status_rec.get('status')})."}

        # Verify conversation binding
        if conversation_id and status_rec.get("conversation_id") and conversation_id != status_rec.get("conversation_id"):
            return {"error": "ACCESS DENIED: Conversation binding mismatch."}

        authorized_ids = status_rec.get("approved_ids") or status_rec.get("candidate_ids", [])
        if not any(skill_name_or_id == a or a.endswith(f":{skill_name_or_id}") or a.endswith(f"--{skill_name_or_id}") or skill_name_or_id in a for a in authorized_ids):
            return {"error": f"ACCESS DENIED: Skill '{skill_name_or_id}' was not authorized under token '{approval_token}'."}

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

    def explain_recommendation(
        self,
        skill_name_or_id: str,
        task: str,
        project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provide detailed scoring breakdown and graph signals for why a skill was recommended."""
        skill = self.repo.get_skill_by_id(skill_name_or_id)
        if not skill:
            skill = self.repo.get_skill_by_name(skill_name_or_id)

        if not skill:
            return {"error": f"Skill '{skill_name_or_id}' not found."}

        # Analyze task and project
        task_analysis = self.matcher.classifier.classify(task)
        project_profile = None
        if project_path:
            p = Path(project_path).resolve()
            if p.is_dir():
                project_profile = self.matcher.detector.analyze_workspace(p)

        # Cluster and neighbors
        cluster = self.traverser.find_related_cluster(skill.id)

        # Lexical score
        fts_res = self.repo.search_fts(task, limit=30)
        lexical_rank = None
        lexical_score = 0.0
        for rank, (s, sc) in enumerate(fts_res, 1):
            if s.id == skill.id:
                lexical_rank = rank
                lexical_score = round(sc, 4)
                break

        # Feedback multiplier
        fb_mult = self.repo.get_skill_feedback_multiplier(skill.id)

        # Project tech match
        matched_techs = []
        if project_profile:
            p_techs = set(t.lower() for t in (project_profile.frameworks + project_profile.languages + project_profile.databases))
            s_techs = set(t.lower() for t in skill.technologies)
            matched_techs = sorted(list(p_techs.intersection(s_techs)))

        return {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "category": skill.category,
            "quality_score": skill.quality_score,
            "feedback_multiplier": fb_mult,
            "lexical": {
                "rank": lexical_rank,
                "score": lexical_score,
                "in_top_30": lexical_rank is not None
            },
            "technology_alignment": {
                "matched_technologies": matched_techs,
                "skill_technologies": skill.technologies
            },
            "knowledge_graph": {
                "category": cluster["category"],
                "concepts": cluster.get("concepts", []),
                "prerequisites_count": len(cluster["prerequisites"]),
                "complements_count": len(cluster["complements"])
            },
            "task_domains": task_analysis.domains,
            "task_intents": task_analysis.intents
        }

    def graph_query(
        self,
        query_type: str,
        identifier: str,
        max_hops: int = 1
    ) -> Dict[str, Any]:
        """Perform typed queries against the Knowledge Fabric.
        
        query_type options: 'cluster', 'neighbors', 'prerequisites', 'complements', 'technology', 'concept'.
        """
        q = query_type.lower().strip()
        if q == "cluster":
            return self.traverser.find_related_cluster(identifier)
        elif q == "prerequisites":
            return {
                "target": identifier,
                "prerequisites": self.traverser.find_skill_prerequisites(identifier)
            }
        elif q == "complements":
            return {
                "target": identifier,
                "complements": self.traverser.find_skill_complements(identifier)
            }
        elif q == "technology":
            return {
                "technology": identifier,
                "skills": self.traverser.find_skills_by_technology(identifier)
            }
        elif q == "concept":
            return {
                "concept": identifier,
                "skills": self.traverser.find_skills_by_concept(identifier)
            }
        else:
            neighbors = self.traverser.get_neighbors(identifier, max_hops=max_hops)
            return {
                "node": identifier,
                "neighbor_count": len(neighbors),
                "neighbors": neighbors
            }

    def graph_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        max_hops: int = 1
    ) -> Dict[str, Any]:
        """Traverse neighbors of a node with optional relationship filter."""
        rel = relationship_type.strip() if relationship_type else None
        neighbors = self.traverser.get_neighbors(node_id, relationship_type=rel, max_hops=max_hops)
        return {
            "node_id": node_id,
            "relationship_filter": rel,
            "max_hops": max_hops,
            "count": len(neighbors),
            "neighbors": neighbors
        }

    def list_project_profiles(self) -> List[Dict[str, Any]]:
        """Return all stored project architectural profiles in SQLite."""
        cur = self.repo.conn.cursor()
        cur.execute("SELECT project_path, profile_json, last_analyzed_at FROM project_profiles ORDER BY last_analyzed_at DESC")
        profiles = []
        for r in cur.fetchall():
            try:
                data = json.loads(r["profile_json"])
            except Exception:
                data = {}
            profiles.append({
                "project_path": r["project_path"],
                "last_analyzed_at": r["last_analyzed_at"],
                "languages": data.get("languages", []),
                "frameworks": data.get("frameworks", []),
                "databases": data.get("databases", []),
                "testing_frameworks": data.get("testing_frameworks", [])
            })
        return profiles

    def skillforge_health(self) -> Dict[str, Any]:
        """Comprehensive health check of registry, graph, indexes, and cache."""
        cur = self.repo.conn.cursor()
        
        # Check SQLite integrity
        cur.execute("PRAGMA integrity_check;")
        integrity = cur.fetchone()[0]
        
        # Check FTS5
        cur.execute("SELECT COUNT(*) as cnt FROM skill_fts;")
        fts_count = cur.fetchone()["cnt"]
        
        stats = self.repo.get_stats()
        graph_stats = self.repo.get_graph_stats()
        cache_stats = self.engine.cache.stats()
        
        return {
            "status": "healthy" if integrity == "ok" else "degraded",
            "sqlite_integrity": integrity,
            "total_skills": stats["total_skills"],
            "fts5_indexed_rows": fts_count,
            "graph": graph_stats,
            "cache": cache_stats,
            "database_path": str(self.repo.db_path)
        }


    def list_ecosystem_assets(self, asset_type: Optional[str] = None, scope: Optional[str] = None, surface: Optional[str] = None) -> List[Dict[str, Any]]:
        """List registered Antigravity ecosystem assets (rules, agents, plugins, MCP, hooks)."""
        return self.repo.list_ecosystem_assets(asset_type=asset_type, scope=scope, surface=surface)

    def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """Get complete details, bundled components, and evidence for an ecosystem asset."""
        asset = self.repo.get_ecosystem_asset(asset_id)
        if not asset:
            return {"error": f"Asset '{asset_id}' not found."}
        components = self.repo.get_ecosystem_components(asset_id)
        return {
            "asset": asset,
            "components": components
        }

    def recommend_project_setup(self, project_path: str = ".") -> Dict[str, Any]:
        """Recommend a complete Antigravity setup (skills, rules, agents, plugins, MCP, hooks) for a project."""
        from skillforge.ecosystem.recommender import EcosystemRecommender
        recommender = EcosystemRecommender(self.repo)
        return recommender.recommend_setup(project_path)

    def validate_ecosystem_asset(self, asset_id: str) -> Dict[str, Any]:
        """Validate an ecosystem asset against Antigravity 2.6 specification."""
        asset = self.repo.get_ecosystem_asset(asset_id)
        if not asset:
            return {"error": f"Asset '{asset_id}' not found."}
        return {
            "asset_id": asset_id,
            "name": asset["name"],
            "asset_type": asset["asset_type"],
            "validation_state": asset["validation_state"],
            "trust_state": asset["trust_state"],
            "compatibility_surfaces": asset["compatibility_surfaces"],
            "is_ide_compatible": "antigravity_ide" in asset["compatibility_surfaces"]
        }



    def slif_recommend_skills(self, task: str, project_path: Optional[str] = None, conversation_id: str = "", max_skills: int = 3) -> Dict[str, Any]:
        """Generate ranked candidate skills with human approval token and consent prompt."""
        from skillforge.approval.token_manager import ApprovalTokenManager
        recs = self.recommend_skills(task=task, project_path=project_path, max_skills=max_skills)
        recommended = recs.get("recommended_skills", [])
        if not recommended:
            return {
                "task": task,
                "needs_approval": False,
                "recommended_skills": [],
                "message": "No specialized skills required for this general task."
            }

        token_mgr = ApprovalTokenManager(self.repo.db_path)
        candidate_ids = [s["id"] for s in recommended]
        token = token_mgr.create_approval_request(
            task=task,
            candidate_ids=candidate_ids,
            conversation_id=conversation_id
        )

        skill_names = [s["name"] for s in recommended]
        names_str = ", ".join(f"'{n}'" for n in skill_names)

        return {
            "task": task,
            "needs_approval": True,
            "approval_token": token,
            "recommended_skills": recommended,
            "approval_prompt": f"To activate specialist skill(s) {names_str}, please reply with:\n- YES (to approve all)\n- SELECT <id/name> (to select specific skills)\n- NO (to decline and continue with standard capabilities)",
            "candidate_ids": candidate_ids,
            "expires_in_minutes": 15
        }


    def slif_approve_skills(
        self,
        approval_token: str,
        approved_skill_ids: List[str],
        conversation_id: str = "",
        turn_id: int = 1
    ) -> Dict[str, Any]:
        """Record explicit user approval ('YES' or 'SELECT <id>') for a candidate skill collection."""
        from skillforge.approval.token_manager import ApprovalTokenManager
        token_mgr = ApprovalTokenManager(self.repo.db_path)
        success, msg, valid_ids = token_mgr.approve_token(
            token=approval_token,
            approved_skill_ids=approved_skill_ids,
            conversation_id=conversation_id,
            turn_id=turn_id
        )
        return {
            "approval_token": approval_token,
            "approved": success,
            "message": msg,
            "authorized_skill_ids": valid_ids
        }

    def slif_load_approved_skills(self, approval_token: str, approved_skill_ids: List[str], conversation_id: str = "") -> Dict[str, Any]:
        """Load specialist skill instructions into context, strictly requiring an APPROVED token."""
        from skillforge.runtime.loader import ControlledSkillLoader
        loader = ControlledSkillLoader(self.repo)
        return loader.load_approved_collection(
            skill_identifiers=approved_skill_ids,
            approval_token=approval_token,
            conversation_id=conversation_id
        )

    def slif_decline_skills(self, approval_token: str, conversation_id: str = "") -> Dict[str, Any]:
        """Record human decline of recommended skills."""
        from skillforge.approval.token_manager import ApprovalTokenManager
        token_mgr = ApprovalTokenManager(self.repo.db_path)
        success = token_mgr.decline_request(approval_token, conversation_id=conversation_id)
        return {
            "approval_token": approval_token,
            "declined": success,
            "message": "Specialist skills declined. Antigravity will proceed using standard built-in capabilities."
        }

    def slif_cross_source_verify(self, statement: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify empirical or research statements against multi-tier evidence sources."""
        from skillforge.research.cross_verifier import CrossSourceVerifier
        verifier = CrossSourceVerifier(self.repo.db_path)
        return verifier.verify_statement(statement=statement, sources=sources)

    def slif_execute_script(
        self,
        skill_identifier: str,
        script_path: str,
        parameters: Optional[Dict[str, Any]] = None,
        granted_permissions: Optional[List[str]] = None,
        approval_token: str = "",
        conversation_id: str = "",
        dry_run: bool = False,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Execute a local skill script with permission controls, timeouts, secret redaction, and auditing."""
        from skillforge.runtime.executor import LocalSkillExecutor
        executor = LocalSkillExecutor(self.repo)
        return executor.execute_script(
            skill_identifier=skill_identifier,
            script_path=script_path,
            parameters=parameters,
            granted_permissions=granted_permissions,
            approval_token=approval_token,
            conversation_id=conversation_id,
            dry_run=dry_run,
            timeout=timeout
        )
