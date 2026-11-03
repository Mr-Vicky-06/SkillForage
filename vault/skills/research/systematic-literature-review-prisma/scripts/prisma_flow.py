#!/usr/bin/env python3
"""Helper script for systematic-literature-review-prisma."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "systematic-literature-review-prisma", "offline_capable": True}))

if __name__ == "__main__":
    main()
