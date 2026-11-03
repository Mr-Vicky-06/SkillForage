#!/usr/bin/env python3
"""Helper script for github-ecosystem-analyzer."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "github-ecosystem-analyzer", "offline_capable": False}))

if __name__ == "__main__":
    main()
