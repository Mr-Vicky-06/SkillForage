#!/usr/bin/env python3
"""Helper script for lib-rs-crates-benchmarking."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "lib-rs-crates-benchmarking", "offline_capable": True}))

if __name__ == "__main__":
    main()
