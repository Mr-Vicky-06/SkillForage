"""SkillForge Management CLI."""

import json
import os
import sys
from pathlib import Path
from typing import Optional
import click

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from skillforge.database.repository import SkillRepository
from skillforge.indexer.scanner import SkillScanner
from skillforge.retrieval.context_matcher import ContextMatcher
from skillforge.indexer.validator import SkillValidator
from skillforge.mcp_server.tools import SkillForgeTools


def get_default_repo() -> SkillRepository:
    base = Path(__file__).resolve().parent.parent.parent
    db_path = base / "data" / "registry.db"
    return SkillRepository(db_path)


@click.group()
def cli():
    """SkillForge: Local Intelligent Skill Library & Context-Aware Router."""
    pass


@cli.command()
@click.option("--json-out", is_flag=True, help="Output results as JSON.")
def status(json_out: bool):
    """Show database health, indexed counts, and source library status."""
    repo = get_default_repo()
    tools = SkillForgeTools(repo)
    res = tools.status()
    if json_out:
        click.echo(json.dumps(res, indent=2))
    else:
        stats = res["stats"]
        click.echo("========================================")
        click.echo(" SkillForge Local Skill Registry Status")
        click.echo("========================================")
        click.echo(f"Database: {res['database_path']}")
        click.echo(f"Total Skills Indexed: {stats['total_skills']}")
        click.echo(f"Last Indexed: {stats['last_index_time'] or 'Never'}")
        click.echo("\nBy Source:")
        for src, count in stats["by_source"].items():
            click.echo(f"  - {src}: {count}")
        click.echo("\nBy Trust Level:")
        for lvl, count in stats["by_trust_level"].items():
            click.echo(f"  - {lvl}: {count}")
        click.echo("\nTop Categories:")
        for cat, count in list(stats["by_category"].items())[:6]:
            click.echo(f"  - {cat}: {count}")


@cli.command()
@click.option("--force", is_flag=True, help="Force full re-index of all skills.")
def index(force: bool):
    """Scan and index local skill libraries incrementally."""
    repo = get_default_repo()
    scanner = SkillScanner(repo)

    click.echo(f"Scanning skill libraries ({'full re-index' if force else 'incremental'})...")

    def progress(name, current, total):
        sys.stdout.write(f"\rIndexing: {current}/{total} skills...")
        sys.stdout.flush()

    stats = scanner.scan_all(force_reindex=force, progress_cb=progress)
    click.echo("\nIndex scan completed successfully!")
    click.echo(f"  Discovered: {stats['discovered']}")
    click.echo(f"  Indexed/Updated: {stats['indexed']}")
    click.echo(f"  Skipped (unchanged): {stats['skipped_unchanged']}")
    click.echo(f"  Broken metadata: {stats['broken']}")
    click.echo(f"  Quarantined: {stats['quarantined']}")


@cli.command()
def reindex():
    """Force complete re-indexing of all offline, global, and plugin skills."""
    repo = get_default_repo()
    scanner = SkillScanner(repo)
    click.echo("Running full clean re-index...")

    def progress(name, current, total):
        sys.stdout.write(f"\rRe-indexing: {current}/{total} skills...")
        sys.stdout.flush()

    stats = scanner.scan_all(force_reindex=True, progress_cb=progress)
    click.echo("\nFull re-index completed successfully!")
    click.echo(f"  Total Indexed: {stats['indexed']}")


@cli.command("list")
@click.option("--category", default=None, help="Filter by category.")
@click.option("--source", default=None, help="Filter by source type.")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--limit", default=30, help="Max items to display.")
@click.option("--json-out", is_flag=True, help="Output as JSON.")
def list_cmd(category, source, status, limit, json_out):
    """List skills stored in the registry."""
    repo = get_default_repo()
    tools = SkillForgeTools(repo)
    res = tools.list_skills(category=category, source_type=source, status=status, limit=limit)
    if json_out:
        click.echo(json.dumps(res, indent=2))
    else:
        click.echo(f"Displaying {len(res['skills'])} skills:")
        for s in res["skills"]:
            badge = "[INSTALLED]" if "installed" in s["source_type"] else "[OFFLINE]"
            click.echo(f"  {badge} {s['name']:<30} [{s['category']}] (Score: {s['quality_score']}, Trust: {s['trust_level']})")


@cli.command()
@click.argument("query")
@click.option("--limit", default=10, help="Max results to display.")
@click.option("--json-out", is_flag=True, help="Output as JSON.")
def search(query: str, limit: int, json_out: bool):
    """Search skills by keyword, category, or task description."""
    repo = get_default_repo()
    tools = SkillForgeTools(repo)
    results = tools.search_skills(query, limit=limit)
    if json_out:
        click.echo(json.dumps(results, indent=2))
    else:
        click.echo(f"Search results for '{query}':")
        if not results:
            click.echo("  No matching skills found.")
        for r in results:
            click.echo(f"\n  • {r['name']} ({r['source_type']}) - Score: {r['score']}")
            click.echo(f"    Category: {r['category']}")
            click.echo(f"    Desc: {r['description']}")


@cli.command()
@click.option("--task", required=True, help="User task description.")
@click.option("--project", default=None, help="Project directory to analyze.")
@click.option("--max-skills", default=3, help="Max recommendations.")
@click.option("--json-out", is_flag=True, help="Output as JSON.")
def recommend(task: str, project: Optional[str], max_skills: int, json_out: bool):
    """Recommend context-aware skills based on task and project architecture."""
    repo = get_default_repo()
    tools = SkillForgeTools(repo)
    res = tools.recommend_skills(task=task, project_path=project, max_skills=max_skills)
    if json_out:
        click.echo(json.dumps(res, indent=2))
    else:
        click.echo(res["explanation"])


@cli.command()
@click.argument("skill_name")
def show(skill_name: str):
    """Show detailed instructions and metadata for a skill."""
    repo = get_default_repo()
    tools = SkillForgeTools(repo)
    res = tools.load_skill(skill_name)
    if "error" in res:
        click.echo(f"Error: {res['error']}", err=True)
    else:
        click.echo("========================================")
        click.echo(f" Skill: {res['skill_name']} [{res['category']}]")
        click.echo(f" Source: {res['source_type']} | Hash: {res['file_hash'][:12]}...")
        click.echo(f" Quality Score: {res['quality_score']}")
        if res["warnings"]:
            click.echo(f" Warnings: {', '.join(res['warnings'])}")
        click.echo("========================================\n")
        click.echo(res["content"])


@cli.command()
@click.argument("skill_name")
def validate(skill_name: str):
    """Validate structure, frontmatter, and prerequisites for a skill."""
    repo = get_default_repo()
    tools = SkillForgeTools(repo)
    res = tools.validate_skill(skill_name)
    if "error" in res:
        click.echo(f"Error: {res['error']}", err=True)
    else:
        click.echo(f"Skill: {res['skill_name']}")
        click.echo(f"Valid: {res['is_valid']}")
        click.echo(f"Trust Level: {res['trust_level']}")
        click.echo(f"Quality Score: {res['quality_score']}")
        if res["messages"]:
            click.echo("Messages:")
            for m in res["messages"]:
                click.echo(f"  - {m}")


@cli.command()
def doctor():
    """Run diagnostic checks on SkillForge installation and environment."""
    click.echo("========================================")
    click.echo(" SkillForge System Diagnostics")
    click.echo("========================================")

    # 1. Check Python
    click.echo(f"[PASS] Python Runtime: {sys.version.split()[0]}")

    # 2. Check Database
    repo = get_default_repo()
    stats = repo.get_stats()
    click.echo(f"[PASS] SQLite Database: {repo.db_path} ({stats['total_skills']} indexed)")

    # 3. Check Universal Skill Book
    usb_path = Path(r"D:\setup\vignesh-universal-skill-book")
    if usb_path.is_dir():
        click.echo(f"[PASS] Universal Skill Book: Found at {usb_path}")
    else:
        click.echo(f"[WARN] Universal Skill Book not found at {usb_path}")

    # 4. Check Antigravity Global Skills
    global_skills = Path(os.path.expandvars(r"%USERPROFILE%\.gemini\config\skills"))
    if global_skills.is_dir():
        click.echo(f"[PASS] Global Antigravity Skills: Found ({len(list(global_skills.iterdir()))} items)")
    else:
        click.echo(f"[WARN] Global Antigravity skills directory not found at {global_skills}")

    # 5. Check Global MCP Config
    mcp_config = Path(os.path.expandvars(r"%USERPROFILE%\.gemini\config\mcp_config.json"))
    if mcp_config.is_file():
        try:
            with open(mcp_config, "r", encoding="utf-8") as f:
                data = json.load(f)
            has_sf = "skillforge" in data.get("mcpServers", {})
            click.echo(f"[PASS] Antigravity MCP Config: Valid JSON ({len(data.get('mcpServers', {}))} servers, SkillForge registered: {has_sf})")
        except Exception as e:
            click.echo(f"[FAIL] Antigravity MCP Config: Error reading JSON: {e}")
    else:
        click.echo(f"[WARN] Antigravity MCP Config file not found at {mcp_config}")

    # 6. Check Router Skill
    router_skill = global_skills / "skill-library-router" / "SKILL.md"
    if router_skill.is_file():
        click.echo(f"[PASS] SkillForge Router Skill: Installed at {router_skill}")
    else:
        click.echo(f"[WARN] SkillForge Router Skill: Not yet installed in global skills")

    click.echo("\nAll essential diagnostics completed.")


@cli.command()
@click.option("--output", default="reports/INVENTORY.md", help="Output path for markdown report.")
def report(output: str):
    """Generate comprehensive inventory and audit report."""
    repo = get_default_repo()
    stats = repo.get_stats()

    base = Path(__file__).resolve().parent.parent.parent
    out_path = base / output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# SkillForge Master Library Inventory & Audit Report",
        "",
        f"**Generated:** {stats['last_index_time'] or 'Live'}",
        f"**Total Indexed Skills:** {stats['total_skills']}",
        "",
        "## Summary by Source",
        "",
        "| Source | Count |",
        "|---|---:|",
    ]
    for src, cnt in stats["by_source"].items():
        lines.append(f"| {src} | {cnt} |")

    lines.extend([
        "",
        "## Summary by Category",
        "",
        "| Category | Count |",
        "|---|---:|",
    ])
    for cat, cnt in stats["by_category"].items():
        lines.append(f"| {cat} | {cnt} |")

    lines.extend([
        "",
        "## Summary by Trust Level",
        "",
        "| Trust Level | Count |",
        "|---|---:|",
    ])
    for lvl, cnt in stats["by_trust_level"].items():
        lines.append(f"| {lvl} | {cnt} |")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    click.echo(f"Report written to: {out_path}")


@cli.command("serve-dashboard")
@click.option("--host", default="127.0.0.1", help="Host interface (local only).")
@click.option("--port", default=8765, help="Port number.")
def serve_dashboard(host: str, port: int):
    """Launch lightweight local SkillForge web dashboard."""
    from skillforge.dashboard.app import start_dashboard
    start_dashboard(host=host, port=port)


def main():
    cli()


if __name__ == "__main__":
    main()
