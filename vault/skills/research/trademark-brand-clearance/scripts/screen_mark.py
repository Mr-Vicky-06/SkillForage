#!/usr/bin/env python3
"""Helper script for trademark-brand-clearance."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "trademark-brand-clearance", "offline_capable": False}))

if __name__ == "__main__":
    main()
