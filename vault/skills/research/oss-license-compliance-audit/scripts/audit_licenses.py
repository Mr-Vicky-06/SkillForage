#!/usr/bin/env python3
"""Helper script for oss-license-compliance-audit."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "oss-license-compliance-audit", "offline_capable": True}))

if __name__ == "__main__":
    main()
