#!/usr/bin/env python3
"""Package Supply Chain Security & Scorecard Auditor."""
import sys
import json

def audit_supply_chain(deps):
    unpinned = [d for d in deps if not d.get("version") or d.get("version") in ["*", "latest"]]
    known_vulns = [d for d in deps if d.get("vulnerabilities")]
    score = max(0, 10 - (len(unpinned) * 2 + len(known_vulns) * 3))
    return {
        "dependencies_scanned": len(deps),
        "unpinned_dependencies": unpinned,
        "vulnerabilities_detected": len(known_vulns),
        "supply_chain_hygiene_score": score,
        "status": "PASS" if score >= 7 else "FAIL"
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"deps": [{"name": "fastapi", "version": "0.115.0"}, {"name": "unpinned-pkg", "version": "latest"}]}
    res = audit_supply_chain(payload.get("deps", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
