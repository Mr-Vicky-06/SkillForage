#!/usr/bin/env python3
"""Statistical Sample Size & Power Analysis Calculator."""
import sys
import json
import math

def calculate_sample_size(baseline_conv, mde_relative, alpha=0.05, power=0.80):
    p1 = baseline_conv
    p2 = baseline_conv * (1.0 + mde_relative)
    p_bar = (p1 + p2) / 2.0
    # Z-scores: alpha=0.05 two-tailed -> Z=1.96, power=0.80 -> Z=0.8416
    z_alpha = 1.96
    z_beta = 0.8416
    numerator = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    denominator = (p2 - p1) ** 2
    n_per_variant = math.ceil(numerator / denominator) if denominator > 0 else 0
    return {
        "baseline_conversion": baseline_conv,
        "minimum_detectable_effect_relative": mde_relative,
        "sample_size_per_variant": n_per_variant,
        "total_sample_size": n_per_variant * 2,
        "alpha": alpha,
        "power": power
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"baseline_conversion": 0.05, "mde_relative": 0.10}
    res = calculate_sample_size(payload.get("baseline_conversion", 0.05), payload.get("mde_relative", 0.10))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
