#!/usr/bin/env python3
"""Technology Radar & Trend Matrix Categorizer."""
import sys
import json

RINGS = ["ADOPT", "TRIAL", "ASSESS", "HOLD"]

def categorize_radar(technologies):
    radar = {r: [] for r in RINGS}
    for tech in technologies:
        name = tech.get("name", "Unknown")
        ring = tech.get("ring", "ASSESS").upper()
        if ring in radar:
            radar[ring].append(name)
        else:
            radar["ASSESS"].append(name)
    return {"tech_radar": radar, "total_technologies": len(technologies)}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"technologies": [{"name": "FastMCP", "ring": "ADOPT"}, {"name": "Local SLIF", "ring": "ADOPT"}, {"name": "Legacy Central Servers", "ring": "HOLD"}]}
    res = categorize_radar(payload.get("technologies", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
