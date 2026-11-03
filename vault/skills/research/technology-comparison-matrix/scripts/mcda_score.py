#!/usr/bin/env python3
"""Multi-Criteria Decision Analysis (MCDA) Scoring Engine."""
import sys
import json

def score_mcda(options, weights):
    # weights: {"latency": 0.3, "dx": 0.2, "license": 0.2, "community": 0.3}
    ranked = []
    for opt in options:
        name = opt.get("name", "Unknown")
        scores = opt.get("scores", {})
        total = sum(scores.get(crit, 0) * w for crit, w in weights.items())
        ranked.append({"name": name, "total_score": round(total, 3), "breakdown": scores})
    ranked.sort(key=lambda x: x["total_score"], reverse=True)
    return {"ranking": ranked, "winner": ranked[0]["name"] if ranked else None}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {
        "weights": {"latency": 0.4, "dx": 0.3, "license": 0.3},
        "options": [
            {"name": "Option A (Postgres pgvector)", "scores": {"latency": 8.5, "dx": 9.0, "license": 10.0}},
            {"name": "Option B (Dedicated Vector DB)", "scores": {"latency": 9.5, "dx": 8.0, "license": 7.0}}
        ]
    }
    res = score_mcda(payload.get("options", []), payload.get("weights", {}))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
