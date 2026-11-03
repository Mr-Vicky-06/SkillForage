# SLIF End-to-End Data Flow Diagrams

**Document Version:** 1.0.0  
**Status:** Approved Specification  
**Format:** Pure Markdown (.md)  

---

### 1. Task Ingestion, Routing, Approval & Execution Flow

```mermaid
sequenceDiagram
    autonumber
    actor Developer
    participant IDE as Antigravity IDE
    participant Hook as PreInvocation Hook
    participant MCP as FastMCP Router (skillforge)
    participant DB as SQLite Registry (WAL)
    participant Loader as Controlled Loader
    participant Vault as Local Skill Vault

    Developer->>IDE: "Refactor database migrations with SQLite WAL mode"
    IDE->>Hook: Fire PreInvocation event (turn_index)
    Hook->>MCP: skillforge_recommend_skills(task, project_path)
    MCP->>DB: Query FTS5 + Graph CTE + LRU Cache
    DB-->>MCP: Candidate Skills: [database-migrations, clean-code]
    MCP->>DB: Mint Approval Token (Token="A1B2C3", TTL=15m)
    MCP-->>Hook: Formatted Recommendation + Token
    Hook-->>IDE: Inject Approval Prompt into turn
    IDE-->>Developer: Displays Recommended Skills & Token
    
    alt Developer Approves
        Developer->>IDE: "APPROVE SKILLFORGE A1B2C3: database-migrations"
        IDE->>MCP: skillforge_load_approved_skills(token="A1B2C3", skill_ids=["database-migrations"])
        MCP->>DB: Validate Token, Status, Expiration & Candidate IDs
        DB-->>MCP: Validated (Status -> "LOADED")
        MCP->>Loader: Fetch instructions from vault
        Loader->>Vault: Read SKILL.md & verify SHA-256
        Vault-->>Loader: File Verified
        Loader-->>MCP: Full Instructions
        MCP-->>IDE: Injects expert methodology into model context
        IDE->>Developer: Executes verified task with loaded skills
    else Developer Declines
        Developer->>IDE: "NO"
        IDE->>MCP: skillforge_decline_skills(token="A1B2C3")
        MCP->>DB: Update Status -> "DECLINED"
        IDE->>Developer: Continues with baseline capabilities (Zero skills loaded)
    end
```

---

### 2. Cross-Source Research Verification Data Flow

```mermaid
sequenceDiagram
    autonumber
    participant Agent as Antigravity Agent
    participant MCP as FastMCP (cross-verifier)
    participant Cache as Local Research Cache
    participant Remote as Outbound HTTPS (Client-Direct)

    Agent->>MCP: skillforge_cross_source_verify(claims, sources)
    MCP->>Cache: Check for cached DOI / Patent / SEC filing
    alt Cache Hit
        Cache-->>MCP: Cached Primary Evidence
    else Cache Miss & Online Mode
        MCP->>Remote: Direct client HTTPS request to Semantic Scholar / Crossref
        Remote-->>MCP: Primary Bibliographic & Citation Data
        MCP->>Cache: Store snapshot in local cache
    else Cache Miss & Strict Offline Mode
        MCP-->>Agent: Flag claim: "Unverified (Requires Online API in Strict Offline Mode)"
    end
    MCP->>MCP: Cross-compare claims & compute confidence score
    MCP-->>Agent: Verification Report (Verified, Contradictions, Limitations)
```
