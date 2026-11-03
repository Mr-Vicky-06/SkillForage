#!/usr/bin/env python3
"""Automated Exploratory Data Analysis & Outlier Detector."""
import sys
import json

def run_eda(values):
    if not values:
        return {"error": "No data values provided."}
    v_sorted = sorted(values)
    n = len(v_sorted)
    mean_val = sum(v_sorted) / n
    median_val = v_sorted[n // 2]
    q1 = v_sorted[n // 4]
    q3 = v_sorted[(3 * n) // 4]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = [x for x in v_sorted if x < lower_bound or x > upper_bound]

    return {
        "count": n,
        "mean": round(mean_val, 2),
        "median": median_val,
        "iqr": round(iqr, 2),
        "outlier_count": len(outliers),
        "outliers": outliers,
        "distribution_assessment": "skewed" if len(outliers) > 0 else "symmetric"
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"values": [10, 12, 14, 15, 16, 18, 19, 105]}
    res = run_eda(payload.get("values", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
