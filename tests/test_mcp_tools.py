"""Tests for All 9 MCP Tool Endpoints."""

from pathlib import Path
from skillforge.database.repository import SkillRepository
from skillforge.mcp_server.tools import SkillForgeTools


def get_test_tools():
    db_path = Path(__file__).resolve().parent.parent / "data" / "registry.db"
    repo = SkillRepository(db_path)
    return SkillForgeTools(repo)


def test_tool_status():
    tools = get_test_tools()
    res = tools.status()
    assert res["status"] == "online"
    assert "stats" in res
    assert res["stats"]["total_skills"] > 0


def test_tool_search_skills():
    tools = get_test_tools()
    res = tools.search_skills("python", limit=5)
    assert isinstance(res, list)
    assert len(res) > 0
    assert "name" in res[0]
    assert "category" in res[0]


def test_tool_analyze_project():
    tools = get_test_tools()
    res = tools.analyze_project(str(Path(__file__).resolve().parent.parent))
    assert "project_path" in res
    assert "python" in res["languages"]


def test_tool_recommend_skills():
    tools = get_test_tools()
    res = tools.recommend_skills(task="Build a Next.js React frontend with Tailwind CSS", max_skills=3)
    assert res["selected_count"] > 0
    assert "explanation" in res
    assert len(res["recommendations"]) <= 3


def test_tool_load_skill():
    tools = get_test_tools()
    # 1. Unapproved load must be denied
    unappr_res = tools.load_skill("karpathy-guidelines")
    assert "error" in unappr_res
    assert "ACCESS DENIED" in unappr_res["error"]

    # 2. Approved load must succeed
    from skillforge.approval.token_manager import ApprovalTokenManager
    mgr = ApprovalTokenManager(tools.repo.db_path)
    tok = mgr.create_approval_request("Load Karpathy", ["karpathy-guidelines"])
    mgr.approve_token(tok, ["karpathy-guidelines"])

    res = tools.load_skill("karpathy-guidelines", approval_token=tok)
    assert "error" not in res
    assert res["name"] == "karpathy-guidelines"
    assert "Simplicity First" in res["instructions"] or "Think Before Coding" in res["instructions"]


def test_tool_list_skills():
    tools = get_test_tools()
    res = tools.list_skills(category="ai", limit=10)
    assert "skills" in res
    assert res["total_returned"] > 0


def test_tool_validate_skill():
    tools = get_test_tools()
    res = tools.validate_skill("karpathy-guidelines")
    assert res["is_valid"] is True
    assert res["quality_score"] > 0.5


def test_tool_record_feedback():
    tools = get_test_tools()
    res = tools.record_skill_feedback(
        skill_name_or_id="karpathy-guidelines",
        rating=1,
        feedback_type="helpful",
        comment="Very concise and effective rules"
    )
    assert res["status"] == "success"
    assert res["recorded_rating"] == 1


def test_tool_read_resource_path_traversal():
    tools = get_test_tools()
    # 1. Unapproved call denied
    unappr = tools.read_skill_resource("karpathy-guidelines", "../../Windows/win.ini")
    assert "ACCESS DENIED" in unappr.get("error", "")

    # 2. Approved call blocked by PathGuard
    from skillforge.approval.token_manager import ApprovalTokenManager
    mgr = ApprovalTokenManager(tools.repo.db_path)
    tok = mgr.create_approval_request("Read resource", ["karpathy-guidelines"])
    mgr.approve_token(tok, ["karpathy-guidelines"])

    res = tools.read_skill_resource("karpathy-guidelines", "../../Windows/win.ini", approval_token=tok)
    assert "error" in res
    assert "Security Violation" in res["error"] or "outside" in res["error"]

