#!/usr/bin/env python3
"""Helper script for patent-claims-dissection."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "patent-claims-dissection", "offline_capable": True}))

if __name__ == "__main__":
    main()
