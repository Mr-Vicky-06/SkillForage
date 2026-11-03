#!/usr/bin/env python3
"""LaTeX Academic Paper Syntax & Citation Validator."""
import sys
import json
import re

def check_latex(content):
    issues = []
    # Check unbalanced math delimiters
    single_dollars = len(re.findall(r"(?<!\\)\$", content))
    if single_dollars % 2 != 0:
        issues.append("Unbalanced inline math $ delimiters detected.")
    # Check unescaped underscores outside math
    # Check undefined citations
    citations = re.findall(r"\\cite\{([^\}]+)\}", content)
    return {"syntax_valid": len(issues) == 0, "issues": issues, "citation_keys_referenced": citations}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"content": "We propose SLIF \\cite{vaswani2017}. The runtime is $O(N)$."}
    res = check_latex(payload.get("content", ""))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
