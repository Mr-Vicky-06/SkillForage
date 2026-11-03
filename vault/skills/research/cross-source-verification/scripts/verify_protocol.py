#!/usr/bin/env python3
"""Functional Cross-Source Fact & Citation Verification Protocol."""
import sys
import json
import re

def extract_keywords(text):
    stop = {"the", "a", "an", "is", "was", "and", "or", "in", "on", "at", "to", "for", "of", "with", "by"}
    words = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text.lower())
    return [w for w in words if w not in stop]

def verify_evidence(statement, sources):
    claim_words = set(extract_keywords(statement))
    tier1_count = 0
    tier2_count = 0
    contradictions = 0
    evidence = []

    contradiction_pats = [re.compile(r"\b(refute[sd]?|disprove[sd]?|contradict[s]?|incorrect|false)\b", re.I)]

    for s in sources:
        ref = s.get("url") or s.get("source", "unknown")
        snippet = s.get("quote") or s.get("snippet", "")
        tier = 1 if any(t in ref.lower() for t in [".gov", "doi.org", "nature.com", "ieee.org", "acm.org"]) else 2

        # Check contradiction
        is_contra = any(p.search(snippet) for p in contradiction_pats)
        # Check overlap
        snippet_words = set(extract_keywords(snippet))
        overlap = claim_words.intersection(snippet_words)
        is_support = len(overlap) >= 2 and not is_contra

        if is_contra:
            contradictions += 1
        elif is_support:
            if tier == 1:
                tier1_count += 1
            else:
                tier2_count += 1

        evidence.append({"source": ref, "tier": tier, "supports": is_support, "contradicts": is_contra, "matched_entities": list(overlap)})

    status = "disputed" if contradictions > 0 else ("verified" if (tier1_count >= 2 or (tier1_count >= 1 and tier2_count >= 2)) else "likely" if tier1_count >= 1 else "unverified")
    conf = 0.95 if status == "verified" else (0.75 if status == "likely" else 0.40)

    return {"statement": statement, "status": status, "confidence": conf, "tier1_count": tier1_count, "tier2_count": tier2_count, "contradictions": contradictions, "evidence": evidence}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"statement": "Transformer architecture introduced in 2017 Attention Is All You Need", "sources": [{"url": "https://doi.org/10.5555/3295222", "quote": "We introduce Transformer in 2017 attention mechanism."}]}
    res = verify_evidence(payload.get("statement", ""), payload.get("sources", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
