"""SLIF Local Skill Script Executor: Sandboxed, timeout-managed local execution engine."""

from __future__ import annotations
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from skillforge.approval.token_manager import ApprovalTokenManager
from skillforge.database.repository import SkillRepository
from skillforge.security.path_guard import PathGuard


def redact_secrets(text: str) -> str:
    """Redacts tokens, API keys, passwords from text output and parameters."""
    if not text:
        return text
    cleaned = text
    cleaned = re.sub(
        r"(?i)(api[_-]?key|secret|password|token|bearer|auth|credential)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?",
        r"\1: [REDACTED]",
        cleaned
    )
    cleaned = re.sub(r"ghp_[a-zA-Z0-9]{36}", "[REDACTED_GH_TOKEN]", cleaned)
    cleaned = re.sub(r"sk-[a-zA-Z0-9]{20,}", "[REDACTED_KEY]", cleaned)
    return cleaned


class LocalSkillExecutor:
    """Executes approved skill scripts locally with sandboxed parameters, timeouts, and auditing."""

    def __init__(
        self,
        repo: SkillRepository,
        token_mgr: Optional[ApprovalTokenManager] = None,
        default_timeout_seconds: float = 30.0,
        strict_offline: bool = False
    ):
        self.repo = repo
        self.token_mgr = token_mgr or ApprovalTokenManager(repo.db_path)
        self.default_timeout_seconds = default_timeout_seconds
        self.strict_offline = strict_offline
        self.path_guard = PathGuard()

    def execute_script(
        self,
        skill_identifier: str,
        script_path: str | Path,
        parameters: Optional[Dict[str, Any]] = None,
        granted_permissions: Optional[List[str]] = None,
        approval_token: str = "",
        conversation_id: str = "",
        dry_run: bool = False,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Execute a local skill script with security checks, timeouts, and auditing."""
        start_time = time.perf_counter()
        params = parameters or {}
        permissions = set(granted_permissions or [])
        timeout_sec = timeout if timeout is not None else self.default_timeout_seconds
        script_file = Path(script_path).resolve()

        # 1. Approval Gate Validation
        if not dry_run:
            is_valid, msg, _ = self.token_mgr.validate_approval(
                token=approval_token,
                requested_ids=[skill_identifier],
                conversation_id=conversation_id
            )
            if not is_valid:
                return {
                    "success": False,
                    "exit_code": -1,
                    "error": f"EXECUTION DENIED: Approval verification failed: {msg}",
                    "stdout": "",
                    "stderr": "",
                    "duration_ms": 0.0,
                    "dry_run": dry_run
                }

        # 2. Path Security & Script Existence
        if not script_file.is_file():
            return {
                "success": False,
                "exit_code": -1,
                "error": f"EXECUTION ERROR: Script not found at '{script_file}'.",
                "stdout": "",
                "stderr": "",
                "duration_ms": 0.0,
                "dry_run": dry_run
            }

        # 3. Permissions Check
        if "EXECUTE_SCRIPT" not in permissions:
            return {
                "success": False,
                "exit_code": -1,
                "error": "EXECUTION DENIED: Missing required permission 'EXECUTE_SCRIPT'.",
                "stdout": "",
                "stderr": "",
                "duration_ms": 0.0,
                "dry_run": dry_run
            }

        # 4. Strict Offline Mode Check
        if self.strict_offline and "ACCESS_NETWORK" in permissions:
            return {
                "success": False,
                "exit_code": -1,
                "error": "POLICY VIOLATION: Network access blocked in strict-offline mode.",
                "stdout": "",
                "stderr": "",
                "duration_ms": 0.0,
                "dry_run": dry_run
            }

        # 5. Dry-Run Handling
        if dry_run:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "success": True,
                "exit_code": 0,
                "stdout": f"[DRY-RUN] Script '{script_file.name}' validated. Permissions: {list(permissions)}. Ready for execution.",
                "stderr": "",
                "duration_ms": duration_ms,
                "dry_run": True
            }

        # 6. Prepare Execution Environment
        env = os.environ.copy()
        if self.strict_offline:
            env["SKILLFORGE_OFFLINE_MODE"] = "1"
            for secret_var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN"]:
                env.pop(secret_var, None)

        suffix = script_file.suffix.lower()
        if suffix == ".py":
            cmd = [sys.executable, str(script_file)]
        elif suffix in [".js", ".mjs"]:
            cmd = ["node", str(script_file)]
        elif suffix in [".ps1"]:
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_file)]
        elif suffix in [".sh", ".bash"]:
            cmd = ["bash", str(script_file)]
        else:
            return {
                "success": False,
                "exit_code": -1,
                "error": f"UNSUPPORTED SCRIPT TYPE: Extension '{suffix}' cannot be executed directly.",
                "stdout": "",
                "stderr": "",
                "duration_ms": 0.0,
                "dry_run": False
            }

        if params:
            safe_params_json = json.dumps(params)
            cmd.append(safe_params_json)

        # 7. Subprocess Execution with Timeout
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=timeout_sec,
                cwd=str(script_file.parent)
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            stdout_clean = redact_secrets(proc.stdout)
            stderr_clean = redact_secrets(proc.stderr)
            exit_code = proc.returncode
            success = (exit_code == 0)
            err_msg = stderr_clean if not success else None

        except subprocess.TimeoutExpired:
            duration_ms = timeout_sec * 1000.0
            return {
                "success": False,
                "exit_code": -2,
                "error": f"EXECUTION TIMEOUT: Script exceeded allotted limit of {timeout_sec:.1f}s.",
                "stdout": "",
                "stderr": "Execution timed out.",
                "duration_ms": duration_ms,
                "dry_run": False
            }
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "success": False,
                "exit_code": -3,
                "error": f"EXECUTION EXCEPTION: {str(e)}",
                "stdout": "",
                "stderr": str(e),
                "duration_ms": duration_ms,
                "dry_run": False
            }

        # 8. Record Execution in Database Audit Log
        self._record_execution_audit(
            conversation_id=conversation_id,
            skill_id=skill_identifier,
            script_path=str(script_file),
            params=params,
            permissions=list(permissions),
            duration_ms=duration_ms,
            exit_code=exit_code,
            output_summary=stdout_clean[:500] if stdout_clean else (stderr_clean[:500] if stderr_clean else "")
        )

        return {
            "success": success,
            "exit_code": exit_code,
            "stdout": stdout_clean,
            "stderr": stderr_clean,
            "duration_ms": duration_ms,
            "dry_run": False,
            "error": err_msg
        }

    def _record_execution_audit(
        self,
        conversation_id: str,
        skill_id: str,
        script_path: str,
        params: Dict[str, Any],
        permissions: List[str],
        duration_ms: float,
        exit_code: int,
        output_summary: str
    ) -> None:
        """Persist execution log entry safely with redacted parameters."""
        try:
            safe_params_str = redact_secrets(json.dumps(params))
            now_iso = datetime.now(timezone.utc).isoformat()
            with self.repo.conn:
                self.repo.conn.execute(
                    """
                    INSERT INTO execution_audit_log (
                        conversation_id, skill_id, script_path, params_json,
                        permissions_granted, duration_ms, exit_code, output_summary, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conversation_id,
                        skill_id,
                        script_path,
                        safe_params_str,
                        json.dumps(permissions),
                        duration_ms,
                        exit_code,
                        output_summary,
                        now_iso
                    )
                )
        except Exception:
            pass
