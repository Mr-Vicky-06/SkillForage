#!/usr/bin/env python3
"""RFC & Architecture Decision Record (ADR) Linter."""
import sys
import json
import re

REQUIRED_SECTIONS = ["title", "status", "context", "decision", "consequences"]

def validate_adr(markdown_text):
    text_lower = markdown_text.lower()
    missing = [sec for sec in REQUIRED_SECTIONS if f"# {sec}" not in text_lower and f"## {sec}" not in text_lower]
    rfc_keywords = re.findall(r"\b(MUST|MUST NOT|REQUIRED|SHALL|SHALL NOT|SHOULD|SHOULD NOT|RECOMMENDED|MAY|OPTIONAL)\b", markdown_text)
    return {
        "is_valid_adr": len(missing) == 0,
        "missing_sections": missing,
        "rfc_2119_keywords_used": len(rfc_keywords)
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"content": "# Status\nAccepted\n# Context\nSecurity hardening\n# Decision\nWe MUST use token gating.\n# Consequences\nZero bypass."}
    res = validate_adr(payload.get("content", ""))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
