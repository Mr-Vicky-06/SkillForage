"""SQLite Database Migration and Schema Initialization for SkillForge."""

import sqlite3
from pathlib import Path


def init_database(db_path: str | Path) -> sqlite3.Connection:
    """Initialize SQLite database with required tables, indexes, and FTS5."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA cache_size = -64000;")  # 64MB cache
    conn.execute("PRAGMA temp_store = MEMORY;")
    
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS skill_sources (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            source_type TEXT NOT NULL,
            is_enabled INTEGER DEFAULT 1,
            last_scanned_at TEXT,
            skill_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            subcategory TEXT,
            source_type TEXT NOT NULL,
            source_path TEXT NOT NULL,
            relative_path TEXT,
            file_hash TEXT NOT NULL,
            mtime REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            trust_level TEXT NOT NULL DEFAULT 'reviewed',
            quality_score REAL DEFAULT 1.0,
            author TEXT,
            version TEXT DEFAULT '1.0.0',
            raw_frontmatter TEXT,
            missing_files TEXT,
            security_flags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS skill_tags (
            skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            tag TEXT NOT NULL,
            PRIMARY KEY (skill_id, tag)
        );

        CREATE TABLE IF NOT EXISTS skill_triggers (
            skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            trigger TEXT NOT NULL,
            PRIMARY KEY (skill_id, trigger)
        );

        CREATE TABLE IF NOT EXISTS skill_technologies (
            skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            technology TEXT NOT NULL,
            PRIMARY KEY (skill_id, technology)
        );

        CREATE TABLE IF NOT EXISTS skill_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            dependency_type TEXT NOT NULL,
            dependency_name TEXT NOT NULL,
            is_satisfied INTEGER DEFAULT 1,
            details TEXT
        );

        CREATE TABLE IF NOT EXISTS skill_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            target_skill_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            reason TEXT
        );

        CREATE TABLE IF NOT EXISTS project_profiles (
            project_path TEXT PRIMARY KEY,
            profile_json TEXT NOT NULL,
            last_analyzed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS routing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            project_path TEXT,
            selected_skills TEXT NOT NULL,
            confidence REAL NOT NULL,
            reasoning TEXT,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            task_context TEXT,
            rating INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            comment TEXT,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS indexing_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT NOT NULL
        );

        -- FTS5 virtual table for full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS skill_fts USING fts5(
            skill_id UNINDEXED,
            name,
            description,
            category,
            subcategory,
            triggers,
            tags,
            technologies,
            tokenize = 'unicode61'
        );

        CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
        CREATE INDEX IF NOT EXISTS idx_skills_source_type ON skills(source_type);
        CREATE INDEX IF NOT EXISTS idx_skills_status ON skills(status);
        CREATE INDEX IF NOT EXISTS idx_skills_trust ON skills(trust_level);

        -- Knowledge Fabric / Graph Tables
        CREATE TABLE IF NOT EXISTS graph_nodes (
            id TEXT PRIMARY KEY,
            node_type TEXT NOT NULL,
            name TEXT NOT NULL,
            metadata_json TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS graph_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
            target_id TEXT NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
            relationship_type TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            confidence REAL DEFAULT 1.0,
            bidirectional INTEGER DEFAULT 0,
            metadata_json TEXT
        );

        CREATE TABLE IF NOT EXISTS graph_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER REFERENCES graph_edges(id) ON DELETE CASCADE,
            evidence_type TEXT NOT NULL,
            source_snippet TEXT,
            confidence REAL DEFAULT 1.0
        );

        CREATE TABLE IF NOT EXISTS entity_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT NOT NULL,
            canonical_node_id TEXT NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
            alias_type TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_graph_nodes_type_name ON graph_nodes(node_type, name);
        CREATE INDEX IF NOT EXISTS idx_graph_edges_source_rel ON graph_edges(source_id, relationship_type);
        CREATE INDEX IF NOT EXISTS idx_graph_edges_target_rel ON graph_edges(target_id, relationship_type);
        CREATE INDEX IF NOT EXISTS idx_graph_edges_type ON graph_edges(relationship_type);
        CREATE INDEX IF NOT EXISTS idx_entity_aliases_alias ON entity_aliases(alias COLLATE NOCASE);
        """)
        
    return conn

