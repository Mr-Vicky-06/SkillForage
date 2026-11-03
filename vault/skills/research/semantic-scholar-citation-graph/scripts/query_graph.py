#!/usr/bin/env python3
"""Helper script for semantic-scholar-citation-graph."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "semantic-scholar-citation-graph", "offline_capable": False}))

if __name__ == "__main__":
    main()
