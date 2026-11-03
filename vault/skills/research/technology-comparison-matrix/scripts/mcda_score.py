#!/usr/bin/env python3
"""Helper script for technology-comparison-matrix."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "technology-comparison-matrix", "offline_capable": True}))

if __name__ == "__main__":
    main()
