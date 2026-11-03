#!/usr/bin/env python3
"""Helper script for exploratory-data-analysis-eda."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "exploratory-data-analysis-eda", "offline_capable": True}))

if __name__ == "__main__":
    main()
