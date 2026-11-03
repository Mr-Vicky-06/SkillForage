#!/usr/bin/env python3
"""Fact-Checking and Ungrounded Claim Detector."""
import sys
import json

def filter_claims(generated_text, ground_truth):
    claims = [s.strip() for s in generated_text.split(".") if len(s.strip()) > 10]
    gt_lower = ground_truth.lower()
    verified = []
    unverified = []

    for c in claims:
        words = [w.lower() for w in c.split() if len(w) > 3]
        matches = [w for w in words if w in gt_lower]
        ratio = len(matches) / len(words) if words else 0
        if ratio >= 0.5:
            verified.append({"claim": c, "overlap_ratio": round(ratio, 2)})
        else:
            unverified.append({"claim": c, "overlap_ratio": round(ratio, 2), "warning": "Potential hallucination"})

    return {
        "total_claims": len(claims),
        "grounded_claims_count": len(verified),
        "hallucination_risks_count": len(unverified),
        "grounded_claims": verified,
        "potential_hallucinations": unverified
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {
        "generated_text": "Python was created by Guido van Rossum. It was released in 1845.",
        "ground_truth": "Python is a language created by Guido van Rossum and released in 1991."
    }
    res = filter_claims(payload.get("generated_text", ""), payload.get("ground_truth", ""))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
