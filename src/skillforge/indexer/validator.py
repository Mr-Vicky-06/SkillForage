"""Skill Structure and Prerequisite Validator."""

import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from skillforge.database.models import SkillRecord, SkillStatus, TrustLevel


class SkillValidator:
    def validate_skill(self, skill: SkillRecord) -> Tuple[bool, List[str]]:
        """Validate a SkillRecord's integrity, file existence, and prerequisites.
        
        Returns:
            (is_valid, validation_messages)
        """
        messages: List[str] = []
        is_valid = True

        # Check source file existence
        path = Path(skill.source_path)
        if not path.is_file():
            messages.append(f"Source file does not exist: {skill.source_path}")
            return False, messages

        # Mandatory fields
        if not skill.name or not skill.name.strip():
            messages.append("Missing mandatory field: name")
            is_valid = False

        if not skill.description or not skill.description.strip():
            messages.append("Missing mandatory field: description")
            is_valid = False

        if not skill.category or not skill.category.strip():
            messages.append("Missing mandatory field: category")
            is_valid = False

        # Check missing referenced files
        if skill.missing_files:
            messages.append(f"Missing referenced files ({len(skill.missing_files)}): {', '.join(skill.missing_files[:3])}")

        # Check dependencies / binaries
        for dep in skill.dependencies:
            if dep.dependency_type == "binary":
                found = shutil.which(dep.name) is not None
                dep.is_satisfied = found
                if not found:
                    messages.append(f"External binary prerequisite missing: '{dep.name}'")

        # Security check
        if skill.trust_level == TrustLevel.QUARANTINED:
            messages.append(f"Security quarantine: {', '.join(skill.security_flags)}")
            is_valid = False

        return is_valid, messages

