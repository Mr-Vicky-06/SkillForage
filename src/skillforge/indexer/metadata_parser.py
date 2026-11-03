"""Robust YAML Frontmatter and Metadata Parser for Agent Skills."""

import hashlib
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

from skillforge.database.models import (
    SkillDependency,
    SkillRecord,
    SkillStatus,
    SourceType,
    TrustLevel,
)
from skillforge.security.content_audit import ContentAuditor


COMMON_TECHNOLOGIES = [
    "python", "typescript", "javascript", "rust", "go", "golang", "c++", "c#", "java", "kotlin",
    "react", "next.js", "nextjs", "vue", "svelte", "angular", "node", "nodejs",
    "fastapi", "flask", "django", "express", "tailwind", "shadcn",
    "langchain", "langgraph", "llamaindex", "autogen", "crewai", "openai", "gemini", "anthropic",
    "pytorch", "tensorflow", "scikit-learn", "huggingface", "keras",
    "bigquery", "snowflake", "postgres", "postgresql", "mysql", "sqlite", "mongodb", "redis",
    "spark", "pyspark", "dbt", "dataform", "kafka", "airflow",
    "docker", "kubernetes", "k8s", "terraform", "ansible", "aws", "gcp", "azure",
    "playwright", "puppeteer", "selenium", "jest", "pytest", "cypress",
    "android", "ios", "react-native", "flutter"
]


class MetadataParser:
    def __init__(self):
        self.auditor = ContentAuditor()

    def parse_skill_file(
        self,
        skill_file_path: str | Path,
        source_type: SourceType,
        category: str,
        subcategory: str = "",
        relative_path: str = ""
    ) -> Optional[SkillRecord]:
        """Parse a SKILL.md file into a SkillRecord."""
        path = Path(skill_file_path).resolve()
        if not path.is_file():
            return None

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

        # Compute hash and mtime
        file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        mtime = path.stat().st_mtime

        # Extract frontmatter and body
        frontmatter, body = self._extract_frontmatter(content)

        # Name and description
        skill_dir = path.parent
        dir_name = skill_dir.name

        name = str(frontmatter.get("name") or dir_name).strip()
        description = str(frontmatter.get("description") or "").strip()

        # If description is missing from frontmatter, inspect first body paragraph
        if not description:
            description = self._extract_fallback_description(body)

        # Version and author
        version = str(frontmatter.get("version") or "1.0.0").strip()
        author = str(frontmatter.get("author") or "").strip()

        # Extract tags, triggers, technologies
        tags = self._extract_tags(frontmatter, body)
        triggers = self._extract_triggers(frontmatter, body)
        technologies = self._extract_technologies(frontmatter, body, name, description)

        # Referenced files check
        referenced_files, missing_files = self._check_referenced_files(skill_dir, body)

        # Extract dependencies
        dependencies = self._extract_dependencies(frontmatter, body)

        # Security and quality audit
        trust_level, quality_score, security_flags = self.auditor.audit_skill_content(
            content=content,
            name=name,
            description=description,
            missing_files=missing_files
        )

        # Check status
        status = SkillStatus.ACTIVE
        if "deprecated" in name.lower() or "deprecated" in description.lower() or frontmatter.get("deprecated"):
            status = SkillStatus.DEPRECATED
        elif trust_level == TrustLevel.QUARANTINED:
            status = SkillStatus.QUARANTINED
        elif not name or not description:
            status = SkillStatus.BROKEN

        skill_id = f"{source_type.value}:{category}:{name.lower()}"

        return SkillRecord(
            id=skill_id,
            name=name,
            description=description,
            category=category,
            subcategory=subcategory,
            source_type=source_type,
            source_path=str(path),
            relative_path=relative_path or str(path.relative_to(path.parent.parent)),
            file_hash=file_hash,
            mtime=mtime,
            status=status,
            trust_level=trust_level,
            quality_score=quality_score,
            author=author,
            version=version,
            tags=sorted(list(tags)),
            triggers=sorted(list(triggers)),
            technologies=sorted(list(technologies)),
            dependencies=dependencies,
            referenced_files=referenced_files,
            missing_files=missing_files,
            security_flags=security_flags,
            raw_frontmatter=frontmatter
        )

    def _extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter between --- fences with robust fallback."""
        frontmatter: Dict[str, Any] = {}
        body = content

        pattern = r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            fm_text = match.group(1)
            body = match.group(2)
            try:
                parsed = yaml.safe_load(fm_text)
                if isinstance(parsed, dict):
                    frontmatter = parsed
            except Exception:
                # Regex fallback for key: value
                for line in fm_text.splitlines():
                    kv = line.split(":", 1)
                    if len(kv) == 2:
                        k = kv[0].strip()
                        v = kv[1].strip().strip('"\'')
                        if k and v:
                            frontmatter[k] = v

        return frontmatter, body

    def _extract_fallback_description(self, body: str) -> str:
        """Extract the first meaningful paragraph as description if frontmatter omitted it."""
        paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
        for p in paragraphs:
            # Skip headers
            if p.startswith("#"):
                continue
            # Clean markdown bold/links
            cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", p)
            cleaned = re.sub(r"[*_`]", "", cleaned)
            if len(cleaned) > 20:
                return cleaned[:300]
        return ""

    def _extract_tags(self, frontmatter: Dict[str, Any], body: str) -> Set[str]:
        tags = set()
        raw_tags = frontmatter.get("tags") or frontmatter.get("keywords") or []
        if isinstance(raw_tags, list):
            for t in raw_tags:
                if isinstance(t, str) and t.strip():
                    tags.add(t.strip().lower())
        elif isinstance(raw_tags, str):
            for t in raw_tags.split(","):
                if t.strip():
                    tags.add(t.strip().lower())
        return tags

    def _extract_triggers(self, frontmatter: Dict[str, Any], body: str) -> Set[str]:
        triggers = set()
        raw_triggers = frontmatter.get("triggers") or frontmatter.get("triggers_on") or []
        if isinstance(raw_triggers, list):
            for tr in raw_triggers:
                if isinstance(tr, str) and tr.strip():
                    triggers.add(tr.strip().lower())

        # Extract "Use when: ..." patterns from text
        matches = re.findall(r"(?:Use when|When to use|Trigger on|Activate for)[:\s]+([^\n\.]+)", body, re.IGNORECASE)
        for m in matches:
            for phrase in m.split(","):
                p = phrase.strip().lower()
                if len(p) > 3 and len(p) < 80:
                    triggers.add(p)

        return triggers

    def _extract_technologies(
        self,
        frontmatter: Dict[str, Any],
        body: str,
        name: str,
        description: str
    ) -> Set[str]:
        techs = set()
        text_lower = f"{name} {description} {body[:2000]}".lower()

        # Frontmatter technologies/stacks
        raw_tech = frontmatter.get("technologies") or frontmatter.get("stacks") or []
        if isinstance(raw_tech, list):
            for t in raw_tech:
                if isinstance(t, str):
                    techs.add(t.strip().lower())

        for ct in COMMON_TECHNOLOGIES:
            # Word boundary search
            pattern = r"\b" + re.escape(ct) + r"\b"
            if re.search(pattern, text_lower):
                techs.add(ct)

        return techs

    def _check_referenced_files(self, skill_dir: Path, body: str) -> Tuple[List[str], List[str]]:
        """Identify referenced resource/reference files in markdown and verify existence."""
        referenced: List[str] = []
        missing: List[str] = []

        # Find relative path mentions like references/xxx.md or resources/xxx.md
        matches = re.findall(r"(?:references|resources|scripts|templates)/[a-zA-Z0-9_\-\.\/]+", body)
        for rel in set(matches):
            clean_rel = rel.strip("`'\"()[],.")
            referenced.append(clean_rel)
            target = skill_dir / clean_rel
            if not target.exists():
                missing.append(clean_rel)

        return referenced, missing

    def _extract_dependencies(self, frontmatter: Dict[str, Any], body: str) -> List[SkillDependency]:
        deps: List[SkillDependency] = []
        raw_deps = frontmatter.get("dependencies") or frontmatter.get("prerequisites") or []

        if isinstance(raw_deps, list):
            for d in raw_deps:
                if isinstance(d, str):
                    deps.append(SkillDependency(dependency_type="general", name=d.strip()))
                elif isinstance(d, dict):
                    deps.append(SkillDependency(
                        dependency_type=d.get("type", "general"),
                        name=d.get("name", "unknown"),
                        details=d.get("details", "")
                    ))

        # Check for command prerequisites mentioned in text (e.g. requires uv, requires node)
        for tool in ["uv", "node", "npm", "python", "git", "docker", "pnpm", "bun"]:
            if re.search(r"requires\s+" + tool, body, re.IGNORECASE):
                deps.append(SkillDependency(dependency_type="binary", name=tool))

        return deps

