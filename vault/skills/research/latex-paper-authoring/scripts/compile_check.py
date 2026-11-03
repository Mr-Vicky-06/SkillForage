#!/usr/bin/env python3
"""Helper script for latex-paper-authoring."""
import json
import sys

def main():
    print(json.dumps({"status": "ready", "skill": "latex-paper-authoring", "offline_capable": True}))

if __name__ == "__main__":
    main()
