#!/usr/bin/env python3
"""Helper script for cross-source-verification."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "cross-source-verification", "offline_capable": True}))

if __name__ == "__main__":
    main()
