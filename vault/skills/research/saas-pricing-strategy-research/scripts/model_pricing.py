#!/usr/bin/env python3
"""SaaS Pricing Strategy & Monetization Modeling Tool."""
import sys
import json

def model_pricing(tiers, user_volume):
    revenue_models = []
    for t in tiers:
        name = t.get("name", "Tier")
        base = t.get("base_price", 0)
        per_user = t.get("per_user", 0)
        usage_fee = t.get("usage_rate", 0)
        mrr = base + (per_user * user_volume) + (usage_fee * user_volume * 100)
        revenue_models.append({"tier": name, "projected_mrr": mrr, "projected_arr": mrr * 12})
    return {"modeled_user_volume": user_volume, "projections": revenue_models}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"user_volume": 50, "tiers": [{"name": "Seat-Based", "base_price": 500, "per_user": 20}, {"name": "Usage-Based", "base_price": 100, "usage_rate": 0.05}]}
    res = model_pricing(payload.get("tiers", []), payload.get("user_volume", 50))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
