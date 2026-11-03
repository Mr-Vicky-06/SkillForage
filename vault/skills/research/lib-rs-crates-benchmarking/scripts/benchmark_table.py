#!/usr/bin/env python3
"""Library & Crate Benchmark Comparative Table Formatter."""
import sys
import json

def compare_crates(crates):
    table = []
    for c in crates:
        table.append({
            "name": c.get("name", "unknown"),
            "binary_size_kb": c.get("size_kb", 0),
            "memory_mb": c.get("memory_mb", 0),
            "speed_ops_sec": c.get("ops_sec", 0)
        })
    table.sort(key=lambda x: x["speed_ops_sec"], reverse=True)
    return {"comparative_benchmark": table}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"crates": [{"name": "serde_json", "size_kb": 120, "memory_mb": 4.2, "ops_sec": 450000}, {"name": "postcard", "size_kb": 35, "memory_mb": 1.1, "ops_sec": 1200000}]}
    res = compare_crates(payload.get("crates", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
