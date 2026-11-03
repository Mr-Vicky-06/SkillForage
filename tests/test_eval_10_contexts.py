"""Evaluation Suite for SkillForge across the 10 Required Project Contexts."""

import json
import tempfile
from pathlib import Path
import pytest

from skillforge.database.repository import SkillRepository
from skillforge.retrieval.context_matcher import ContextMatcher


TEST_BENCHMARK = [
    {
        "id": "ctx-1",
        "name": "Python backend/API application",
        "task": "Build a Python FastAPI REST API service with validation and endpoints",
        "manifest": {"filename": "pyproject.toml", "content": 'dependencies = ["fastapi", "pytest", "pydantic"]'},
        "acceptable_skills": ["fastapi", "python-engineer", "api-and-interface-design", "backend-architecture", "fastapi-templates", "fastapi-router-py"]
    },
    {
        "id": "ctx-2",
        "name": "React/Next.js frontend application",
        "task": "Develop a responsive React Next.js user interface with Tailwind CSS",
        "manifest": {"filename": "package.json", "content": '{"dependencies": {"react": "^18.0", "next": "^14.0", "tailwindcss": "^3.0"}}'},
        "acceptable_skills": ["nextjs", "react", "frontend-ui-engineering", "ui-ux-pro-max", "frontend-engineer", "ui-styling", "tailwind", "fp-ts-react"]
    },
    {
        "id": "ctx-3",
        "name": "AI agent and LangGraph application",
        "task": "Build an autonomous AI agent with LangGraph StateGraph and tool execution",
        "manifest": {"filename": "pyproject.toml", "content": 'dependencies = ["langgraph", "langchain", "openai"]'},
        "acceptable_skills": ["langgraph", "autonomous-agents", "ai-agent-architect", "agent-memory-systems", "google-antigravity-sdk", "langchain"]
    },
    {
        "id": "ctx-4",
        "name": "RAG application",
        "task": "Implement a Retrieval-Augmented Generation RAG system with vector database",
        "manifest": {"filename": "pyproject.toml", "content": 'dependencies = ["chromadb", "langchain", "tiktoken"]'},
        "acceptable_skills": ["rag-implementation", "rag", "rag-engineer", "embeddings", "vector-database", "agent-memory-systems", "langchain"]
    },
    {
        "id": "ctx-5",
        "name": "Machine learning project",
        "task": "Train and evaluate a machine learning model using PyTorch neural networks",
        "manifest": {"filename": "requirements.txt", "content": "torch\ntorchvision\nscikit-learn\npandas"},
        "acceptable_skills": ["ml-best-practices", "data-ml-engineer", "pytorch", "neural", "machine-learning", "ml-engineer", "data-scientist", "machine-learning-ops-ml-pipeline"]
    },
    {
        "id": "ctx-6",
        "name": "Data engineering and analytics project",
        "task": "Build a BigQuery data transformation pipeline with dbt SQL models",
        "manifest": {"filename": "dbt_project.yml", "content": "name: my_pipeline\nprofile: bigquery"},
        "acceptable_skills": ["bigquery-sql", "dbt-bigquery", "dataform-bigquery", "gcp-data-pipelines", "data-autocleaning", "dbt-transformation-patterns", "dbt"]
    },
    {
        "id": "ctx-7",
        "name": "Android application",
        "task": "Develop an Android mobile app with Jetpack Compose and Kotlin",
        "manifest": {"filename": "build.gradle", "content": "plugins { id 'com.android.application' }\nandroid { }"},
        "acceptable_skills": ["android-cli", "android-device-hub", "compose-preview", "android", "mobile-app-design", "mobile-developer", "mobile"]
    },
    {
        "id": "ctx-8",
        "name": "DevOps and infrastructure project",
        "task": "Create Docker container configuration and CI/CD automated pipeline",
        "manifest": {"filename": "Dockerfile", "content": "FROM python:3.12-slim\nWORKDIR /app"},
        "acceptable_skills": ["ci-cd-and-automation", "docker", "devops", "kubernetes", "shipping-and-launch", "docker-expert"]
    },
    {
        "id": "ctx-9",
        "name": "Security assessment of an authorized application",
        "task": "Reverse engineer and inspect application binary for security vulnerabilities",
        "manifest": {"filename": "pyproject.toml", "content": "dependencies = []"},
        "acceptable_skills": ["reverse-engineer-anything", "reverse-engineer", "security-and-hardening", "security-reviewer", "security-auditor", "security-scanning", "top-web-vulnerabilities"]
    },
    {
        "id": "ctx-10",
        "name": "Documentation and architecture task",
        "task": "Write Architecture Decision Records ADR and document software system architecture",
        "manifest": {"filename": "README.md", "content": "# System Architecture"},
        "acceptable_skills": ["documentation-and-adrs", "software-architect", "architecture", "spec-driven-development", "architecture-decision-records"]
    }
]


def test_10_contexts_retrieval_benchmark():
    db_path = Path(__file__).resolve().parent.parent / "data" / "registry.db"
    repo = SkillRepository(db_path)
    matcher = ContextMatcher(repo)

    top_1_matches = 0
    top_3_matches = 0
    total = len(TEST_BENCHMARK)

    results_report = []

    for item in TEST_BENCHMARK:
        with tempfile.TemporaryDirectory() as tmpdir:
            proj = Path(tmpdir)
            (proj / item["manifest"]["filename"]).write_text(item["manifest"]["content"], encoding="utf-8")

            selected, explanation, profile = matcher.match(
                task=item["task"],
                project_path=str(proj),
                max_skills=3,
                force_refresh_profile=True
            )

            assert len(selected) > 0, f"No skill returned for context: {item['name']}"

            selected_names = [s.skill_name.lower() for s in selected]
            top_1_name = selected_names[0]

            is_top_1 = any(acc.lower() in top_1_name or top_1_name in acc.lower() for acc in item["acceptable_skills"])
            is_top_3 = any(
                any(acc.lower() in s_name or s_name in acc.lower() for acc in item["acceptable_skills"])
                for s_name in selected_names
            )

            if is_top_1:
                top_1_matches += 1
            if is_top_3:
                top_3_matches += 1

            results_report.append({
                "context": item["name"],
                "task": item["task"],
                "selected_top_3": selected_names,
                "top_1_hit": is_top_1,
                "top_3_hit": is_top_3
            })

    top_1_acc = (top_1_matches / total) * 100
    top_3_acc = (top_3_matches / total) * 100

    print(f"\n========================================================")
    print(f" SkillForge 10-Context Retrieval Benchmark Results")
    print(f" Top-1 Accuracy: {top_1_acc:.1f}% ({top_1_matches}/{total})")
    print(f" Top-3 Accuracy: {top_3_acc:.1f}% ({top_3_matches}/{total})")
    print(f"========================================================")
    for r in results_report:
        status_sym = "[PASS]" if r["top_3_hit"] else "[FAIL]"
        print(f"{status_sym} {r['context']}: {r['selected_top_3']}")

    assert top_3_acc >= 90.0, f"Expected at least 90% Top-3 accuracy, got {top_3_acc}%"
    assert top_1_acc >= 70.0, f"Expected at least 70% Top-1 accuracy, got {top_1_acc}%"
