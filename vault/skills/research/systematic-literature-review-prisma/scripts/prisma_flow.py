#!/usr/bin/env python3
"""PRISMA 2020 Flow Counter and Screening Matrix Generator."""
import sys
import json

def calculate_prisma(identified, duplicates, screened_excluded, eligibility_excluded):
    screened = identified - duplicates
    eligible = screened - screened_excluded
    included = eligible - eligibility_excluded
    return {
        "identification": {"records_identified": identified, "duplicates_removed": duplicates},
        "screening": {"records_screened": screened, "records_excluded": screened_excluded},
        "eligibility": {"full_text_assessed": eligible, "full_text_excluded": eligibility_excluded},
        "included": {"studies_included_in_review": included},
        "valid_flow": (included >= 0 and eligible >= 0 and screened >= 0)
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"identified": 250, "duplicates": 40, "screened_excluded": 150, "eligibility_excluded": 35}
    res = calculate_prisma(payload.get("identified", 0), payload.get("duplicates", 0), payload.get("screened_excluded", 0), payload.get("eligibility_excluded", 0))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
