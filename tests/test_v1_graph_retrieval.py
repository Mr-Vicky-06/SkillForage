"""Comprehensive Tests for SkillForge V1 Knowledge Fabric and Hybrid Retrieval."""

import pytest
from pathlib import Path
from skillforge.database.repository import SkillRepository
from skillforge.graph.builder import KnowledgeGraphBuilder
from skillforge.graph.traversal import GraphTraverser
from skillforge.retrieval.cache import QueryCache
from skillforge.retrieval.fusion import ReciprocalRankFusion
from skillforge.retrieval.engine import HybridRetrievalEngine, RetrievalMode
from skillforge.mcp_server.tools import SkillForgeTools


@pytest.fixture
def repo():
    db_path = Path(__file__).resolve().parent.parent / "data" / "registry.db"
    return SkillRepository(db_path)


def test_query_cache():
    cache = QueryCache(max_size=5, ttl_seconds=2.0)
    cache.put("python api", {"result": "ok"})
    assert cache.get("python api") == {"result": "ok"}
    assert cache.get("missing") is None
    
    stats = cache.stats()
    assert stats["cached_entries"] == 1
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_reciprocal_rank_fusion():
    rrf = ReciprocalRankFusion(k=60.0)
    channels = {
        "lexical": [("skill_a", 0.9), ("skill_b", 0.8)],
        "graph": [("skill_b", 1.0), ("skill_c", 0.7)],
        "tech": [("skill_a", 0.95)]
    }
    fused = rrf.fuse(channels)
    assert len(fused) == 3
    # Top item should be skill_a or skill_b
    top_ids = [item["skill_id"] for item in fused]
    assert "skill_a" in top_ids[:2]
    assert "skill_b" in top_ids[:2]
    assert fused[0]["normalized_score"] == 1.0


def test_knowledge_graph_traversal(repo):
    traverser = GraphTraverser(repo)
    cluster = traverser.find_related_cluster("clean-code")
    assert cluster["category"] != ""
    assert "technologies" in cluster
    assert "concepts" in cluster


def test_hybrid_retrieval_engine(repo):
    engine = HybridRetrievalEngine(repo)
    
    # 1. Balanced mode
    res = engine.retrieve("clean code architecture and refactoring", mode=RetrievalMode.BALANCED, limit=3)
    assert res["count"] > 0
    assert len(res["results"]) <= 3
    assert "rrf_score" in res["results"][0]
    
    # 2. Warm query cache hit
    res_cached = engine.retrieve("clean code architecture and refactoring", mode=RetrievalMode.BALANCED, limit=3)
    assert res_cached["cache_hit"] is True
    assert res_cached["duration_ms"] < 2.0

    # 3. Bootstrap mode
    boot = engine.retrieve("bootstrap project", mode=RetrievalMode.BOOTSTRAP, limit=5)
    assert boot["count"] >= 3
    assert any(r["role"] == "architecture" for r in boot["results"])


def test_new_mcp_tools(repo):
    tools = SkillForgeTools(repo)
    
    # Health check
    health = tools.skillforge_health()
    assert health["status"] == "healthy"
    assert health["total_skills"] >= 800
    assert health["graph"]["total_nodes"] > 500
    
    # Explain recommendation
    exp = tools.explain_recommendation("clean-code", task="refactoring legacy python code")
    assert "skill_id" in exp
    assert "lexical" in exp
    assert "knowledge_graph" in exp
    
    # Graph query
    g_res = tools.graph_query("concept", "clean-code")
    assert "concept" in g_res or "skills" in g_res or "node" in g_res
    
    # List project profiles
    profiles = tools.list_project_profiles()
    assert isinstance(profiles, list)
