#!/usr/bin/env python3
"""Helper script for patent-prior-art-search."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "patent-prior-art-search", "offline_capable": False}))

if __name__ == "__main__":
    main()
