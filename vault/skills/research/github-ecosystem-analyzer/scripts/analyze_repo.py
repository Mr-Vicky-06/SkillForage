#!/usr/bin/env python3
"""GitHub Open-Source Repo Velocity & Bus Factor Analyzer."""
import sys
import json

def analyze_repo_metrics(metrics):
    commits = metrics.get("monthly_commits", 0)
    authors = metrics.get("active_authors", 0)
    top_author_share = metrics.get("top_author_commit_share", 0.5)
    bus_factor = "HIGH_RISK" if top_author_share > 0.8 else ("MODERATE" if top_author_share > 0.5 else "HEALTHY")
    velocity = "HIGH" if commits > 100 else ("MODERATE" if commits > 20 else "LOW")
    return {
        "repo": metrics.get("repo", "unknown/repo"),
        "bus_factor_rating": bus_factor,
        "development_velocity": velocity,
        "active_authors": authors,
        "top_author_share": top_author_share
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"repo": "pallets/flask", "monthly_commits": 45, "active_authors": 8, "top_author_commit_share": 0.42}
    res = analyze_repo_metrics(payload)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
