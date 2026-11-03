#!/usr/bin/env python3
"""Patent Claims Dissection & Limitation Charting Tool."""
import sys
import json
import re

def dissect_claim(claim_text):
    # Standard format: [preamble], comprising: [clause 1]; [clause 2]; wherein [clause 3].
    parts = re.split(r",\s*comprising:?|;\s*", claim_text, flags=re.I)
    preamble = parts[0].strip() if parts else "Unknown"
    limitations = [p.strip() for p in parts[1:] if len(p.strip()) > 5]
    return {
        "preamble": preamble,
        "limitations_count": len(limitations),
        "limitations": [{"element_id": f"L{i+1}", "text": lim} for i, lim in enumerate(limitations)],
        "breadth_score": "BROAD" if len(limitations) <= 2 else ("MODERATE" if len(limitations) <= 4 else "NARROW")
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"claim_text": "A computer-implemented method for semantic routing, comprising: ingesting a user prompt; retrieving candidate skills from a local database; validating an approval token; and loading authorized instructions."}
    res = dissect_claim(payload.get("claim_text", ""))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
