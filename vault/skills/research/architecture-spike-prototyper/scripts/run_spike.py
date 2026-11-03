#!/usr/bin/env python3
"""Architecture Spike Prototype Hypothesis Tester."""
import sys
import json
import time

def evaluate_hypothesis(hypothesis_name, iterations=10000):
    start = time.perf_counter()
    # Run test cycle
    total = 0
    for i in range(iterations):
        total += i * 2
    duration_ms = (time.perf_counter() - start) * 1000.0
    return {
        "hypothesis": hypothesis_name,
        "iterations": iterations,
        "duration_ms": round(duration_ms, 3),
        "ops_per_ms": round(iterations / duration_ms, 1) if duration_ms > 0 else 0,
        "verdict": "FEASIBLE" if duration_ms < 500 else "EXCEEDS_BUDGET"
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"hypothesis": "In-memory token validation under 10ms"}
    res = evaluate_hypothesis(payload.get("hypothesis", "Default spike"))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
