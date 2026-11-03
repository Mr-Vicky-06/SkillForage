"""Tests for Project Context Analyzer and Task Intent Classifier."""

import json
import tempfile
from pathlib import Path
from skillforge.analyzer.project_detector import ProjectDetector
from skillforge.analyzer.task_classifier import TaskClassifier


def test_project_detector_python_fastapi():
    detector = ProjectDetector()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pyproject.toml").write_text("""
[project]
dependencies = ["fastapi", "pytest", "sqlalchemy", "bigquery"]
""", encoding="utf-8")
        (root / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()", encoding="utf-8")

        profile = detector.analyze_workspace(root)
        assert "python" in profile.languages
        assert "fastapi" in profile.frameworks
        assert "pytest" in profile.testing_frameworks
        assert "bigquery" in profile.databases


def test_project_detector_node_nextjs():
    detector = ProjectDetector()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        pkg = {
            "dependencies": {
                "next": "14.0.0",
                "react": "18.2.0",
                "tailwindcss": "^3.3.0"
            },
            "devDependencies": {
                "vitest": "^1.0.0"
            }
        }
        (root / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
        (root / "app.tsx").write_text("export default function Page() {}", encoding="utf-8")

        profile = detector.analyze_workspace(root)
        assert "typescript" in profile.languages
        assert "next.js" in profile.frameworks
        assert "react" in profile.frameworks
        assert "tailwind" in profile.frameworks
        assert "vitest" in profile.testing_frameworks


def test_project_detector_strictly_excludes_secrets_and_node_modules():
    detector = ProjectDetector()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create sensitive files
        (root / ".env").write_text("SECRET_KEY=12345", encoding="utf-8")
        (root / "credentials.json").write_text('{"token": "xyz"}', encoding="utf-8")
        
        # Create node_modules and .venv
        nm = root / "node_modules"
        nm.mkdir()
        (nm / "package.json").write_text('{"name": "ignore-me"}', encoding="utf-8")
        
        venv = root / ".venv"
        venv.mkdir()
        (venv / "pyproject.toml").write_text('dependencies = ["ignore-me"]', encoding="utf-8")

        profile = detector.analyze_workspace(root)
        # Neither .env nor node_modules manifest should be in detected_files
        assert not any(".env" in f for f in profile.detected_files)
        assert not any("credentials" in f for f in profile.detected_files)
        assert not any("node_modules" in f for f in profile.detected_files)
        assert not any(".venv" in f for f in profile.detected_files)


def test_task_classifier_domains_and_intents():
    classifier = TaskClassifier()
    res = classifier.classify("Build a resilient LangGraph agent for RAG retrieval")
    assert "build" in res.intents
    assert "ai" in res.domains
    assert "agent" in res.extracted_terms
    assert "langgraph" in res.extracted_terms

