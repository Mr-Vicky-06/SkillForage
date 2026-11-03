"""Skill Discovery and Incremental Scanning Engine."""

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

from skillforge.database.models import SkillRecord, SkillStatus, SourceType
from skillforge.database.repository import SkillRepository
from skillforge.indexer.deduplication import DeduplicationEngine
from skillforge.indexer.metadata_parser import MetadataParser
from skillforge.indexer.validator import SkillValidator


class SkillScanner:
    def __init__(self, repository: SkillRepository):
        self.repo = repository
        self.parser = MetadataParser()
        self.validator = SkillValidator()
        self.dedup = DeduplicationEngine()

    def scan_all(
        self,
        usb_path: str = r"D:\setup\vignesh-universal-skill-book",
        global_skills_path: Optional[str] = None,
        plugins_path: Optional[str] = None,
        project_skills_path: Optional[str] = None,
        builtin_skills_path: Optional[str] = None,
        force_reindex: bool = False,
        progress_cb: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, int]:
        """Scan all skill sources incrementally and index them into SQLite."""
        if global_skills_path is None:
            global_skills_path = os.path.expandvars(r"%USERPROFILE%\.gemini\config\skills")
        if plugins_path is None:
            plugins_path = os.path.expandvars(r"%USERPROFILE%\.gemini\config\plugins")
        if builtin_skills_path is None:
            builtin_skills_path = os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity\builtin\skills")
        if project_skills_path is None and os.path.isdir(r"D:\setup\.agents\skills"):
            project_skills_path = r"D:\setup\.agents\skills"

        all_records: List[SkillRecord] = []
        stats = {
            "discovered": 0,
            "indexed": 0,
            "skipped_unchanged": 0,
            "broken": 0,
            "quarantined": 0,
        }

        # Collect candidate skill paths: list of (skill_file_path, source_type, category, subcat, rel_path)
        candidates = []

        # 1. Offline Universal Skill Book
        usb_dir = Path(usb_path)
        if usb_dir.is_dir():
            skills_sub = usb_dir / "skills"
            search_root = skills_sub if skills_sub.is_dir() else usb_dir
            for dirpath, dirnames, filenames in os.walk(search_root):
                if "SKILL.md" in filenames:
                    skill_file = Path(dirpath) / "SKILL.md"
                    rel = Path(dirpath).relative_to(search_root)
                    parts = rel.parts
                    cat = parts[0] if len(parts) > 0 else "general"
                    subcat = parts[1] if len(parts) > 2 else ""
                    rel_p = f"skills/{'/'.join(parts)}/SKILL.md"
                    candidates.append((
                        skill_file,
                        SourceType.OFFLINE_BOOK,
                        cat,
                        subcat,
                        rel_p
                    ))

        # 2. Global Antigravity Skills
        g_dir = Path(global_skills_path)
        if g_dir.is_dir():
            for skill_dir in sorted(g_dir.iterdir()):
                if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.is_file():
                        candidates.append((
                            skill_file,
                            SourceType.INSTALLED_GLOBAL,
                            "global",
                            "",
                            f"{skill_dir.name}/SKILL.md"
                        ))

        # 3. Plugin Skills
        p_dir = Path(plugins_path)
        if p_dir.is_dir():
            for plugin_dir in sorted(p_dir.iterdir()):
                if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
                    skills_dir = plugin_dir / "skills"
                    if skills_dir.is_dir():
                        # Direct SKILL.md in skills/
                        root_skill = skills_dir / "SKILL.md"
                        if root_skill.is_file():
                            candidates.append((
                                root_skill,
                                SourceType.INSTALLED_PLUGIN,
                                f"plugin:{plugin_dir.name}",
                                plugin_dir.name,
                                f"{plugin_dir.name}/skills/SKILL.md"
                            ))
                        # Nested subdirectories
                        for sub_dir in sorted(skills_dir.iterdir()):
                            if sub_dir.is_dir():
                                sub_file = sub_dir / "SKILL.md"
                                if sub_file.is_file():
                                    candidates.append((
                                        sub_file,
                                        SourceType.INSTALLED_PLUGIN,
                                        f"plugin:{plugin_dir.name}",
                                        plugin_dir.name,
                                        f"{plugin_dir.name}/skills/{sub_dir.name}/SKILL.md"
                                    ))

        # 4. Built-in Skills
        b_dir = Path(builtin_skills_path)
        if b_dir.is_dir():
            for skill_dir in sorted(b_dir.iterdir()):
                if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.is_file():
                        candidates.append((
                            skill_file,
                            SourceType.INSTALLED_BUILTIN,
                            "builtin",
                            "",
                            f"{skill_dir.name}/SKILL.md"
                        ))

        # 5. Project Skills
        if project_skills_path:
            pr_dir = Path(project_skills_path)
            if pr_dir.is_dir():
                for skill_dir in sorted(pr_dir.iterdir()):
                    if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                        skill_file = skill_dir / "SKILL.md"
                        if skill_file.is_file():
                            candidates.append((
                                skill_file,
                                SourceType.INSTALLED_PROJECT,
                                "project",
                                "",
                                f"{skill_dir.name}/SKILL.md"
                            ))

        total_candidates = len(candidates)
        stats["discovered"] = total_candidates

        # Process each candidate
        for idx, (s_path, s_type, cat, subcat, rel_path) in enumerate(candidates):
            if progress_cb and idx % 25 == 0:
                progress_cb(s_path.name, idx + 1, total_candidates)

            # Check for incremental skip
            skill_id = f"{s_type.value}:{cat}:{s_path.parent.name.lower()}"
            if not force_reindex:
                existing = self.repo.get_skill_hash_and_mtime(skill_id)
                if existing:
                    old_hash, old_mtime = existing
                    current_mtime = s_path.stat().st_mtime
                    if abs(current_mtime - old_mtime) < 0.001:
                        # File timestamp unchanged, load existing
                        existing_record = self.repo.get_skill_by_id(skill_id)
                        if existing_record:
                            all_records.append(existing_record)
                            stats["skipped_unchanged"] += 1
                            continue

            # Parse file
            record = self.parser.parse_skill_file(
                skill_file_path=s_path,
                source_type=s_type,
                category=cat,
                subcategory=subcat,
                relative_path=rel_path
            )

            if not record:
                stats["broken"] += 1
                continue

            # Validate
            is_valid, validation_msgs = self.validator.validate_skill(record)
            if not is_valid:
                if record.status != SkillStatus.QUARANTINED:
                    record.status = SkillStatus.BROKEN
                    stats["broken"] += 1
            if record.status == SkillStatus.QUARANTINED:
                stats["quarantined"] += 1

            all_records.append(record)
            stats["indexed"] += 1

        # Deduplication and relationship pass
        all_records = self.dedup.assign_relationships(all_records)

        # Batch upsert into database
        for rec in all_records:
            self.repo.upsert_skill(rec)

        self.repo.set_metadata("last_index_time", datetime.now(timezone.utc).isoformat())
        self.repo.set_metadata("total_discovered", str(stats["discovered"]))
        self.repo.set_metadata("total_indexed", str(len(all_records)))

        return stats
