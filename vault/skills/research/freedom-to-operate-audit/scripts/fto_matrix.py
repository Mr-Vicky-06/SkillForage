#!/usr/bin/env python3
"""Freedom-To-Operate (FTO) Patent Risk Evaluator."""
import sys
import json

def evaluate_fto(product_spec, patent_claims):
    # Each limitation must be mapped against product spec elements
    mapped_count = 0
    for lim in patent_claims:
        if any(term in product_spec.lower() for term in lim.lower().split() if len(term) > 4):
            mapped_count += 1
    infringement_risk = "HIGH" if mapped_count == len(patent_claims) else ("PARTIAL_DESIGN_AROUND_NEEDED" if mapped_count > 0 else "CLEAR")
    return {"total_limitations": len(patent_claims), "mapped_limitations": mapped_count, "fto_risk_level": infringement_risk}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"product_spec": "Our system executes local vector search with BM25 indexing.", "patent_claims": ["vector search", "cloud proxy server", "remote database"]}
    res = evaluate_fto(payload.get("product_spec", ""), payload.get("patent_claims", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
