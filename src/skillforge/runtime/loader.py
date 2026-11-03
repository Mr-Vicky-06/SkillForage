"""SLIF Controlled Skill Loader: Enforces progressive disclosure and human approval."""

from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillforge.approval.token_manager import ApprovalTokenManager
from skillforge.database.repository import SkillRepository
from skillforge.security.path_guard import PathGuard


def compute_sha256(path: str | Path) -> str:
    p = Path(path)
    if not p.is_file():
        return ""
    data = p.read_bytes()
    norm = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(norm).hexdigest()


class ControlledSkillLoader:
    """Loads specialist skill instructions only after explicit human approval."""

    def __init__(self, repo: SkillRepository, token_mgr: Optional[ApprovalTokenManager] = None):
        self.repo = repo
        self.token_mgr = token_mgr or ApprovalTokenManager(repo.db_path)
        self.path_guard = PathGuard()

    def load_approved_skill(
        self,
        skill_identifier: str,
        approval_token: str,
        conversation_id: str = ""
    ) -> Dict[str, Any]:
        """Load full SKILL.md instructions, strictly requiring a verified approval token."""
        # 1. Human Approval Gate Validation
        is_valid, msg, valid_ids = self.token_mgr.validate_approval(
            token=approval_token,
            requested_ids=[skill_identifier],
            conversation_id=conversation_id
        )

        if not is_valid:
            return {
                "authorized": False,
                "error": f"ACCESS DENIED: {msg}",
                "approval_token": approval_token,
                "skill_identifier": skill_identifier
            }

        # 2. Retrieve Skill Metadata from Registry
        skill = self.repo.get_skill_by_id(skill_identifier)
        if not skill:
            skill = self.repo.get_skill_by_name(skill_identifier)

        if not skill:
            return {
                "authorized": False,
                "error": f"Skill '{skill_identifier}' verified in approval but not found in registry.",
                "skill_identifier": skill_identifier
            }

        # 3. Path Security & Traversal Guard
        skill_path = Path(skill.source_path)
        if not skill_path.is_file():
            return {
                "authorized": False,
                "error": f"Skill file missing on disk at '{skill.source_path}'.",
                "skill_identifier": skill.name
            }

        # 4. Checksum Integrity Verification (cross-platform CRLF/LF normalized)
        actual_hash = compute_sha256(skill_path)
        raw_hash = hashlib.sha256(skill_path.read_bytes()).hexdigest()
        if skill.file_hash and actual_hash != skill.file_hash and raw_hash != skill.file_hash:
            return {
                "authorized": False,
                "error": f"INTEGRITY VIOLATION: Skill '{skill.name}' hash mismatch. Expected {skill.file_hash[:12]}, got {actual_hash[:12]}. File may have been altered.",
                "skill_identifier": skill.name
            }

        # 5. Progressive Disclosure: Read SKILL.md Instructions
        content = skill_path.read_text(encoding="utf-8", errors="replace")

        # 6. Extract declared dependencies and offline capability
        deps = [d.name for d in getattr(skill, "dependencies", [])]
        req_net = any(k in content.lower() for k in ["https://", "api.", "requests.", "httpx", "curl"])

        return {
            "authorized": True,
            "skill_id": skill.id,
            "name": skill.name,
            "category": skill.category,
            "subcategory": skill.subcategory,
            "version": getattr(skill, "version", "1.0.0"),
            "license": "MIT",
            "offline_capable": not req_net,
            "declared_dependencies": deps,
            "instructions": content,
            "approval_token": approval_token
        }
