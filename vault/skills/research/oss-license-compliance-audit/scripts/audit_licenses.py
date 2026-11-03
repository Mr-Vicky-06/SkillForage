#!/usr/bin/env python3
"""SPDX License Compliance & Copyleft Risk Detector."""
import sys
import json

COPYLEFT_LICENSES = {"gpl-2.0", "gpl-3.0", "agpl-3.0", "lgpl-3.0", "mpl-2.0", "epl-2.0"}
PERMISSIVE_LICENSES = {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "isc", "unlicense"}

def audit_packages(packages):
    findings = []
    has_viral_copyleft = False
    for pkg in packages:
        name = pkg.get("name", "unknown")
        lic = pkg.get("license", "unknown").lower()
        if lic in COPYLEFT_LICENSES:
            risk = "HIGH_COPYLEFT" if "agpl" in lic or "gpl" in lic else "MEDIUM_WEAK_COPYLEFT"
            has_viral_copyleft = True
        elif lic in PERMISSIVE_LICENSES:
            risk = "LOW_PERMISSIVE"
        else:
            risk = "UNKNOWN_REVIEW_REQUIRED"
        findings.append({"package": name, "license": lic, "compliance_risk": risk})
    return {"has_viral_copyleft": has_viral_copyleft, "packages_audited": len(packages), "findings": findings}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"packages": [{"name": "requests", "license": "Apache-2.0"}, {"name": "sample-gpl", "license": "GPL-3.0"}]}
    res = audit_packages(payload.get("packages", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
