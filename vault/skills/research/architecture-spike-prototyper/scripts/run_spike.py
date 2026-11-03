#!/usr/bin/env python3
"""Helper script for architecture-spike-prototyper."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "architecture-spike-prototyper", "offline_capable": True}))

if __name__ == "__main__":
    main()
