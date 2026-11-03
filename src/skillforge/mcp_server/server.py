"""SkillForge MCP Server using the Official Python MCP SDK."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer

from skillforge.database.repository import SkillRepository
from skillforge.mcp_server.tools import SkillForgeTools


def create_mcp_server(db_path: Optional[str] = None) -> MCPServer:
    """Create and configure the SkillForge MCP Server."""
    if db_path is None:
        db_path = os.environ.get("SKILLFORGE_DB_PATH", "data/registry.db")

    # If relative path, resolve relative to SkillForge root
    p = Path(db_path)
    if not p.is_absolute():
        p = Path(__file__).resolve().parent.parent.parent.parent / p

    repo = SkillRepository(p)
    tools = SkillForgeTools(repo)

    server = MCPServer(
        name="skillforge",
        title="SkillForge Local Intelligent Skill Registry",
        description="Just-in-time context-aware Agent Skill retrieval and execution registry for Google Antigravity"
    )

    @server.tool(name="skillforge_status", description="Get health, indexed skill counts, source library status, and indexing timestamp.")
    def skillforge_status() -> Dict[str, Any]:
        return tools.status()

    @server.tool(name="search_skills", description="Search skills by keyword, domain, technology, or task description (returns compact metadata).")
    def search_skills(query: str, limit: int = 15) -> List[Dict[str, Any]]:
        return tools.search_skills(query=query, limit=limit)

    @server.tool(name="analyze_project", description="Inspect project files and manifests to detect languages, frameworks, databases, and build tools.")
    def analyze_project(project_path: str) -> Dict[str, Any]:
        return tools.analyze_project(project_path=project_path)

    @server.tool(name="recommend_skills", description="Retrieve context-aware, ranked Agent Skills matching a specific task and project architecture with explanations.")
    def recommend_skills(task: str, project_path: str = "", max_skills: int = 3) -> Dict[str, Any]:
        p = project_path.strip() if project_path else None
        return tools.recommend_skills(task=task, project_path=p, max_skills=max_skills)

    @server.tool(name="load_skill", description="Load full SKILL.md instructions and metadata for a selected skill into the current agent context.")
    def load_skill(skill_name_or_id: str) -> Dict[str, Any]:
        return tools.load_skill(skill_name_or_id=skill_name_or_id)

    @server.tool(name="read_skill_resource", description="Read an explicitly referenced resource, template, or documentation file belonging to a loaded skill.")
    def read_skill_resource(skill_name_or_id: str, relative_path: str) -> Dict[str, Any]:
        return tools.read_skill_resource(skill_name_or_id=skill_name_or_id, relative_path=relative_path)

    @server.tool(name="list_skills", description="List indexed skills with category, source, and status filters.")
    def list_skills(
        category: str = "",
        source_type: str = "",
        status: str = "",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        c = category.strip() if category else None
        st = source_type.strip() if source_type else None
        s = status.strip() if status else None
        return tools.list_skills(category=c, source_type=st, status=s, limit=limit, offset=offset)

    @server.tool(name="validate_skill", description="Validate a skill's structural integrity, frontmatter, and prerequisite tools.")
    def validate_skill(skill_name_or_id: str) -> Dict[str, Any]:
        return tools.validate_skill(skill_name_or_id=skill_name_or_id)

    @server.tool(name="record_skill_feedback", description="Record feedback on whether a loaded skill was helpful, irrelevant, duplicated, or incompatible.")
    def record_skill_feedback(
        skill_name_or_id: str,
        rating: int,
        feedback_type: str,
        comment: str = "",
        task_context: str = ""
    ) -> Dict[str, Any]:
        return tools.record_skill_feedback(
            skill_name_or_id=skill_name_or_id,
            rating=rating,
            feedback_type=feedback_type,
            comment=comment,
            task_context=task_context
        )

    @server.tool(name="explain_recommendation", description="Explain the ranking signals, graph distance, and technology match for a recommended skill.")
    def explain_recommendation(skill_name_or_id: str, task: str, project_path: str = "") -> Dict[str, Any]:
        p = project_path.strip() if project_path else None
        return tools.explain_recommendation(skill_name_or_id=skill_name_or_id, task=task, project_path=p)

    @server.tool(name="graph_query", description="Query Knowledge Fabric: 'cluster', 'prerequisites', 'complements', 'technology', 'concept', or 'neighbors'.")
    def graph_query(query_type: str, identifier: str, max_hops: int = 1) -> Dict[str, Any]:
        return tools.graph_query(query_type=query_type, identifier=identifier, max_hops=max_hops)

    @server.tool(name="graph_neighbors", description="Traverse 1-hop or multi-hop graph neighbors of a skill, technology, or concept.")
    def graph_neighbors(node_id: str, relationship_type: str = "", max_hops: int = 1) -> Dict[str, Any]:
        rel = relationship_type.strip() if relationship_type else None
        return tools.graph_neighbors(node_id=node_id, relationship_type=rel, max_hops=max_hops)

    @server.tool(name="list_project_profiles", description="List all analyzed project architectural profiles stored in SkillForge.")
    def list_project_profiles() -> List[Dict[str, Any]]:
        return tools.list_project_profiles()

    @server.tool(name="skillforge_health", description="Run comprehensive diagnostic health check on SQLite, indexes, graph nodes, and retrieval cache.")
    def skillforge_health() -> Dict[str, Any]:
        return tools.skillforge_health()

    
    @server.tool(name="list_ecosystem_assets", description="List Antigravity ecosystem assets (rules, agents, plugins, MCP servers, hooks, manifests).")
    def list_ecosystem_assets(asset_type: str = "", scope: str = "", surface: str = "") -> List[Dict[str, Any]]:
        t = asset_type.strip() if asset_type else None
        s = scope.strip() if scope else None
        surf = surface.strip() if surface else None
        return tools.list_ecosystem_assets(asset_type=t, scope=s, surface=surf)

    @server.tool(name="get_asset_details", description="Get complete details, metadata, and bundled components for an ecosystem asset.")
    def get_asset_details(asset_id: str) -> Dict[str, Any]:
        return tools.get_asset_details(asset_id=asset_id)

    @server.tool(name="recommend_project_setup", description="Recommend complete Antigravity setup (skills, rules, agents, plugins, MCP, hooks) for a project.")
    def recommend_project_setup(project_path: str = ".") -> Dict[str, Any]:
        return tools.recommend_project_setup(project_path=project_path)

    @server.tool(name="validate_ecosystem_asset", description="Validate an ecosystem asset against official Antigravity 2.6 specifications.")
    def validate_ecosystem_asset(asset_id: str) -> Dict[str, Any]:
        return tools.validate_ecosystem_asset(asset_id=asset_id)

    return server


def main():
    """Run the MCP Server over stdio."""
    server = create_mcp_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

