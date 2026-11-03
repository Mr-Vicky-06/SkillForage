#!/usr/bin/env python3
"""SEC EDGAR 10-K Financial Ratio & Risk Extraction Utility."""
import sys
import json

def analyze_financials(filing_data):
    rev = filing_data.get("revenue", 0)
    rnd = filing_data.get("rnd_expense", 0)
    net_inc = filing_data.get("net_income", 0)
    rnd_intensity = (rnd / rev) if rev > 0 else 0
    profit_margin = (net_inc / rev) if rev > 0 else 0
    return {
        "company": filing_data.get("company", "Unknown"),
        "form": filing_data.get("form", "10-K"),
        "revenue": rev,
        "rnd_expense": rnd,
        "rnd_intensity": round(rnd_intensity, 4),
        "profit_margin": round(profit_margin, 4),
        "risk_factors_count": len(filing_data.get("risk_factors", []))
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"company": "Acme AI Corp", "form": "10-K", "revenue": 100000000, "rnd_expense": 25000000, "net_income": 15000000, "risk_factors": ["GPU shortage", "Regulatory oversight"]}
    res = analyze_financials(payload)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
