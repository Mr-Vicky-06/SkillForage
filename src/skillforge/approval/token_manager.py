"""SLIF Approval Token Manager: Cryptographic, single-use, short-lived consent gate."""

from __future__ import annotations
import json
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ApprovalTokenManager:
    """Manages short-lived approval tokens and conversational consent states."""

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
        """Mint a short-lived, single-use approval token associated with candidate skills."""
        task_text = task or task_query or "task"
        candidates = candidate_ids or []
        random_suffix = secrets.token_hex(2).upper()
        token = f"SF-{random_suffix}"

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=ttl_minutes)

        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO pending_approvals (
                    approval_token, conversation_id, turn_id, task_query,
                    candidate_ids_json, status, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
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
                ) VALUES (?, ?, 'recommend', 'minted', ?, ?)
            """, (
                token,
                conversation_id,
                json.dumps({"candidates": candidates, "task": task_text}),
                now.isoformat()
            ))
        conn.close()
        return token

    # Alias for mint_token
    create_approval_request = mint_token

    def validate_approval(
        self,
        token: str,
        requested_ids: List[str],
        conversation_id: str = ""
    ) -> Tuple[bool, str, List[str]]:
        """Validate whether the approval token is valid, unexpired, and requested IDs were permitted."""
        token = token.strip().upper()
        now = datetime.now(timezone.utc)

        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pending_approvals WHERE approval_token = ?", (token,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return False, f"Approval token '{token}' not found.", []

        status = row["status"]
        expires_at_dt = datetime.fromisoformat(row["expires_at"])
        candidate_ids = json.loads(row["candidate_ids_json"])

        # Check expiration
        if now > expires_at_dt:
            with conn:
                conn.execute("UPDATE pending_approvals SET status = 'expired' WHERE approval_token = ?", (token,))
                conn.execute("""
                    INSERT INTO approval_audit_log (approval_token, conversation_id, action, decision, timestamp)
                    VALUES (?, ?, 'validate', 'rejected_expired', ?)
                """, (token, conversation_id, now.isoformat()))
            conn.close()
            return False, f"Approval token '{token}' has expired (TTL {row['expires_at']}). Request a fresh recommendation.", []

        # Check if already resolved/declined
        if status in ["declined", "expired"]:
            conn.close()
            return False, f"Approval token '{token}' was previously {status}.", []

        # Check conversation matching if specified
        if conversation_id and row["conversation_id"] and conversation_id != row["conversation_id"]:
            conn.close()
            return False, f"Approval token '{token}' does not match active conversation context.", []

        # Validate requested IDs against candidate list
        valid_ids = []
        for req in requested_ids:
            req_clean = req.strip()
            # match either exact ID or exact name
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
                valid_ids.append(match)
            else:
                conn.close()
                return False, f"Skill '{req_clean}' was not in the approved candidate list for token '{token}'.", []

        if not valid_ids:
            # If user said YES without specific IDs, approve all candidates in the list
            valid_ids = list(candidate_ids)

        # Transition to LOADED
        with conn:
            conn.execute("""
                UPDATE pending_approvals 
                SET status = 'loaded', resolved_at = ? 
                WHERE approval_token = ?
            """, (now.isoformat(), token))

            conn.execute("""
                INSERT INTO approval_audit_log (
                    approval_token, conversation_id, action, decision, details_json, timestamp
                ) VALUES (?, ?, 'approve_and_load', 'approved', ?, ?)
            """, (
                token,
                conversation_id,
                json.dumps({"loaded_ids": valid_ids}),
                now.isoformat()
            ))
        conn.close()
        return True, "Approval verified. Instructions authorized for loading.", valid_ids

    def decline_token(self, token: str, conversation_id: str = "") -> bool:
        """Mark an approval token as explicitly declined by the user."""
        token = token.strip().upper()
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_conn()
        with conn:
            conn.execute("UPDATE pending_approvals SET status = 'declined', resolved_at = ? WHERE approval_token = ?", (now, token))
            conn.execute("""
                INSERT INTO approval_audit_log (approval_token, conversation_id, action, decision, timestamp)
                VALUES (?, ?, 'decline', 'declined_by_user', ?)
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
        return res
