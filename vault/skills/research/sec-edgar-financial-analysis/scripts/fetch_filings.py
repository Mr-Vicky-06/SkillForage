#!/usr/bin/env python3
"""Helper script for sec-edgar-financial-analysis."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "sec-edgar-financial-analysis", "offline_capable": False}))

if __name__ == "__main__":
    main()
