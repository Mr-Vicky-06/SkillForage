# SLIF Database Schema & Relational Model Specification

**Document Version:** 1.0.0  
**Status:** Approved Specification  
**Database Engine:** SQLite 3 (WAL Mode, Normal Synchronous, Foreign Keys ON)  
**Location:** `data/registry.db`  

---

### 1. Complete Relational Table Matrix

```mermaid
erDiagram
    SKILLS ||--o{ SKILL_TAGS : "tagged_with"
    SKILLS ||--o{ SKILL_TRIGGERS : "activated_by"
    SKILLS ||--o{ SKILL_DEPENDENCIES : "requires"
    SKILLS ||--o{ SKILL_RELATIONSHIPS : "relates_to"
    
    PENDING_APPROVALS ||--o{ APPROVAL_AUDIT_LOG : "audited_by"
    
    ECOSYSTEM_ASSETS ||--o{ ECOSYSTEM_COMPONENTS : "bundles"
    ECOSYSTEM_ASSETS ||--o{ MCP_CAPABILITIES : "exposes"
    ECOSYSTEM_ASSETS ||--o{ ASSET_EVIDENCE : "verified_by"

    GRAPH_NODES ||--o{ GRAPH_EDGES : "connected_to"
    GRAPH_NODES ||--o{ ENTITY_ALIASES : "aliased_by"

    SKILLS {
        string id PK
        string name
        string description
        string category
        string subcategory
        string source_type
        string source_path
        string file_hash
        real mtime
        string status
        string trust_level
        real quality_score
    }

    PENDING_APPROVALS {
        string approval_token PK
        string conversation_id
        string task_query
        string candidate_ids_json
        string status
        string created_at
        string expires_at
        string resolved_at
    }

    APPROVAL_AUDIT_LOG {
        int id PK
        string approval_token
        string action
        string skill_id
        string decision
        string timestamp
    }
```

---

### 2. DDL Schema Definition (Key Additions)

```sql
-- SLIF Approval State & Session Tracking
CREATE TABLE IF NOT EXISTS pending_approvals (
    approval_token TEXT PRIMARY KEY,
    conversation_id TEXT,
    turn_id INTEGER DEFAULT 1,
    task_query TEXT NOT NULL,
    candidate_ids_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, declined, expired, loaded
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS approval_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    approval_token TEXT NOT NULL,
    conversation_id TEXT,
    action TEXT NOT NULL, -- recommend, approve, decline, load, execute
    skill_id TEXT,
    decision TEXT NOT NULL,
    details_json TEXT,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_approvals_status ON pending_approvals(status);
CREATE INDEX IF NOT EXISTS idx_approvals_expires ON pending_approvals(expires_at);
CREATE INDEX IF NOT EXISTS idx_approval_audit_token ON approval_audit_log(approval_token);
```
