"""SLIF Cryptographic Approval Token Manager (Hardened P0).

Enforces high-entropy tokens, mandatory conversation/turn binding,
strict state machine (PENDING -> APPROVED -> CONSUMED),
single-use replay prevention, and atomic approval collections.
"""

from __future__ import annotations
import json
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ApprovalTokenManager:
    """Manages high-entropy approval tokens and strictly auditable consent transitions."""

    def __init__(self, db_path: str | Path = "data/registry.db"):
        self.db_path = str(db_path)

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def mint_token(
        self,
        task_query: str = "",
        candidate_ids: Optional[List[str]] = None,
        conversation_id: str = "",
        turn_id: int = 1,
        ttl_minutes: int = 15,
        task: str = ""
    ) -> str:
        """Mint a cryptographically secure 128-bit entropy approval token in PENDING state."""
        task_text = task or task_query or "task"
        candidates = candidate_ids or []
        # 32 hex characters = 128 bits of cryptographic entropy
        random_suffix = secrets.token_hex(16).upper()
        token = f"SF-{random_suffix}"

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=ttl_minutes)

        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO pending_approvals (
                    approval_token, conversation_id, turn_id, task_query,
                    candidate_ids_json, approved_ids_json, status, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, NULL, 'pending', ?, ?)
            """, (
                token,
                conversation_id,
                turn_id,
                task_text,
                json.dumps(candidates),
                now.isoformat(),
                expires_at.isoformat()
            ))

            conn.execute("""
                INSERT INTO approval_audit_log (
                    approval_token, conversation_id, action, decision, details_json, timestamp
                ) VALUES (?, ?, 'mint_token', 'pending', ?, ?)
            """, (
                token,
                conversation_id,
                json.dumps({"candidates": candidates, "task": task_text, "turn_id": turn_id}),
                now.isoformat()
            ))
        conn.close()
        return token

    # Alias for mint_token
    create_approval_request = mint_token

    def approve_token(
        self,
        token: str,
        approved_skill_ids: List[str],
        conversation_id: str = "",
        turn_id: int = 1
    ) -> Tuple[bool, str, List[str]]:
        """Transition token from PENDING to APPROVED for an exact non-empty skill collection."""
        token = token.strip().upper()
        now = datetime.now(timezone.utc)

        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pending_approvals WHERE approval_token = ?", (token,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return False, f"ACCESS DENIED: Approval token '{token}' not found.", []

        status = row["status"]
        expires_at_dt = datetime.fromisoformat(row["expires_at"])
        candidate_ids = json.loads(row["candidate_ids_json"])

        # Check expiration
        if now > expires_at_dt:
            with conn:
                conn.execute("UPDATE pending_approvals SET status = 'expired' WHERE approval_token = ?", (token,))
                conn.execute("""
                    INSERT INTO approval_audit_log (approval_token, conversation_id, action, decision, timestamp)
                    VALUES (?, ?, 'approve', 'rejected_expired', ?)
                """, (token, conversation_id, now.isoformat()))
            conn.close()
            return False, f"ACCESS DENIED: Approval token '{token}' has expired (TTL {row['expires_at']}).", []

        # Enforce PENDING prerequisite
        if status != "pending":
            conn.close()
            return False, f"ACCESS DENIED: Token '{token}' cannot be approved because it is in '{status.upper()}' state.", []

        # Mandatory conversation binding
        bound_conv = row["conversation_id"] or ""
        if bound_conv:
            if not conversation_id or conversation_id != bound_conv:
                conn.close()
                return False, f"ACCESS DENIED: Conversation binding mismatch. Token is bound to conversation '{bound_conv}'.", []

        # Mandatory non-empty selection check (NO fallback to all candidates)
        if not approved_skill_ids:
            conn.close()
            return False, "ACCESS DENIED: No skills selected for approval. Explicit selection is mandatory.", []

        # Validate approved skill IDs strictly against candidate list
        valid_ids = []
        for req in approved_skill_ids:
            req_clean = req.strip()
            match = next((
                c for c in candidate_ids 
                if c == req_clean 
                or c.endswith(f":{req_clean}") 
                or c.endswith(f"--{req_clean}")
                or req_clean.endswith(f"--{c}")
                or c.split(":")[-1] == req_clean
                or c.split("--")[-1] == req_clean
                or req_clean.split("--")[-1] == c
            ), None)
            if match:
                if match not in valid_ids:
                    valid_ids.append(match)
            else:
                conn.close()
                return False, f"ACCESS DENIED: Skill '{req_clean}' was not in the proposed candidate list for token '{token}'.", []

        # Atomically transition state to APPROVED
        with conn:
            conn.execute("""
                UPDATE pending_approvals 
                SET status = 'approved', approved_ids_json = ?, approved_at = ?, turn_id = ?
                WHERE approval_token = ?
            """, (json.dumps(valid_ids), now.isoformat(), turn_id, token))

            conn.execute("""
                INSERT INTO approval_audit_log (
                    approval_token, conversation_id, action, decision, details_json, timestamp
                ) VALUES (?, ?, 'approve_token', 'approved', ?, ?)
            """, (
                token,
                conversation_id,
                json.dumps({"approved_ids": valid_ids, "turn_id": turn_id}),
                now.isoformat()
            ))
        conn.close()
        return True, "Approval verified. Candidate collection authorized.", valid_ids

    def consume_token(
        self,
        token: str,
        requested_ids: List[str],
        conversation_id: str = ""
    ) -> Tuple[bool, str, List[str]]:
        """Validate an APPROVED token and atomically transition it to CONSUMED (preventing replay)."""
        token = token.strip().upper()
        now = datetime.now(timezone.utc)

        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pending_approvals WHERE approval_token = ?", (token,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return False, f"ACCESS DENIED: Approval token '{token}' not found.", []

        status = row["status"]
        expires_at_dt = datetime.fromisoformat(row["expires_at"])

        # Check expiration
        if now > expires_at_dt:
            with conn:
                conn.execute("UPDATE pending_approvals SET status = 'expired' WHERE approval_token = ?", (token,))
                conn.execute("""
                    INSERT INTO approval_audit_log (approval_token, conversation_id, action, decision, timestamp)
                    VALUES (?, ?, 'consume', 'rejected_expired', ?)
                """, (token, conversation_id, now.isoformat()))
            conn.close()
            return False, f"ACCESS DENIED: Approval token '{token}' has expired.", []

        # Enforce APPROVED prerequisite - strictly reject PENDING, CONSUMED, DECLINED
        if status == "pending":
            conn.close()
            return False, f"ACCESS DENIED: Token '{token}' is in PENDING state. Explicit user conversational approval is required before loading.", []

        if status == "consumed" or status == "loaded":
            conn.close()
            return False, f"ACCESS DENIED: Token '{token}' has already been consumed (replay prevention). Request a fresh recommendation.", []

        if status == "declined":
            conn.close()
            return False, f"ACCESS DENIED: Token '{token}' was previously declined by user.", []

        if status != "approved":
            conn.close()
            return False, f"ACCESS DENIED: Token '{token}' is in invalid state '{status}'.", []

        # Mandatory conversation binding
        bound_conv = row["conversation_id"] or ""
        if bound_conv:
            if not conversation_id or conversation_id != bound_conv:
                conn.close()
                return False, f"ACCESS DENIED: Conversation binding mismatch. Token is bound to conversation '{bound_conv}'.", []

        # Retrieve approved skill IDs
        raw_approved = row["approved_ids_json"]
        if not raw_approved:
            conn.close()
            return False, f"ACCESS DENIED: No approved skill IDs registered for token '{token}'.", []

        approved_ids = json.loads(raw_approved)

        # Validate requested IDs against approved list
        if not requested_ids:
            conn.close()
            return False, "ACCESS DENIED: No skills requested for loading.", []

        valid_ids = []
        for req in requested_ids:
            req_clean = req.strip()
            match = next((
                c for c in approved_ids 
                if c == req_clean 
                or c.endswith(f":{req_clean}") 
                or c.endswith(f"--{req_clean}")
                or req_clean.endswith(f"--{c}")
                or c.split(":")[-1] == req_clean
                or c.split("--")[-1] == req_clean
                or req_clean.split("--")[-1] == c
            ), None)
            if match:
                if match not in valid_ids:
                    valid_ids.append(match)
            else:
                conn.close()
                return False, f"ACCESS DENIED: Skill '{req_clean}' was not approved under token '{token}'.", []

        # Transition state to CONSUMED
        with conn:
            conn.execute("""
                UPDATE pending_approvals 
                SET status = 'consumed', consumed_at = ?, resolved_at = ? 
                WHERE approval_token = ?
            """, (now.isoformat(), now.isoformat(), token))

            conn.execute("""
                INSERT INTO approval_audit_log (
                    approval_token, conversation_id, action, decision, details_json, timestamp
                ) VALUES (?, ?, 'consume_token', 'consumed', ?, ?)
            """, (
                token,
                conversation_id,
                json.dumps({"consumed_ids": valid_ids}),
                now.isoformat()
            ))
        conn.close()
        return True, "Token verified and consumed. Access authorized.", valid_ids

    # validate_approval delegates directly to consume_token for strict authorization
    def validate_approval(
        self,
        token: str,
        requested_ids: List[str],
        conversation_id: str = ""
    ) -> Tuple[bool, str, List[str]]:
        return self.consume_token(token=token, requested_ids=requested_ids, conversation_id=conversation_id)

    def decline_token(self, token: str, conversation_id: str = "") -> bool:
        """Mark an approval token as explicitly declined by the user."""
        token = token.strip().upper()
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT status, conversation_id FROM pending_approvals WHERE approval_token = ?", (token,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False

        if conversation_id and row["conversation_id"] and conversation_id != row["conversation_id"]:
            conn.close()
            return False

        with conn:
            conn.execute("""
                UPDATE pending_approvals 
                SET status = 'declined', resolved_at = ? 
                WHERE approval_token = ?
            """, (now, token))
            conn.execute("""
                INSERT INTO approval_audit_log (approval_token, conversation_id, action, decision, timestamp)
                VALUES (?, ?, 'decline_token', 'declined_by_user', ?)
            """, (token, conversation_id, now))
        conn.close()
        return True

    # Alias for decline_token
    decline_request = decline_token

    def get_status(self, token: str) -> Optional[Dict[str, Any]]:
        """Retrieve token record details."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pending_approvals WHERE approval_token = ?", (token.strip().upper(),))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res["candidate_ids"] = json.loads(res["candidate_ids_json"])
        if res.get("approved_ids_json"):
            res["approved_ids"] = json.loads(res["approved_ids_json"])
        return res
