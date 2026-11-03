"""SLIF Cross-Source Research Verification Engine.

Performs atomic claim extraction, source tiering (Tier 1/2/3),
contradiction detection, confidence scoring, and local SQLite result persistence.
"""

from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import sqlite3


TIER_1_PATTERNS = [
    r"\.gov(/|$)",
    r"sec\.gov",
    r"patents\.google\.com",
    r"uspto\.gov",
    r"doi\.org",
    r"nature\.com",
    r"acm\.org",
    r"ieee\.org",
    r"science\.org",
    r"springer\.com",
    r"ncbi\.nlm\.nih\.gov",
    r"wipo\.int",
    r"github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/(blob|tree|commit)",
]

TIER_2_PATTERNS = [
    r"arxiv\.org",
    r"biorxiv\.org",
    r"medrxiv\.org",
    r"openalex\.org",
    r"semanticscholar\.org",
    r"techcrunch\.com",
    r"bloomberg\.com",
    r"reuters\.com",
    r"martinfowler\.com",
    r"eng\.uber\.com",
    r"netflixtechblog\.com",
    r"blog\.",
]


def classify_source_tier(source: str) -> int:
    """Classify a source identifier, domain, or URL into Tier 1, 2, or 3."""
    src_lower = source.lower()
    for pat in TIER_1_PATTERNS:
        if re.search(pat, src_lower):
            return 1
    for pat in TIER_2_PATTERNS:
        if re.search(pat, src_lower):
            return 2
    return 3


def extract_atomic_claims(text: str) -> List[str]:
    """Break a complex paragraph or statement into discrete atomic factual claims."""
    # Split by common sentence delimiters and bullet points
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+|- |\* ", text)
    claims = []
    for s in raw_sentences:
        clean = s.strip()
        if len(clean) > 15 and not clean.startswith("#"):
            # Exclude conversational headers
            claims.append(clean)
    return claims if claims else [text.strip()]


class ResearchCache:
    """Local SQLite-backed cache for research queries and retrieved documents."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def get(self, query_key: str, source_api: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if valid and unexpired."""
        h = hashlib.sha256(f"{source_api}:{query_key}".encode("utf-8")).hexdigest()
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT data_json, expires_at FROM research_cache
                WHERE query_key = ? AND source_api = ?
                """,
                (h, source_api)
            ).fetchone()

            if row:
                data_json, expires_at = row
                if expires_at and expires_at < now_iso:
                    # Expired
                    return None
                try:
                    return json.loads(data_json)
                except Exception:
                    return None
        return None

    def set(
        self,
        query_key: str,
        source_api: str,
        data: Dict[str, Any],
        ttl_days: int = 7
    ) -> str:
        """Store research result with content hash and expiry."""
        h = hashlib.sha256(f"{source_api}:{query_key}".encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(days=ttl_days)).isoformat()
        data_str = json.dumps(data)
        content_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO research_cache (query_key, source_api, data_json, content_hash, cached_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(query_key) DO UPDATE SET
                    data_json = excluded.data_json,
                    content_hash = excluded.content_hash,
                    cached_at = excluded.cached_at,
                    expires_at = excluded.expires_at
                """,
                (h, source_api, data_str, content_hash, now.isoformat(), expires)
            )
        return h


class CrossSourceVerifier:
    """Verifies statements across multiple sources using rigorous cross-checking protocol."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self.cache = ResearchCache(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def verify_statement(
        self,
        statement: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify a statement or multi-point claim against a list of evidence sources.
        
        sources format:
        [
            {"url": "...", "title": "...", "quote": "...", "supports": True, "contradicts": False},
            ...
        ]
        """
        claims = extract_atomic_claims(statement)
        verified_claims = []
        overall_status = "verified"
        total_score = 0.0

        for claim in claims:
            res = self._evaluate_claim_evidence(claim, sources)
            verified_claims.append(res)
            total_score += res["confidence_score"]

            # Save to cross_verification_records table
            self._save_record(claim, res["status"], res["confidence_score"], res["evidence"])

        avg_score = total_score / len(claims) if claims else 0.0
        
        # Determine overall status
        statuses = {c["status"] for c in verified_claims}
        if "contradictory" in statuses or "disputed" in statuses:
            overall_status = "disputed"
        elif "unverified" in statuses:
            overall_status = "unverified" if len(statuses) == 1 else "likely"
        elif all(s == "verified" for s in statuses):
            overall_status = "verified"
        else:
            overall_status = "likely"

        return {
            "statement": statement,
            "overall_status": overall_status,
            "overall_confidence": round(avg_score, 2),
            "claims_count": len(claims),
            "claim_verifications": verified_claims,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _evaluate_claim_evidence(
        self,
        claim: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate a single claim against evidence sources with tier weighting and conflict detection."""
        tier1_supporting = 0
        tier2_supporting = 0
        tier3_supporting = 0
        contradictions = 0
        evidence_list = []

        for s in sources:
            source_ref = s.get("url") or s.get("title") or s.get("source", "unknown")
            tier = classify_source_tier(source_ref)
            supports = s.get("supports", True)
            contradicts = s.get("contradicts", False)

            evidence_entry = {
                "source": source_ref,
                "tier": tier,
                "supports": supports,
                "contradicts": contradicts,
                "snippet": s.get("quote") or s.get("snippet", "")
            }
            evidence_list.append(evidence_entry)

            if contradicts:
                contradictions += 1
            elif supports:
                if tier == 1:
                    tier1_supporting += 1
                elif tier == 2:
                    tier2_supporting += 1
                else:
                    tier3_supporting += 1

        # Conflict Detection
        if contradictions > 0:
            status = "disputed" if contradictions >= 1 and (tier1_supporting > 0 or tier2_supporting > 0) else "contradictory"
            conf = max(0.1, 0.4 - (0.1 * contradictions))
        elif tier1_supporting >= 2 or (tier1_supporting >= 1 and tier2_supporting >= 2):
            status = "verified"
            conf = min(0.98, 0.85 + (0.05 * tier1_supporting) + (0.03 * tier2_supporting))
        elif tier1_supporting >= 1 or tier2_supporting >= 2:
            status = "likely"
            conf = min(0.85, 0.70 + (0.05 * tier2_supporting))
        elif tier2_supporting == 1 or tier3_supporting >= 2:
            status = "unverified"
            conf = 0.50
        else:
            status = "unverified"
            conf = 0.25

        return {
            "claim": claim,
            "status": status,
            "confidence_score": round(conf, 2),
            "tier1_count": tier1_supporting,
            "tier2_count": tier2_supporting,
            "contradiction_count": contradictions,
            "evidence": evidence_list
        }

    def _save_record(
        self,
        claim: str,
        status: str,
        confidence: float,
        evidence: List[Dict[str, Any]]
    ) -> None:
        """Persist verified claim record to local SQLite table."""
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO cross_verification_records (
                        claim_text, verified_status, confidence_score, evidence_json, verified_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (claim, status, confidence, json.dumps(evidence), now_iso)
                )
        except Exception:
            pass
