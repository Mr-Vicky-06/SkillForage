# SLIF Security, Permissions & Quarantine Architecture

**Document Version:** 1.0.0  
**Status:** Approved Specification  
**Format:** Pure Markdown (.md)  

---

### 1. The Untrusted Content Boundary

> [!CAUTION]
> Third-party skills, downloaded research papers, web pages, and API responses are **untrusted data**. They can never execute commands, modify global configurations, or override Antigravity's security rules.

---

### 2. The 8 Permission Dimensions

Every skill declares its requested permissions in `manifest.json`:

```text
+---------------------------------------------------------------+
|                    THE 8 PERMISSION DIMENSIONS                |
+-------------------------+-------------------------------------+
| 1. READ_LOCAL_FILES     | Read files within workspace root    |
| 2. WRITE_LOCAL_FILES    | Create/edit files in workspace      |
| 3. EXECUTE_SCRIPT       | Run local Python/Bash helper scripts|
| 4. ACCESS_NETWORK       | Direct outbound HTTPS requests      |
| 5. ACCESS_CREDENTIALS   | Read specified environment variable |
| 6. MODIFY_PROJECT       | Modify build/dependency files       |
| 7. INSTALL_DEPENDENCIES | Run pip/npm install in local .venv  |
| 8. EXECUTE_SYSTEM_CMD   | Run system CLI tools (git, docker)  |
+-------------------------+-------------------------------------+
```

---

### 3. Quarantine Protocol

When a skill or source exhibits suspicious characteristics:
1. **Trigger Heuristics:**
   - Prompt injection patterns (`Ignore all prior instructions`, `System prompt override`).
   - Secret exfiltration commands (`cat ~/.ssh/id_rsa`, accessing browser cookie databases).
   - Destructive filesystem commands (`rm -rf /`, `del /s /q`).
   - Encoded shell payloads (`powershell -enc`).
2. **Containment:** Status is updated to `QUARANTINED` in `registry.db`.
3. **Retrieval Exclusion:** The retrieval engine filters out quarantined skills with `WHERE status != 'quarantined'`.
4. **Audit Logging:** File hash, line number, and regex match are stored in `asset_evidence`.
