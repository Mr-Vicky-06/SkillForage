#!/usr/bin/env python3
"""Helper script for competitive-product-teardown."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "competitive-product-teardown", "offline_capable": True}))

if __name__ == "__main__":
    main()
