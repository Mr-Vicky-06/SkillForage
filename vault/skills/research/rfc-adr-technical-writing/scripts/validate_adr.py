#!/usr/bin/env python3
"""Helper script for rfc-adr-technical-writing."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "rfc-adr-technical-writing", "offline_capable": True}))

if __name__ == "__main__":
    main()
