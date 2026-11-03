#!/usr/bin/env python3
"""Competitive Product Teardown Matrix Builder."""
import sys
import json

def build_teardown(our_product, competitors):
    our_features = set(our_product.get("features", []))
    matrix = []
    for comp in competitors:
        c_name = comp.get("name", "Competitor")
        c_features = set(comp.get("features", []))
        matrix.append({
            "competitor": c_name,
            "parity_features": list(our_features.intersection(c_features)),
            "our_advantages": list(our_features - c_features),
            "competitor_advantages": list(c_features - our_features)
        })
    return {"our_product": our_product.get("name", "Ours"), "teardown_analysis": matrix}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"our_product": {"name": "SkillForge", "features": ["100% Local", "Cryptographic Approval", "FTS5 Search", "Sandboxed Execution"]}, "competitors": [{"name": "Cloud Hub", "features": ["Cloud Hosted", "Public Directory", "FTS5 Search"]}]}
    res = build_teardown(payload.get("our_product", {}), payload.get("competitors", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
