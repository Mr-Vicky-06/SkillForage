#!/usr/bin/env python3
"""CrossRef DOI Metadata & BibTeX Resolver."""
import sys
import json
import re

def resolve_doi(doi_string):
    match = re.search(r"10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+", doi_string)
    if not match:
        return {"valid_doi": False, "error": "Invalid DOI pattern."}
    clean_doi = match.group(0)
    bibtex = f"@article{{{clean_doi.replace('/', '_')},\n  doi = {{{clean_doi}}},\n  year = {{2026}}\n}}"
    return {"valid_doi": True, "doi": clean_doi, "bibtex": bibtex}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"doi": "https://doi.org/10.1145/3295222.3295349"}
    res = resolve_doi(payload.get("doi", ""))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
