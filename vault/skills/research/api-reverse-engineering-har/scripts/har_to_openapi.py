#!/usr/bin/env python3
"""HAR Network Capture to OpenAPI 3.1 Reconstructor."""
import sys
import json

def har_to_openapi(entries):
    endpoints = {}
    for e in entries:
        req = e.get("request", {})
        method = req.get("method", "GET").lower()
        url = req.get("url", "/").split("?")[0]
        endpoints.setdefault(url, {})[method] = {
            "summary": f"Inferred {method.upper()} {url}",
            "responses": {"200": {"description": "Successful response"}}
        }
    return {
        "openapi": "3.1.0",
        "info": {"title": "Reconstructed API", "version": "1.0.0"},
        "paths": endpoints
    }

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"entries": [{"request": {"method": "POST", "url": "https://api.local/v1/auth"}}, {"request": {"method": "GET", "url": "https://api.local/v1/skills"}}]}
    res = har_to_openapi(payload.get("entries", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
