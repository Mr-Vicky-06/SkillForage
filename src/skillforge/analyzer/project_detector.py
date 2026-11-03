"""Project Context Analyzer and Technology Stack Detector."""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from skillforge.database.models import ProjectProfile


EXCLUDED_DIRS = {
    ".git", ".svn", ".hg", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", "target", "out", ".next", ".nuxt", ".turbo",
    "vendor", ".gemini", ".idea", ".vscode"
}

EXCLUDED_FILES = {
    ".env", ".env.local", ".env.production", ".env.development",
    "id_rsa", "id_ed25519", "credentials.json", "service_account.json",
    "keystore.jks"
}


class ProjectDetector:
    def analyze_workspace(self, workspace_path: str | Path) -> ProjectProfile:
        """Inspect a workspace directory and return a structured ProjectProfile.
        
        Read-only, strictly skips secrets, dependencies, and build directories.
        """
        root = Path(workspace_path).resolve()
        profile = ProjectProfile(project_path=str(root))

        if not root.is_dir():
            return profile

        languages: Set[str] = set()
        frameworks: Set[str] = set()
        package_managers: Set[str] = set()
        databases: Set[str] = set()
        ai_ml: Set[str] = set()
        infrastructure: Set[str] = set()
        build_tools: Set[str] = set()
        testing_frameworks: Set[str] = set()
        deployment: Set[str] = set()
        detected_files: List[str] = []

        # Shallow / bounded traversal: max depth 3
        for dirpath, dirnames, filenames in os.walk(root):
            # Prune excluded directories in-place
            dirnames[:] = [d for d in dirnames if d.lower() not in EXCLUDED_DIRS and not d.startswith(".")]

            rel_depth = len(Path(dirpath).relative_to(root).parts)
            if rel_depth > 3:
                continue

            for f in filenames:
                f_lower = f.lower()
                if f_lower in EXCLUDED_FILES or f_lower.endswith((".key", ".pem", ".pfx", ".cert", ".crt")):
                    continue

                full_path = Path(dirpath) / f
                rel_file = str(full_path.relative_to(root))

                # Language detection by extension
                if f_lower.endswith(".py"):
                    languages.add("python")
                elif f_lower.endswith((".ts", ".tsx")):
                    languages.add("typescript")
                elif f_lower.endswith((".js", ".jsx", ".mjs", ".cjs")):
                    languages.add("javascript")
                elif f_lower.endswith(".rs"):
                    languages.add("rust")
                elif f_lower.endswith(".go"):
                    languages.add("go")
                elif f_lower.endswith((".java", ".kt")):
                    languages.add("java" if f_lower.endswith(".java") else "kotlin")
                elif f_lower.endswith((".cpp", ".cc", ".cxx", ".h", ".hpp")):
                    languages.add("c++")
                elif f_lower.endswith(".sql"):
                    languages.add("sql")

                # Package manifest inspections
                if f_lower in ("pytest.ini", "conftest.py", "tox.ini"):
                    testing_frameworks.add("pytest")
                    detected_files.append(rel_file)
                elif f_lower in ("playwright.config.ts", "playwright.config.js"):
                    testing_frameworks.add("playwright")
                    detected_files.append(rel_file)
                elif f_lower in ("jest.config.js", "jest.config.ts"):
                    testing_frameworks.add("jest")
                    detected_files.append(rel_file)
                elif f_lower in ("vitest.config.ts", "vitest.config.js"):
                    testing_frameworks.add("vitest")
                    detected_files.append(rel_file)

                if f_lower == "package.json":
                    package_managers.add("npm")
                    detected_files.append(rel_file)
                    self._inspect_package_json(full_path, frameworks, testing_frameworks, build_tools)

                elif f_lower in ("pnpm-lock.yaml", "yarn.lock", "bun.lockb"):
                    if "pnpm" in f_lower:
                        package_managers.add("pnpm")
                    elif "yarn" in f_lower:
                        package_managers.add("yarn")
                    elif "bun" in f_lower:
                        package_managers.add("bun")
                    detected_files.append(rel_file)

                elif f_lower in ("pyproject.toml", "requirements.txt", "setup.py", "pipfile"):
                    package_managers.add("pip")
                    detected_files.append(rel_file)
                    self._inspect_python_manifest(full_path, frameworks, ai_ml, testing_frameworks, databases)

                elif f_lower == "uv.lock":
                    package_managers.add("uv")
                    detected_files.append(rel_file)

                elif f_lower == "cargo.toml":
                    package_managers.add("cargo")
                    languages.add("rust")
                    detected_files.append(rel_file)

                elif f_lower == "go.mod":
                    languages.add("go")
                    detected_files.append(rel_file)

                elif f_lower == "dockerfile" or f_lower.startswith("dockerfile."):
                    infrastructure.add("docker")
                    detected_files.append(rel_file)

                elif f_lower in ("docker-compose.yml", "docker-compose.yaml", "compose.yml"):
                    infrastructure.add("docker-compose")
                    detected_files.append(rel_file)

                elif f_lower.endswith((".tf", ".tfvars")):
                    infrastructure.add("terraform")
                    detected_files.append(rel_file)

                elif ".github" in dirpath.lower() and f_lower.endswith((".yml", ".yaml")):
                    infrastructure.add("github-actions")
                    detected_files.append(rel_file)

                # Android detection
                elif f_lower in ("androidmanifest.xml", "build.gradle", "build.gradle.kts"):
                    detected_files.append(rel_file)
                    try:
                        content_sample = full_path.read_text(encoding="utf-8", errors="replace")[:1000]
                        if "com.android" in content_sample or "android {" in content_sample:
                            frameworks.add("android")
                    except Exception:
                        pass

        profile.languages = sorted(list(languages))
        profile.frameworks = sorted(list(frameworks))
        profile.package_managers = sorted(list(package_managers))
        profile.databases = sorted(list(databases))
        profile.ai_ml = sorted(list(ai_ml))
        profile.infrastructure = sorted(list(infrastructure))
        profile.build_tools = sorted(list(build_tools))
        profile.testing_frameworks = sorted(list(testing_frameworks))
        profile.deployment = sorted(list(deployment))
        profile.detected_files = detected_files[:25]  # Limit to 25 items

        return profile

    def _inspect_package_json(
        self,
        path: Path,
        frameworks: Set[str],
        testing: Set[str],
        build_tools: Set[str]
    ) -> None:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            if "next" in deps:
                frameworks.add("next.js")
                frameworks.add("react")
            elif "react" in deps:
                frameworks.add("react")
            if "vue" in deps:
                frameworks.add("vue")
            if "svelte" in deps or "@sveltejs/kit" in deps:
                frameworks.add("svelte")
            if "express" in deps:
                frameworks.add("express")
            if "tailwindcss" in deps:
                frameworks.add("tailwind")
            if "@shadcn/ui" in deps or "shadcn" in deps:
                frameworks.add("shadcn")
            if "vite" in deps:
                build_tools.add("vite")
            if "webpack" in deps:
                build_tools.add("webpack")
            if "jest" in deps:
                testing.add("jest")
            if "vitest" in deps:
                testing.add("vitest")
            if "@playwright/test" in deps or "playwright" in deps:
                testing.add("playwright")
            if "cypress" in deps:
                testing.add("cypress")
        except Exception:
            pass

    def _inspect_python_manifest(
        self,
        path: Path,
        frameworks: Set[str],
        ai_ml: Set[str],
        testing: Set[str],
        databases: Set[str]
    ) -> None:
        try:
            text = path.read_text(encoding="utf-8", errors="replace").lower()

            # Frameworks
            if "fastapi" in text:
                frameworks.add("fastapi")
            if "flask" in text:
                frameworks.add("flask")
            if "django" in text:
                frameworks.add("django")

            # AI / ML
            if "langchain" in text:
                ai_ml.add("langchain")
            if "langgraph" in text:
                ai_ml.add("langgraph")
            if "llamaindex" in text:
                ai_ml.add("llamaindex")
            if "torch" in text or "pytorch" in text:
                ai_ml.add("pytorch")
            if "tensorflow" in text:
                ai_ml.add("tensorflow")
            if "transformers" in text or "huggingface" in text:
                ai_ml.add("huggingface")
            if "openai" in text:
                ai_ml.add("openai")
            if "google-generativeai" in text or "google-genai" in text:
                ai_ml.add("gemini")

            # Databases / Data engineering
            if "bigquery" in text or "google-cloud-bigquery" in text:
                databases.add("bigquery")
            if "pyspark" in text or "spark" in text:
                databases.add("pyspark")
            if "dbt" in text:
                databases.add("dbt")
            if "sqlalchemy" in text or "psycopg" in text or "asyncpg" in text:
                databases.add("postgres")

            # Testing
            if "pytest" in text:
                testing.add("pytest")
            if "playwright" in text:
                testing.add("playwright")
        except Exception:
            pass

