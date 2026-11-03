#!/usr/bin/env python3
"""Executive Whitepaper Briefing Formatter (Minto Pyramid SCQA)."""
import sys
import json

def format_scqa(situation, complication, question, answer, key_actions):
    return {
        "situation": situation,
        "complication": complication,
        "core_question": question,
        "executive_answer": answer,
        "recommended_actions": key_actions,
        "format": "Minto Pyramid Principle Executive Summary"
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {
        "situation": "SkillForge hosts 876 skills locally.",
        "complication": "Uncontrolled token leakage could permit unauthorized execution.",
        "question": "How to guarantee zero unapproved activations?",
        "answer": "Implement single-use 128-bit cryptographic tokens in APPROVED state.",
        "actions": ["Deploy TokenManager", "Enforce os isolation", "Validate manifests"]
    }
    res = format_scqa(payload.get("situation", ""), payload.get("complication", ""), payload.get("question", ""), payload.get("answer", ""), payload.get("actions", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
