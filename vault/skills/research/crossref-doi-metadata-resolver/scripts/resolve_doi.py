#!/usr/bin/env python3
"""Helper script for crossref-doi-metadata-resolver."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "crossref-doi-metadata-resolver", "offline_capable": False}))

if __name__ == "__main__":
    main()
