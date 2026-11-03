#!/usr/bin/env python3
"""Helper script for ab-testing-experiment-design."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "ab-testing-experiment-design", "offline_capable": True}))

if __name__ == "__main__":
    main()
