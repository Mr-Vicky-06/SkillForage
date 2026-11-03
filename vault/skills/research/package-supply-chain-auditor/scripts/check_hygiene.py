#!/usr/bin/env python3
"""Helper script for package-supply-chain-auditor."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "package-supply-chain-auditor", "offline_capable": False}))

if __name__ == "__main__":
    main()
