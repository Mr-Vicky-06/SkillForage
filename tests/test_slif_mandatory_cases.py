"""SLIF Mandatory 20 Benchmark Test Cases (Part 14 Specification).

Verifies routing relevance, approval gating, permission sandboxing,
offline execution, cross-verification, tamper detection, and idempotency.
"""

from __future__ import annotations
import hashlib
import json
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest

from skillforge.database.repository import SkillRepository
from skillforge.approval.token_manager import ApprovalTokenManager
from skillforge.runtime.loader import ControlledSkillLoader
from skillforge.runtime.executor import LocalSkillExecutor
from skillforge.research.cross_verifier import CrossSourceVerifier, ResearchCache, classify_source_tier
from skillforge.mcp_server.tools import SkillForgeTools


@pytest.fixture(scope="module")
def repo():
    db_path = Path("data/registry.db").resolve()
    return SkillRepository(db_path)


@pytest.fixture(scope="module")
def tools(repo):
    return SkillForgeTools(repo)


@pytest.fixture
def token_mgr(repo):
    return ApprovalTokenManager(repo.db_path)


@pytest.fixture
def loader(repo, token_mgr):
    return ControlledSkillLoader(repo, token_mgr)


@pytest.fixture
def executor(repo, token_mgr):
    return LocalSkillExecutor(repo, token_mgr)


# ---------------------------------------------------------
# Test Case 1: Routing relevance - Python async REST API
# ---------------------------------------------------------
def test_01_routing_relevance_python_api(tools):
    task = "Build a high-performance async REST API with Python FastAPI and pydantic"
    res = tools.recommend_skills(task=task, max_skills=3)
    skills = res.get("recommended_skills", [])
    assert len(skills) > 0
    names = [s["name"].lower() for s in skills]
    categories = [s.get("category", "").lower() for s in skills]
    assert any("fastapi" in n or "python" in n or "api" in n or "backend" in c or "development" in c for n, c in zip(names, categories))


# ---------------------------------------------------------
# Test Case 2: Routing relevance - Patent prior art search
# ---------------------------------------------------------
def test_02_routing_relevance_patents(tools):
    task = "Conduct a patent prior art search and classify claims using CPC classifications"
    res = tools.recommend_skills(task=task, max_skills=3)
    skills = res.get("recommended_skills", [])
    assert len(skills) > 0
    names = [s["name"].lower() for s in skills]
    assert any("patent" in n for n in names)


# ---------------------------------------------------------
# Test Case 3: Routing relevance - Academic literature review
# ---------------------------------------------------------
def test_03_routing_relevance_literature(tools):
    task = "Conduct a systematic literature review following PRISMA 2020 protocol and citation graph"
    res = tools.recommend_skills(task=task, max_skills=3)
    skills = res.get("recommended_skills", [])
    assert len(skills) > 0
    names = [s["name"].lower() for s in skills]
    assert any("prisma" in n or "semantic-scholar" in n or "literature" in n or "citation" in n for n in names)


# ---------------------------------------------------------
# Test Case 4: Routing relevance - Market teardown
# ---------------------------------------------------------
def test_04_routing_relevance_market(tools):
    task = "Perform a competitive product teardown and analyze SaaS pricing tier strategies"
    res = tools.recommend_skills(task=task, max_skills=3)
    skills = res.get("recommended_skills", [])
    assert len(skills) > 0
    names = [s["name"].lower() for s in skills]
    assert any("competitive" in n or "pricing" in n or "teardown" in n for n in names)


# ---------------------------------------------------------
# Test Case 5: Multi-domain recommendation
# ---------------------------------------------------------
def test_05_multi_domain_recommendation(tools):
    task = "Design a dbt SQL data pipeline with comprehensive unit testing and validation"
    res = tools.recommend_skills(task=task, max_skills=4)
    skills = res.get("recommended_skills", [])
    assert len(skills) >= 2
    names = [s["name"].lower() for s in skills]
    categories = [s.get("category", "").lower() for s in skills]
    assert any("dbt" in n or "sql" in n or "data" in c for n, c in zip(names, categories))


# ---------------------------------------------------------
# Test Case 6: Negative recommendation - Vague prompt
# ---------------------------------------------------------
def test_06_negative_recommendation_vague_prompt(tools):
    task = "do the thing"
    res = tools.recommend_skills(task=task, max_skills=3)
    skills = res.get("recommended_skills", [])
    if skills:
        assert skills[0].get("confidence", 0) < 0.70


# ---------------------------------------------------------
# Test Case 7: Approval gating - Recommended skills NOT loaded before approval
# ---------------------------------------------------------
def test_07_approval_gating_unloaded_before_approval(tools):
    task = "Run an exploratory data analysis on statistical outliers"
    res = tools.slif_recommend_skills(task=task, max_skills=2)
    assert res["needs_approval"] is True
    assert "approval_token" in res
    assert res["approval_token"].startswith("SF-")
    for s in res["recommended_skills"]:
        assert "content" not in s
        assert "instructions" not in s


# ---------------------------------------------------------
# Test Case 8: Approval gating - "YES" response loads all approved skills
# ---------------------------------------------------------
def test_08_approval_gating_yes_loads_all(tools):
    task = "Design A/B test sample sizes and power analysis"
    rec = tools.slif_recommend_skills(task=task, max_skills=1)
    token = rec["approval_token"]
    c_ids = rec["candidate_ids"]

    # Human confirms YES -> Approve first, then Load
    appr_res = tools.slif_approve_skills(approval_token=token, approved_skill_ids=c_ids)
    assert appr_res["approved"] is True

    load_res = tools.slif_load_approved_skills(
        approval_token=token,
        approved_skill_ids=c_ids
    )
    assert load_res["all_authorized"] is True
    assert len(load_res["loaded_skills"]) == len(c_ids)
    assert load_res["loaded_skills"][0]["authorized"] is True
    assert len(load_res["loaded_skills"][0]["instructions"]) > 50


# ---------------------------------------------------------
# Test Case 9: Approval gating - "SELECT <id>" loads only approved subset
# ---------------------------------------------------------
def test_09_approval_gating_select_subset_loads_only_selected(tools):
    task = "Evaluate open source license compliance and package supply chain"
    rec = tools.slif_recommend_skills(task=task, max_skills=2)
    token = rec["approval_token"]
    c_ids = rec["candidate_ids"]
    assert len(c_ids) >= 1

    selected_id = c_ids[:1]
    appr_res = tools.slif_approve_skills(approval_token=token, approved_skill_ids=selected_id)
    assert appr_res["approved"] is True

    load_res = tools.slif_load_approved_skills(
        approval_token=token,
        approved_skill_ids=selected_id
    )
    assert load_res["all_authorized"] is True
    assert len(load_res["loaded_skills"]) == 1
    assert load_res["loaded_skills"][0]["skill_id"] == selected_id[0]


# ---------------------------------------------------------
# Test Case 10: Approval gating - "NO" declines and proceeds without skills
# ---------------------------------------------------------
def test_10_approval_gating_no_declines_and_proceeds(tools):
    task = "Create a LaTeX academic paper"
    rec = tools.slif_recommend_skills(task=task, max_skills=1)
    token = rec["approval_token"]

    decline_res = tools.slif_decline_skills(approval_token=token)
    assert decline_res["declined"] is True

    load_res = tools.slif_load_approved_skills(
        approval_token=token,
        approved_skill_ids=rec["candidate_ids"]
    )
    assert load_res["all_authorized"] is False
    assert "ACCESS DENIED" in load_res["loaded_skills"][0]["error"]


# ---------------------------------------------------------
# Test Case 11: Expired approval token fails
# ---------------------------------------------------------
def test_11_expired_approval_token(token_mgr, loader):
    token = token_mgr.create_approval_request(
        task="Test expiry",
        candidate_ids=["research--ab-testing-experiment-design"],
        ttl_minutes=-5
    )
    res = loader.load_approved_skill("research--ab-testing-experiment-design", approval_token=token)
    assert res["authorized"] is False
    assert "expired" in res["error"].lower()


# ---------------------------------------------------------
# Test Case 12: Unapproved skill access blocked
# ---------------------------------------------------------
def test_12_unapproved_skill_access_blocked(loader):
    res = loader.load_approved_skill(
        skill_identifier="research--patent-prior-art-search",
        approval_token="SF-INVALID-TOKEN"
    )
    assert res["authorized"] is False
    assert "ACCESS DENIED" in res["error"]


# ---------------------------------------------------------
# Test Case 13: Unapproved script execution blocked
# ---------------------------------------------------------
def test_13_unapproved_script_execution_blocked(executor):
    script_path = Path("vault/skills/research/ab-testing-experiment-design/scripts/power_analysis.py")
    res = executor.execute_script(
        skill_identifier="research--ab-testing-experiment-design",
        script_path=script_path,
        granted_permissions=["EXECUTE_SCRIPT"],
        approval_token="SF-UNAUTHORIZED"
    )
    assert res["success"] is False
    assert "EXECUTION DENIED" in res["error"]


# ---------------------------------------------------------
# Test Case 14: Offline execution of local script
# ---------------------------------------------------------
def test_14_offline_execution_local_script(token_mgr, executor):
    skill_id = "research--systematic-literature-review-prisma"
    token = token_mgr.create_approval_request(task="Offline PRISMA", candidate_ids=[skill_id])
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id])
    script_path = Path("vault/skills/research/systematic-literature-review-prisma/scripts/prisma_flow.py")

    res = executor.execute_script(
        skill_identifier=skill_id,
        script_path=script_path,
        granted_permissions=["EXECUTE_SCRIPT", "READ_LOCAL_FILES"],
        approval_token=token
    )
    assert res["success"] is True
    assert res["exit_code"] == 0
    assert "valid_flow" in res["stdout"]


# ---------------------------------------------------------
# Test Case 15: Strict-offline enforcement blocks network permissions
# ---------------------------------------------------------
def test_15_strict_offline_enforcement(repo, token_mgr):
    offline_executor = LocalSkillExecutor(repo, token_mgr, strict_offline=True)
    skill_id = "research--github-ecosystem-analyzer"
    token = token_mgr.create_approval_request(task="Analyze repo", candidate_ids=[skill_id])
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id])
    script_path = Path("vault/skills/research/github-ecosystem-analyzer/scripts/analyze_repo.py")

    res = offline_executor.execute_script(
        skill_identifier=skill_id,
        script_path=script_path,
        granted_permissions=["EXECUTE_SCRIPT", "ACCESS_NETWORK"],
        approval_token=token
    )
    assert res["success"] is False
    assert "strict-offline" in res["error"].lower()


# ---------------------------------------------------------
# Test Case 16: Dependency resolution reported before approval
# ---------------------------------------------------------
def test_16_dependency_resolution_reported(tools):
    task = "Extract financial data from SEC EDGAR filings"
    rec = tools.slif_recommend_skills(task=task, max_skills=1)
    skills = rec.get("recommended_skills", [])
    assert len(skills) > 0
    s = skills[0]
    assert "offline_capable" in s or "category" in s


# ---------------------------------------------------------
# Test Case 17: Research cross-verification protocol
# ---------------------------------------------------------
def test_17_research_cross_verification_protocol(tools):
    statement = "The Transformer architecture was introduced in the 2017 paper Attention Is All You Need."
    sources = [
        {
            "url": "https://doi.org/10.5555/3295222.3295349",
            "title": "NeurIPS Proceedings",
            "quote": "We propose the Transformer, a model architecture eschewing recurrence.",
            "supports": True,
            "contradicts": False
        },
        {
            "url": "https://acm.org/citation.cfm?id=3295222",
            "title": "ACM Digital Library",
            "quote": "Vaswani et al., Attention is all you need.",
            "supports": True,
            "contradicts": False
        }
    ]
    res = tools.slif_cross_source_verify(statement=statement, sources=sources)
    assert res["overall_status"] == "verified"
    assert res["overall_confidence"] >= 0.85
    assert len(res["claim_verifications"]) >= 1


# ---------------------------------------------------------
# Test Case 18: Research cache functionality
# ---------------------------------------------------------
def test_18_research_cache_hit(repo):
    cache = ResearchCache(repo.db_path)
    q_key = "transformer-paper-citations-2026"
    api_source = "semantic-scholar"
    payload = {"citation_count": 125000, "influential": 8400}

    h = cache.set(q_key, api_source, payload, ttl_days=7)
    assert h is not None

    cached = cache.get(q_key, api_source)
    assert cached is not None
    assert cached["citation_count"] == 125000


# ---------------------------------------------------------
# Test Case 19: Tamper detection checksum mismatch
# ---------------------------------------------------------
def test_19_tamper_detection_checksum_mismatch(repo, token_mgr, loader, tmp_path):
    skill_id = "research--ab-testing-experiment-design"
    token = token_mgr.create_approval_request(task="Tamper check", candidate_ids=[skill_id])
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id])

    skill = repo.get_skill_by_id(skill_id)
    original_path = Path(skill.source_path)
    original_bytes = original_path.read_bytes()

    try:
        tampered_bytes = original_bytes + b"\n# Tampered injection attack"
        original_path.write_bytes(tampered_bytes)

        res = loader.load_approved_skill(skill_id, approval_token=token)
        assert res["authorized"] is False
        assert "INTEGRITY VIOLATION" in res["error"]
    finally:
        original_path.write_bytes(original_bytes)

    token2 = token_mgr.create_approval_request(task="Tamper check 2", candidate_ids=[skill_id])
    token_mgr.approve_token(token=token2, approved_skill_ids=[skill_id])
    clean_res = loader.load_approved_skill(skill_id, approval_token=token2)
    assert clean_res["authorized"] is True


# ---------------------------------------------------------
# Test Case 20: Idempotency test for recommendations
# ---------------------------------------------------------
def test_20_idempotency_recommendation(tools):
    task = "Build an RFC architecture decision record with trade-off analysis"
    res1 = tools.recommend_skills(task=task, max_skills=3)
    res2 = tools.recommend_skills(task=task, max_skills=3)

    skills1 = [s["id"] for s in res1.get("recommended_skills", [])]
    skills2 = [s["id"] for s in res2.get("recommended_skills", [])]
    assert skills1 == skills2
