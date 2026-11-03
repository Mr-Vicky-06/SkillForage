#!/usr/bin/env python3
"""Helper script for api-reverse-engineering-har."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "api-reverse-engineering-har", "offline_capable": True}))

if __name__ == "__main__":
    main()
