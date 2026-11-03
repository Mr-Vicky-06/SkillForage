"""SQLite Repository for SkillForge Database Operations."""

from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skillforge.database.migrations import init_database
from skillforge.database.models import (
    ProjectProfile,
    SkillDependency,
    SkillRecord,
    SkillRelationship,
    SkillStatus,
    SourceType,
    TrustLevel,
)


class SkillRepository:
    def __init__(self, db_path: str | Path = "data/registry.db"):
        self.db_path = Path(db_path)
        self.conn = init_database(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()

    def get_skill_by_id(self, skill_id: str) -> Optional[SkillRecord]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM skills WHERE id = ?", (skill_id,))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_skill(row)

    def get_skill_by_name(self, name: str) -> Optional[SkillRecord]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM skills WHERE name = ? COLLATE NOCASE LIMIT 1", (name,))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_skill(row)

    def get_skill_hash_and_mtime(self, skill_id: str) -> Optional[Tuple[str, float]]:
        cur = self.conn.cursor()
        cur.execute("SELECT file_hash, mtime FROM skills WHERE id = ?", (skill_id,))
        row = cur.fetchone()
        if row:
            return row["file_hash"], row["mtime"]
        return None

    def upsert_skill(self, skill: SkillRecord) -> None:
        cur = self.conn.cursor()
        with self.conn:
            # Upsert into skills table
            cur.execute("""
            INSERT INTO skills (
                id, name, description, category, subcategory,
                source_type, source_path, relative_path, file_hash,
                mtime, status, trust_level, quality_score, author,
                version, raw_frontmatter, missing_files, security_flags,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                category = excluded.category,
                subcategory = excluded.subcategory,
                source_type = excluded.source_type,
                source_path = excluded.source_path,
                relative_path = excluded.relative_path,
                file_hash = excluded.file_hash,
                mtime = excluded.mtime,
                status = excluded.status,
                trust_level = excluded.trust_level,
                quality_score = excluded.quality_score,
                author = excluded.author,
                version = excluded.version,
                raw_frontmatter = excluded.raw_frontmatter,
                missing_files = excluded.missing_files,
                security_flags = excluded.security_flags,
                updated_at = excluded.updated_at;
            """, (
                skill.id, skill.name, skill.description, skill.category, skill.subcategory,
                skill.source_type.value, skill.source_path, skill.relative_path, skill.file_hash,
                skill.mtime, skill.status.value, skill.trust_level.value, skill.quality_score,
                skill.author, skill.version, json.dumps(skill.raw_frontmatter),
                json.dumps(skill.missing_files), json.dumps(skill.security_flags),
                skill.created_at, datetime.now(timezone.utc).isoformat()
            ))

            # Replace tags, triggers, technologies
            cur.execute("DELETE FROM skill_tags WHERE skill_id = ?", (skill.id,))
            for tag in skill.tags:
                cur.execute("INSERT OR IGNORE INTO skill_tags (skill_id, tag) VALUES (?, ?)", (skill.id, tag))

            cur.execute("DELETE FROM skill_triggers WHERE skill_id = ?", (skill.id,))
            for trigger in skill.triggers:
                cur.execute("INSERT OR IGNORE INTO skill_triggers (skill_id, trigger) VALUES (?, ?)", (skill.id, trigger))

            cur.execute("DELETE FROM skill_technologies WHERE skill_id = ?", (skill.id,))
            for tech in skill.technologies:
                cur.execute("INSERT OR IGNORE INTO skill_technologies (skill_id, technology) VALUES (?, ?)", (skill.id, tech))

            # Replace dependencies
            cur.execute("DELETE FROM skill_dependencies WHERE skill_id = ?", (skill.id,))
            for dep in skill.dependencies:
                cur.execute("""
                INSERT INTO skill_dependencies (skill_id, dependency_type, dependency_name, is_satisfied, details)
                VALUES (?, ?, ?, ?, ?)
                """, (skill.id, dep.dependency_type, dep.name, 1 if dep.is_satisfied else 0, dep.details))

            # Replace relationships
            cur.execute("DELETE FROM skill_relationships WHERE source_skill_id = ?", (skill.id,))
            for rel in skill.relationships:
                cur.execute("""
                INSERT INTO skill_relationships (source_skill_id, target_skill_id, relationship_type, reason)
                VALUES (?, ?, ?, ?)
                """, (skill.id, rel.target_skill_id, rel.relationship_type, rel.reason))

            # Sync FTS table
            cur.execute("DELETE FROM skill_fts WHERE skill_id = ?", (skill.id,))
            cur.execute("""
            INSERT INTO skill_fts (skill_id, name, description, category, subcategory, triggers, tags, technologies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill.id,
                skill.name,
                skill.description or "",
                skill.category or "",
                skill.subcategory or "",
                " ".join(skill.triggers),
                " ".join(skill.tags),
                " ".join(skill.technologies)
            ))

    def _row_to_skill(self, row: sqlite3.Row) -> SkillRecord:
        skill_id = row["id"]
        cur = self.conn.cursor()

        # Tags
        cur.execute("SELECT tag FROM skill_tags WHERE skill_id = ?", (skill_id,))
        tags = [r["tag"] for r in cur.fetchall()]

        # Triggers
        cur.execute("SELECT trigger FROM skill_triggers WHERE skill_id = ?", (skill_id,))
        triggers = [r["trigger"] for r in cur.fetchall()]

        # Technologies
        cur.execute("SELECT technology FROM skill_technologies WHERE skill_id = ?", (skill_id,))
        technologies = [r["technology"] for r in cur.fetchall()]

        # Dependencies
        cur.execute("SELECT dependency_type, dependency_name, is_satisfied, details FROM skill_dependencies WHERE skill_id = ?", (skill_id,))
        dependencies = [
            SkillDependency(
                dependency_type=r["dependency_type"],
                name=r["dependency_name"],
                is_satisfied=bool(r["is_satisfied"]),
                details=r["details"] or ""
            )
            for r in cur.fetchall()
        ]

        # Relationships
        cur.execute("SELECT target_skill_id, relationship_type, reason FROM skill_relationships WHERE source_skill_id = ?", (skill_id,))
        relationships = [
            SkillRelationship(
                target_skill_id=r["target_skill_id"],
                relationship_type=r["relationship_type"],
                reason=r["reason"] or ""
            )
            for r in cur.fetchall()
        ]

        raw_fm = json.loads(row["raw_frontmatter"]) if row["raw_frontmatter"] else {}
        missing_files = json.loads(row["missing_files"]) if row["missing_files"] else []
        sec_flags = json.loads(row["security_flags"]) if row["security_flags"] else []

        return SkillRecord(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            category=row["category"],
            subcategory=row["subcategory"] or "",
            source_type=SourceType(row["source_type"]),
            source_path=row["source_path"],
            relative_path=row["relative_path"] or "",
            file_hash=row["file_hash"],
            mtime=row["mtime"],
            status=SkillStatus(row["status"]),
            trust_level=TrustLevel(row["trust_level"]),
            quality_score=row["quality_score"],
            author=row["author"] or "",
            version=row["version"] or "1.0.0",
            tags=tags,
            triggers=triggers,
            technologies=technologies,
            dependencies=dependencies,
            relationships=relationships,
            missing_files=missing_files,
            security_flags=sec_flags,
            raw_frontmatter=raw_fm,
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def list_skills(
        self,
        category: Optional[str] = None,
        source_type: Optional[str] = None,
        status: Optional[str] = None,
        trust_level: Optional[str] = None,
        limit: int = 200,
        offset: int = 0
    ) -> List[SkillRecord]:
        query = "SELECT * FROM skills WHERE 1=1"
        params: List[Any] = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if source_type:
            query += " AND source_type = ?"
            params.append(source_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        if trust_level:
            query += " AND trust_level = ?"
            params.append(trust_level)

        query += " ORDER BY name ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cur = self.conn.cursor()
        cur.execute(query, params)
        return [self._row_to_skill(r) for r in cur.fetchall()]

    def search_fts(self, query: str, limit: int = 20) -> List[Tuple[SkillRecord, float]]:
        """Search skills using SQLite FTS5 BM25 match."""
        # Sanitize query for FTS5 (avoid syntax errors on special characters)
        cleaned_words = [w.strip() for w in query.replace('"', ' ').replace("'", " ").replace("*", " ").split()]
        valid_words = [w for w in cleaned_words if len(w) > 1 and w.isalnum()]
        if not valid_words:
            return []

        fts_match_expr = " OR ".join(f'"{w}"*' for w in valid_words)
        cur = self.conn.cursor()
        try:
            cur.execute("""
            SELECT skill_id, rank
            FROM skill_fts
            WHERE skill_fts MATCH ?
            ORDER BY rank
            LIMIT ?;
            """, (fts_match_expr, limit))
            results = []
            for row in cur.fetchall():
                skill = self.get_skill_by_id(row["skill_id"])
                if skill:
                    # FTS5 rank is negative (lower = better match), convert to positive score
                    score = max(0.01, 1.0 / (1.0 + abs(row["rank"])))
                    results.append((skill, score))
            return results
        except sqlite3.OperationalError:
            return []

    def get_skills_by_technology(self, tech: str) -> List[SkillRecord]:
        cur = self.conn.cursor()
        cur.execute("""
        SELECT s.* FROM skills s
        JOIN skill_technologies t ON s.id = t.skill_id
        WHERE t.technology = ? COLLATE NOCASE
        """, (tech,))
        return [self._row_to_skill(r) for r in cur.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM skills")
        total = cur.fetchone()["total"]

        cur.execute("SELECT source_type, COUNT(*) AS count FROM skills GROUP BY source_type")
        by_source = {r["source_type"]: r["count"] for r in cur.fetchall()}

        cur.execute("SELECT category, COUNT(*) AS count FROM skills GROUP BY category ORDER BY count DESC")
        by_category = {r["category"]: r["count"] for r in cur.fetchall()}

        cur.execute("SELECT status, COUNT(*) AS count FROM skills GROUP BY status")
        by_status = {r["status"]: r["count"] for r in cur.fetchall()}

        cur.execute("SELECT trust_level, COUNT(*) AS count FROM skills GROUP BY trust_level")
        by_trust = {r["trust_level"]: r["count"] for r in cur.fetchall()}

        cur.execute("SELECT value FROM indexing_metadata WHERE key = 'last_index_time'")
        last_index = cur.fetchone()

        return {
            "total_skills": total,
            "by_source": by_source,
            "by_category": by_category,
            "by_status": by_status,
            "by_trust_level": by_trust,
            "last_index_time": last_index["value"] if last_index else None
        }

    def set_metadata(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute("""
            INSERT INTO indexing_metadata (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at;
            """, (key, value, datetime.now(timezone.utc).isoformat()))

    def get_metadata(self, key: str) -> Optional[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM indexing_metadata WHERE key = ?", (key,))
        row = cur.fetchone()
        return row["value"] if row else None

    def record_feedback(self, skill_id: str, rating: int, feedback_type: str, comment: str = "", task_context: str = "") -> None:
        with self.conn:
            self.conn.execute("""
            INSERT INTO user_feedback (skill_id, rating, feedback_type, comment, task_context, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (skill_id, rating, feedback_type, comment, task_context, datetime.now(timezone.utc).isoformat()))

    def get_skill_feedback_multiplier(self, skill_id: str) -> float:
        """Returns a multiplier (default 1.0) based on historical user feedback."""
        cur = self.conn.cursor()
        cur.execute("SELECT AVG(rating) AS avg_rating, COUNT(*) AS count FROM user_feedback WHERE skill_id = ?", (skill_id,))
        row = cur.fetchone()
        if not row or row["count"] == 0 or row["avg_rating"] is None:
            return 1.0
        # Positive feedback raises score up to 1.25, negative down to 0.75
        avg_r = max(-1.0, min(1.0, row["avg_rating"]))
        return 1.0 + (avg_r * 0.25)

    def record_routing(self, task: str, project_path: str, selected_skills: List[str], confidence: float, reasoning: str) -> None:
        with self.conn:
            self.conn.execute("""
            INSERT INTO routing_history (task, project_path, selected_skills, confidence, reasoning, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (task, project_path, json.dumps(selected_skills), confidence, reasoning, datetime.now(timezone.utc).isoformat()))

    def get_project_profile(self, project_path: str) -> Optional[ProjectProfile]:
        cur = self.conn.cursor()
        cur.execute("SELECT profile_json FROM project_profiles WHERE project_path = ?", (project_path,))
        row = cur.fetchone()
        if not row:
            return None
        data = json.loads(row["profile_json"])
        return ProjectProfile(**data)

    def save_project_profile(self, profile: ProjectProfile) -> None:
        with self.conn:
            self.conn.execute("""
            INSERT INTO project_profiles (project_path, profile_json, last_analyzed_at)
            VALUES (?, ?, ?)
            ON CONFLICT(project_path) DO UPDATE SET
                profile_json = excluded.profile_json,
                last_analyzed_at = excluded.last_analyzed_at;
            """, (profile.project_path, json.dumps(profile.__dict__), datetime.now(timezone.utc).isoformat()))
