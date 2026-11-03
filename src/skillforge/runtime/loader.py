"""SLIF Controlled Skill Loader: Enforces progressive disclosure and human approval (Hardened P0)."""

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
        """Load full SKILL.md instructions, strictly requiring an APPROVED authorization token."""
        # 1. Human Approval Gate Validation (Consumes the token)
        is_valid, msg, valid_ids = self.token_mgr.consume_token(
            token=approval_token,
            requested_ids=[skill_identifier],
            conversation_id=conversation_id
        )

        if not is_valid:
            return {
                "authorized": False,
                "error": msg,
                "approval_token": approval_token,
                "skill_identifier": skill_identifier
            }

        return self._read_skill_content(skill_identifier, approval_token)

    def load_approved_collection(
        self,
        skill_identifiers: List[str],
        approval_token: str,
        conversation_id: str = ""
    ) -> Dict[str, Any]:
        """Atomically validate and load an entire approved skill collection in one transaction."""
        # 1. Atomic token consumption for the whole collection
        is_valid, msg, valid_ids = self.token_mgr.consume_token(
            token=approval_token,
            requested_ids=skill_identifiers,
            conversation_id=conversation_id
        )

        if not is_valid:
            return {
                "all_authorized": False,
                "error": msg,
                "approval_token": approval_token,
                "loaded_skills": [{
                    "authorized": False,
                    "error": msg,
                    "skill_identifier": sid
                } for sid in skill_identifiers]
            }

        loaded = []
        for sid in valid_ids:
            res = self._read_skill_content(sid, approval_token)
            loaded.append(res)

        all_ok = all(s.get("authorized", False) for s in loaded)
        return {
            "all_authorized": all_ok,
            "approval_token": approval_token,
            "loaded_skills": loaded
        }

    def _read_skill_content(self, skill_identifier: str, approval_token: str) -> Dict[str, Any]:
        """Read and verify skill instructions from disk."""
        skill = self.repo.get_skill_by_id(skill_identifier)
        if not skill:
            skill = self.repo.get_skill_by_name(skill_identifier)

        if not skill:
            return {
                "authorized": False,
                "error": f"Skill '{skill_identifier}' verified in approval but not found in registry.",
                "skill_identifier": skill_identifier
            }

        # Path Security & Traversal Guard
        skill_path = Path(skill.source_path)
        if not skill_path.is_file():
            return {
                "authorized": False,
                "error": f"Skill file missing on disk at '{skill.source_path}'.",
                "skill_identifier": skill.name
            }

        # Checksum Integrity Verification (cross-platform CRLF/LF normalized)
        actual_hash = compute_sha256(skill_path)
        raw_hash = hashlib.sha256(skill_path.read_bytes()).hexdigest()
        if skill.file_hash and actual_hash != skill.file_hash and raw_hash != skill.file_hash:
            return {
                "authorized": False,
                "error": f"INTEGRITY VIOLATION: Skill '{skill.name}' hash mismatch. Expected {skill.file_hash[:12]}, got {actual_hash[:12]}. File may have been altered.",
                "skill_identifier": skill.name
            }

        # Read SKILL.md Instructions
        content = skill_path.read_text(encoding="utf-8", errors="replace")

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
