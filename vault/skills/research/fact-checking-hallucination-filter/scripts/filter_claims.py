#!/usr/bin/env python3
"""Helper script for fact-checking-hallucination-filter."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "fact-checking-hallucination-filter", "offline_capable": True}))

if __name__ == "__main__":
    main()
