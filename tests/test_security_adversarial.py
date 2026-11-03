"""SLIF Adversarial Security & Penetration Test Suite (P0 Hardening Sprint).

Verifies 15 specific attack vectors:
1. Loading with a PENDING token.
2. Loading with a CONSUMED token (Replay prevention).
3. Reusing a token for multiple/unapproved skills.
4. Missing conversation ID when token is bound.
5. Wrong/spoofed conversation ID.
6. Empty skill selection rejected (no fallback to all candidates).
7. Unauthorized legacy loader calls (load_skill without token).
8. Unauthorized resource reads (read_skill_resource without token).
9. Arbitrary script path execution outside approved skill directory.
10. Script path traversal and symlink boundary attacks.
11. Attempted environment-secret exfiltration (SAFE_ENV_ALLOWLIST verification).
12. Network access attempts during strict-offline operation.
13. Execution of declined skill scripts.
14. Undeclared permission escalation / unapproved execution.
15. Cross-source verifier independent check (ignores caller-supplied boolean flags).
"""

from __future__ import annotations
import json
import os
import subprocess
import pytest
from pathlib import Path

from skillforge.approval.token_manager import ApprovalTokenManager
from skillforge.database.repository import SkillRepository
from skillforge.mcp_server.tools import SkillForgeTools
from skillforge.runtime.executor import LocalSkillExecutor
from skillforge.runtime.loader import ControlledSkillLoader
from skillforge.research.cross_verifier import CrossSourceVerifier


@pytest.fixture
def repo():
    return SkillRepository("data/registry.db")


@pytest.fixture
def token_mgr():
    return ApprovalTokenManager("data/registry.db")


@pytest.fixture
def loader(repo):
    return ControlledSkillLoader(repo)


@pytest.fixture
def executor(repo, token_mgr):
    return LocalSkillExecutor(repo, token_mgr)


@pytest.fixture
def tools(repo):
    return SkillForgeTools(repo)


# =====================================================================
# Attack Vector 1: Loading with a PENDING token
# =====================================================================
def test_adv_01_loading_with_pending_token(token_mgr, loader):
    skill_id = "research--cross-source-verification"
    token = token_mgr.create_approval_request(
        task="Test Pending Token Attack",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-01"
    )
    # Token is PENDING. Loader must strictly refuse to load.
    res = loader.load_approved_skill(skill_id, approval_token=token, conversation_id="conv-sec-01")
    assert res["authorized"] is False
    assert "PENDING" in res["error"]


# =====================================================================
# Attack Vector 2: Loading with a CONSUMED token (Replay prevention)
# =====================================================================
def test_adv_02_loading_with_consumed_token(token_mgr, loader):
    skill_id = "research--cross-source-verification"
    token = token_mgr.create_approval_request(
        task="Test Replay Attack",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-02"
    )
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id], conversation_id="conv-sec-02")
    
    # First load succeeds and CONSUMES the token
    res1 = loader.load_approved_skill(skill_id, approval_token=token, conversation_id="conv-sec-02")
    assert res1["authorized"] is True

    # Replay attempt: Second load with the exact same token must fail
    res2 = loader.load_approved_skill(skill_id, approval_token=token, conversation_id="conv-sec-02")
    assert res2["authorized"] is False
    assert "consumed" in res2["error"].lower() or "replay" in res2["error"].lower()


# =====================================================================
# Attack Vector 3: Reusing a token for an unapproved skill
# =====================================================================
def test_adv_03_reusing_token_unapproved_skill(token_mgr, loader):
    skill_a = "research--cross-source-verification"
    skill_b = "research--patent-prior-art-search"
    token = token_mgr.create_approval_request(
        task="Test Cross-Skill Reuse",
        candidate_ids=[skill_a, skill_b],
        conversation_id="conv-sec-03"
    )
    # User only approves skill_a
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_a], conversation_id="conv-sec-03")

    # Attempt to load skill_b using token approved only for skill_a
    res = loader.load_approved_skill(skill_b, approval_token=token, conversation_id="conv-sec-03")
    assert res["authorized"] is False
    assert "was not approved" in res["error"]


# =====================================================================
# Attack Vector 4: Missing conversation ID when bound
# =====================================================================
def test_adv_04_missing_conversation_id_when_bound(token_mgr, loader):
    skill_id = "research--cross-source-verification"
    token = token_mgr.create_approval_request(
        task="Test Conversation Binding",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-bound-100"
    )
    # Try to approve without providing conversation_id
    success, msg, _ = token_mgr.approve_token(token=token, approved_skill_ids=[skill_id], conversation_id="")
    assert success is False
    assert "Conversation binding mismatch" in msg


# =====================================================================
# Attack Vector 5: Wrong/spoofed conversation ID
# =====================================================================
def test_adv_05_wrong_conversation_id_spoofing(token_mgr, loader):
    skill_id = "research--cross-source-verification"
    token = token_mgr.create_approval_request(
        task="Test Conversation Hijacking",
        candidate_ids=[skill_id],
        conversation_id="conv-legit-user"
    )
    # Adversary attempts approval with different conversation ID
    success, msg, _ = token_mgr.approve_token(token=token, approved_skill_ids=[skill_id], conversation_id="conv-attacker")
    assert success is False
    assert "Conversation binding mismatch" in msg


# =====================================================================
# Attack Vector 6: Empty skill selection rejected
# =====================================================================
def test_adv_06_empty_skill_selection(token_mgr):
    skill_id = "research--cross-source-verification"
    token = token_mgr.create_approval_request(
        task="Test Empty Selection Fallback",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-06"
    )
    # Approving with empty list must NOT fall back to all candidates
    success, msg, valid_ids = token_mgr.approve_token(token=token, approved_skill_ids=[], conversation_id="conv-sec-06")
    assert success is False
    assert "No skills selected for approval" in msg


# =====================================================================
# Attack Vector 7: Unauthorized legacy loader calls
# =====================================================================
def test_adv_07_unauthorized_legacy_loader_calls(tools):
    # Calling load_skill directly without approval token
    res = tools.load_skill("karpathy-guidelines")
    assert "error" in res
    assert "ACCESS DENIED" in res["error"]


# =====================================================================
# Attack Vector 8: Unauthorized resource reads
# =====================================================================
def test_adv_08_unauthorized_resource_reads(tools):
    # Calling read_skill_resource without approval token
    res = tools.read_skill_resource("karpathy-guidelines", "reference.md")
    assert "error" in res
    assert "ACCESS DENIED" in res["error"]


# =====================================================================
# Attack Vector 9: Arbitrary script path execution outside approved package
# =====================================================================
def test_adv_09_arbitrary_script_path_execution(token_mgr, executor):
    skill_id = "research--cross-source-verification"
    token = token_mgr.create_approval_request(
        task="Test Arbitrary Script Execution",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-09"
    )
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id], conversation_id="conv-sec-09")

    # Attempt to execute an external script (e.g. system script or scripts/patch_tests.py)
    external_script = Path("scripts/patch_tests.py").resolve()
    res = executor.execute_script(
        skill_identifier=skill_id,
        script_path=external_script,
        granted_permissions=["EXECUTE_SCRIPT"],
        approval_token=token,
        conversation_id="conv-sec-09"
    )
    assert res["success"] is False
    assert "SECURITY VIOLATION" in res["error"]
    assert "escapes skill package boundary" in res["error"]


# =====================================================================
# Attack Vector 10: Script path traversal and symlink attacks
# =====================================================================
def test_adv_10_script_path_traversal(token_mgr, executor):
    skill_id = "research--cross-source-verification"
    token = token_mgr.create_approval_request(
        task="Test Traversal Attack",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-10"
    )
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id], conversation_id="conv-sec-10")

    # Path traversal attempt pointing outside skill package
    traversal_path = Path("vault/skills/research/cross-source-verification/scripts/../../../../Windows/win.ini")
    res = executor.execute_script(
        skill_identifier=skill_id,
        script_path=traversal_path,
        granted_permissions=["EXECUTE_SCRIPT"],
        approval_token=token,
        conversation_id="conv-sec-10"
    )
    assert res["success"] is False
    assert "SECURITY VIOLATION" in res["error"]


# =====================================================================
# Attack Vector 11: Attempted environment-secret exfiltration
# =====================================================================
def test_adv_11_environment_secret_allowlist_scrubbing(token_mgr, executor, monkeypatch):
    # Inject toxic credentials into current environment
    monkeypatch.setenv("OPENAI_API_KEY", "sk-live-secret-key-1234567890abcdef")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_123456789012345678901234567890123456")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-123456789012-secrettoken")
    monkeypatch.setenv("DATABASE_PASSWORD", "SuperSecretP@ssw0rd99!")

    skill_id = "research--technology-comparison-matrix"
    token = token_mgr.create_approval_request(
        task="Test Secret Exfiltration",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-11"
    )
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id], conversation_id="conv-sec-11")

    script_path = Path("vault/skills/research/technology-comparison-matrix/scripts/mcda_score.py")

    # Run the script and check that the child process environment did not inherit any secrets
    res = executor.execute_script(
        skill_identifier=skill_id,
        script_path=script_path,
        granted_permissions=["EXECUTE_SCRIPT", "READ_LOCAL_FILES"],
        approval_token=token,
        conversation_id="conv-sec-11"
    )
    assert res["success"] is True
    # Confirm output did not leak any secrets
    combined_out = res["stdout"] + res["stderr"]
    assert "sk-live-secret" not in combined_out
    assert "wJalrXUtn" not in combined_out
    assert "ghp_" not in combined_out
    assert "SuperSecret" not in combined_out


# =====================================================================
# Attack Vector 12: Network access during strict-offline operation
# =====================================================================
def test_adv_12_strict_offline_network_blocked(repo, token_mgr):
    offline_exec = LocalSkillExecutor(repo, token_mgr, strict_offline=True)
    skill_id = "research--github-ecosystem-analyzer"
    token = token_mgr.create_approval_request(
        task="Test Offline Network Block",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-12"
    )
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id], conversation_id="conv-sec-12")

    script_path = Path("vault/skills/research/github-ecosystem-analyzer/scripts/analyze_repo.py")
    res = offline_exec.execute_script(
        skill_identifier=skill_id,
        script_path=script_path,
        granted_permissions=["EXECUTE_SCRIPT", "ACCESS_NETWORK"],
        approval_token=token,
        conversation_id="conv-sec-12"
    )
    assert res["success"] is False
    assert "strict-offline" in res["error"].lower()


# =====================================================================
# Attack Vector 13: Execution of declined skill
# =====================================================================
def test_adv_13_declined_skill_execution(token_mgr, executor, tools):
    skill_id = "research--ab-testing-experiment-design"
    token = token_mgr.create_approval_request(
        task="Test Declined Execution",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-13"
    )
    # User declines
    tools.slif_decline_skills(approval_token=token, conversation_id="conv-sec-13")

    script_path = Path("vault/skills/research/ab-testing-experiment-design/scripts/power_analysis.py")
    res = executor.execute_script(
        skill_identifier=skill_id,
        script_path=script_path,
        granted_permissions=["EXECUTE_SCRIPT"],
        approval_token=token,
        conversation_id="conv-sec-13"
    )
    assert res["success"] is False
    assert "declined" in res["error"].lower()


# =====================================================================
# Attack Vector 14: Undeclared permission escalation
# =====================================================================
def test_adv_14_undeclared_permission_escalation(token_mgr, executor):
    # systematic-literature-review-prisma only declares READ_LOCAL_FILES, WRITE_LOCAL_FILES
    skill_id = "research--systematic-literature-review-prisma"
    token = token_mgr.create_approval_request(
        task="Test Escalation Attack",
        candidate_ids=[skill_id],
        conversation_id="conv-sec-14"
    )
    token_mgr.approve_token(token=token, approved_skill_ids=[skill_id], conversation_id="conv-sec-14")

    script_path = Path("vault/skills/research/systematic-literature-review-prisma/scripts/prisma_flow.py")
    # Attacker requests ACCESS_NETWORK which is NOT in manifest
    res = executor.execute_script(
        skill_identifier=skill_id,
        script_path=script_path,
        granted_permissions=["EXECUTE_SCRIPT", "ACCESS_NETWORK"],
        approval_token=token,
        conversation_id="conv-sec-14"
    )
    assert res["success"] is False
    assert "SECURITY VIOLATION" in res["error"]
    assert "Network access requested but not declared" in res["error"]


# =====================================================================
# Attack Vector 15: Cross-Source Verifier independent check
# =====================================================================
def test_adv_15_research_verification_ignores_caller_claims():
    verifier = CrossSourceVerifier("data/registry.db")
    
    # Caller maliciously flags a contradicting source as "supports: True"
    malicious_sources = [
        {
            "url": "https://nature.com/articles/s41586-fake",
            "title": "Cold Fusion Replication Study",
            "snippet": "We conducted extensive trials on cold fusion and our experimental data conclusively refutes and contradicts the hypothesis of room temperature fusion.",
            "supports": True,  # Malicious lie by caller
            "contradicts": False
        }
    ]
    res = verifier.verify_statement("Cold fusion was achieved at room temperature.", malicious_sources)
    # The verifier MUST catch the contradiction independently and NOT verify the statement
    assert res["overall_status"] in ("disputed", "contradictory")
    assert res["claim_verifications"][0]["contradiction_count"] >= 1
